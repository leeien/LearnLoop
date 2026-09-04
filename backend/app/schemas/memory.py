from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MemoryType


class MemoryCreate(BaseModel):
    memory_type: MemoryType
    topic: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    source: str = Field(default="manual", min_length=1, max_length=200)
    importance: float = Field(default=0.5, ge=0, le=1)
    confidence: float = Field(default=0.5, ge=0, le=1)
    next_review_at: datetime | None = None
    tags: list[str] = Field(default_factory=list)


class MemoryUpdate(BaseModel):
    memory_type: MemoryType | None = None
    topic: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    source: str | None = Field(default=None, min_length=1, max_length=200)
    importance: float | None = Field(default=None, ge=0, le=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    next_review_at: datetime | None = None
    tags: list[str] | None = None


class MemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    memory_type: MemoryType
    topic: str
    content: str
    source: str
    importance: float
    confidence: float
    next_review_at: datetime | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class MemoryDeleteResult(BaseModel):
    id: int


class CuratedMemoryCandidate(BaseModel):
    content: str = Field(min_length=1)
    importance: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    next_review_days: int = Field(ge=1, le=90)
    tags: list[str] = Field(default_factory=list)


class MemoryCuratorOutput(BaseModel):
    memories: list[CuratedMemoryCandidate] = Field(min_length=1, max_length=5)

