from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LearningHarnessLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    entity_type: str
    entity_id: str
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    status: str
    latency_ms: int
    created_at: datetime


class HarnessLogFilters(BaseModel):
    event_type: str | None = None
    entity_type: str | None = None
    status: str | None = None
    limit: int = Field(default=100, ge=1, le=500)
