import time
import pytest
from fastapi.testclient import TestClient

import jwt

from app.main import create_app
from app.core.config import settings


class DummyRedis:
    def __init__(self):
        self.kv = {}
        self.counts = {}

    async def ping(self):
        return True

    async def aclose(self):
        return True

    async def incr(self, key):
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def expire(self, key, ttl):
        return True

    async def set(self, key, val, ex=None, nx=False):
        if nx and key in self.kv:
            return False
        self.kv[key] = val
        return True


class DummyKafka:
    def __init__(self):
        self.sent = []

    async def start(self): pass
    async def stop(self): pass

    async def publish_raw(self, payload, headers):
        self.sent.append((payload, headers))


def make_token(tenant_id="t1", source_id="s1"):
    now = int(time.time())
    payload = {
        "iss": settings.ingest_jwt_issuer,
        "aud": settings.ingest_jwt_audience,
        "iat": now,
        "exp": now + 3600,
        "tenant_id": tenant_id,
        "source_id": source_id,
        "scope": "agent",
    }
    return jwt.encode(payload, settings.ingest_jwt_secret, algorithm="HS256")


@pytest.mark.asyncio
async def test_ingest_ok(monkeypatch):
    app = create_app()

    # inject dummy deps
    app.state.redis = DummyRedis()
    app.state.kafka = DummyKafka()

    client = TestClient(app)
    token = make_token()

    res = client.post(
        "/api/v1/ingest",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Nonce": "nonce-12345678",
            "X-Timestamp": str(int(time.time())),
        },
        json={"events": [{"event_type": "auth", "severity": 5, "message": "ok"}]},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["accepted"] == 1


@pytest.mark.asyncio
async def test_replay_detected(monkeypatch):
    app = create_app()
    app.state.redis = DummyRedis()
    app.state.kafka = DummyKafka()

    client = TestClient(app)
    token = make_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Nonce": "nonce-REPLAY-123456",
        "X-Timestamp": str(int(time.time())),
    }

    res1 = client.post("/api/v1/ingest", headers=headers, json={"events": [{"event_type": "auth"}]})
    assert res1.status_code == 200

    res2 = client.post("/api/v1/ingest", headers=headers, json={"events": [{"event_type": "auth"}]})
    assert res2.status_code == 409
