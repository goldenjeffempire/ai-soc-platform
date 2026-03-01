import time
from fastapi import Header, HTTPException
from redis.asyncio import Redis

from .config import settings


async def enforce_replay_protection(
    redis: Redis,
    tenant_id: str,
    source_id: str,
    x_nonce: str = Header(..., alias="X-Nonce"),
    x_timestamp: str = Header(..., alias="X-Timestamp"),
) -> None:
    nonce = (x_nonce or "").strip()
    if len(nonce) < 8 or len(nonce) > 128:
        raise HTTPException(status_code=400, detail="Invalid X-Nonce")

    try:
        ts = int(x_timestamp)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid X-Timestamp")

    now = int(time.time())
    if abs(now - ts) > settings.replay_window_sec:
        raise HTTPException(status_code=400, detail="Timestamp outside allowed window")

    key = f"replay:{tenant_id}:{source_id}:{nonce}"
    # SETNX: store nonce once with TTL
    ok = await redis.set(key, "1", ex=settings.replay_window_sec, nx=True)
    if not ok:
        raise HTTPException(status_code=409, detail="Replay detected")
