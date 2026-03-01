import logging
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from redis.asyncio import Redis

from .core.config import settings
from .core.logging import setup_logging
from .core.kafka import KafkaProducer
from .api.v1.ingest import router as ingest_router

logger = logging.getLogger("ingestion.app")


def create_app() -> FastAPI:
    setup_logging(settings.log_level)

    app = FastAPI(
        title="Ingestion Service",
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.on_event("startup")
    async def startup() -> None:
        app.state.redis = Redis.from_url(settings.redis_url, decode_responses=True)
        app.state.kafka = KafkaProducer()
        await app.state.kafka.start()
        logger.info("startup_complete")

    @app.on_event("shutdown")
    async def shutdown() -> None:
        await app.state.kafka.stop()
        await app.state.redis.aclose()
        logger.info("shutdown_complete")

    @app.middleware("http")
    async def limit_body_size(request: Request, call_next):
        cl = request.headers.get("content-length")
        if cl and int(cl) > settings.max_body_bytes:
            return PlainTextResponse("Payload too large", status_code=413)
        return await call_next(request)

    @app.get("/healthz")
    async def healthz():
        return {"ok": True}

    @app.get("/readyz")
    async def readyz(request: Request):
        # lightweight readiness check
        try:
            pong = await request.app.state.redis.ping()
            return {"ready": True, "redis": pong}
        except Exception:
            return PlainTextResponse("Not ready", status_code=503)

    @app.get("/metrics")
    async def metrics():
        return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)

    app.include_router(ingest_router, prefix="/api/v1", tags=["ingest"])
    return app


app = create_app()
