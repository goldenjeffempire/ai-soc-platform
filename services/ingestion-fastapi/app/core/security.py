from dataclasses import dataclass
from typing import Any, Dict

import jwt
from fastapi import Header, HTTPException
from jwt import InvalidTokenError

from .config import settings


@dataclass(frozen=True)
class AgentClaims:
    tenant_id: str
    source_id: str
    scope: str


def verify_agent_jwt(authorization: str = Header(...)) -> AgentClaims:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1].strip()

    try:
        payload: Dict[str, Any] = jwt.decode(
            token,
            settings.ingest_jwt_secret,
            algorithms=["HS256"],
            issuer=settings.ingest_jwt_issuer,
            audience=settings.ingest_jwt_audience,
        )
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    tenant_id = str(payload.get("tenant_id", "")).strip()
    source_id = str(payload.get("source_id", "")).strip()
    scope = str(payload.get("scope", "")).strip()

    if not tenant_id or not source_id:
        raise HTTPException(status_code=401, detail="Invalid token claims")
    if scope != "agent":
        raise HTTPException(status_code=403, detail="Insufficient token scope")

    return AgentClaims(tenant_id=tenant_id, source_id=source_id, scope=scope)
