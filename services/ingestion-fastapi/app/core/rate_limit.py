import time
from fastapi import HTTPException
from redis.asyncio import Redis

from .config import settings


async def enforce_rate_limit(redis: Redis, tenant_id: str, source_id: str) -> None:
    limit = settings.rate_limit_per_minute
    window = int(time.time() // 60)  # minute window
    key = f"rl:{tenant_id}:{source_id}:{window}"

    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 70)  # slightly > 60 sec

    if count > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
