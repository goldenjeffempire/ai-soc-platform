import time
import uuid
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from redis.asyncio import Redis

from ..core.security import AgentClaims, verify_agent_jwt
from ..core.schemas import IngestBatch
from ..core.rate_limit import enforce_rate_limit
from ..core.replay_protection import enforce_replay_protection
from ..core.metrics import INGEST_LATENCY, INGEST_REQUESTS
from ..core.kafka import KafkaProducer

router = APIRouter()
logger = logging.getLogger("ingestion.api")


def get_redis(request: Request) -> Redis:
    return request.app.state.redis


def get_kafka(request: Request) -> KafkaProducer:
    return request.app.state.kafka


@router.post("/ingest")
async def ingest(
    batch: IngestBatch,
    request: Request,
    claims: AgentClaims = Depends(verify_agent_jwt),
) -> Dict[str, Any]:
    start = time.time()
    tenant_id = claims.tenant_id
    source_id = claims.source_id

    try:
        # security controls
        redis = get_redis(request)
        await enforce_rate_limit(redis, tenant_id, source_id)
        await enforce_replay_protection(redis, tenant_id, source_id)

        # publish each event (MVP). Later: batch publish.
        kafka = get_kafka(request)
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))

        accepted = 0
        for e in batch.events:
            envelope = {
                "ingest_id": str(uuid.uuid4()),
                "tenant_id": tenant_id,
                "source_id": source_id,
                "received_at": int(time.time()),
                "event": e.model_dump(),
            }
            headers = {
                "tenant_id": tenant_id,
                "source_id": source_id,
                "request_id": request_id,
            }
            await kafka.publish_raw(envelope, headers=headers)
            accepted += 1

        INGEST_REQUESTS.labels(status="ok", tenant_id=tenant_id, source_id=source_id).inc()
        return {"status": "ok", "accepted": accepted, "tenant_id": tenant_id, "source_id": source_id}

    except HTTPException as he:
        INGEST_REQUESTS.labels(status=str(he.status_code), tenant_id=tenant_id, source_id=source_id).inc()
        raise
    except Exception as e:
        logger.exception("ingest_failed", extra={"tenant_id": tenant_id, "source_id": source_id})
        INGEST_REQUESTS.labels(status="500", tenant_id=tenant_id, source_id=source_id).inc()
        raise HTTPException(status_code=500, detail="Internal error") from e
    finally:
        INGEST_LATENCY.observe(time.time() - start)
