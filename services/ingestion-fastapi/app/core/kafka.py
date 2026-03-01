import json
import logging
from typing import Any, Dict, Optional

from aiokafka import AIOKafkaProducer

from .config import settings
from .metrics import KAFKA_PUBLISH

logger = logging.getLogger("ingestion.kafka")


class KafkaProducer:
    def __init__(self) -> None:
        self._producer: Optional[AIOKafkaProducer] = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap,
            linger_ms=10,
            acks="all",
            enable_idempotence=True,
        )
        await self._producer.start()
        logger.info("kafka producer started")

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()
            logger.info("kafka producer stopped")

    async def publish_raw(self, payload: Dict[str, Any], headers: Dict[str, str]) -> None:
        if not self._producer:
            raise RuntimeError("Kafka producer not started")

        try:
            await self._producer.send_and_wait(
                topic=settings.kafka_topic_raw,
                value=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
                headers=[(k, v.encode("utf-8")) for k, v in headers.items()],
            )
            KAFKA_PUBLISH.labels(status="ok").inc()
        except Exception:
            KAFKA_PUBLISH.labels(status="error").inc()
            raise
