from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IngestEvent(BaseModel):
    # Minimal input schema: allow agent flexibility
    event_type: str = Field(..., min_length=1, max_length=64)
    severity: int = Field(5, ge=0, le=10)
    timestamp: Optional[str] = Field(None, description="ISO8601 string preferred")
    host: Optional[str] = Field(None, max_length=255)
    user: Optional[str] = Field(None, max_length=255)
    ip_src: Optional[str] = Field(None, max_length=64)
    ip_dst: Optional[str] = Field(None, max_length=64)
    port: Optional[int] = Field(None, ge=0, le=65535)
    action: Optional[str] = Field(None, max_length=128)
    message: Optional[str] = Field(None, max_length=4096)
    tags: List[str] = Field(default_factory=list, max_length=50)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    raw: Dict[str, Any] = Field(default_factory=dict)


class IngestBatch(BaseModel):
    events: List[IngestEvent] = Field(..., min_length=1, max_length=500)
