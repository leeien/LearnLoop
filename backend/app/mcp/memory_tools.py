from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.database import SessionLocal
from app.models.enums import MemoryType
from app.schemas.memory import MemoryCreate, MemoryRead, MemoryUpdate
from app.services import memory_service

from .tool_registry import ToolDefinition, ToolRegistry


class ToolInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MemorySearchInput(ToolInput):
    query: str = Field(min_length=1, max_length=500)
    topic: str | None = Field(default=None, min_length=1, max_length=200)
    memory_type: MemoryType | None = None
    limit: int = Field(default=5, ge=1, le=100)


class MemoryWriteInput(ToolInput):
    memory_type: MemoryType
    topic: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    source: str = Field(min_length=1, max_length=200)
    importance: float = Field(default=0.5, ge=0, le=1)
    confidence: float = Field(default=0.5, ge=0, le=1)
    next_review_at: datetime | None = None
    tags: list[str] = Field(default_factory=list, max_length=50)


class MemoryUpdateInput(ToolInput):
    memory_id: int = Field(gt=0)
    content: str | None = Field(default=None, min_length=1)
    importance: float | None = Field(default=None, ge=0, le=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    next_review_at: datetime | None = None
    tags: list[str] | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def require_change(self) -> "MemoryUpdateInput":
        if self.model_fields_set == {"memory_id"}:
            raise ValueError("At least one memory field must be provided.")
        return self


class MemoryDueReviewsInput(ToolInput):
    date: date
    limit: int = Field(default=20, ge=1, le=100)


class MemoryDeleteInput(ToolInput):
    memory_id: int = Field(gt=0)


def register_memory_tools(registry: ToolRegistry) -> None:
    definitions = (
        ToolDefinition(
            name="memory.search",
            description=(
                "Search long-term learning memories by text with optional "
                "topic and memory type filters."
            ),
            input_schema=MemorySearchInput.model_json_schema(),
            handler=_search,
        ),
        ToolDefinition(
            name="memory.write",
            description=(
                "Create one durable learning memory through MemoryService."
            ),
            input_schema=MemoryWriteInput.model_json_schema(),
            handler=_write,
        ),
        ToolDefinition(
            name="memory.update",
            description=(
                "Update allowed fields of an existing learning memory."
            ),
            input_schema=MemoryUpdateInput.model_json_schema(),
            handler=_update,
        ),
        ToolDefinition(
            name="memory.list_due_reviews",
            description=(
                "List memories whose next review time is due by a date."
            ),
            input_schema=MemoryDueReviewsInput.model_json_schema(),
            handler=_list_due_reviews,
        ),
        ToolDefinition(
            name="memory.delete",
            description="Delete an inaccurate learning memory by ID.",
            input_schema=MemoryDeleteInput.model_json_schema(),
            handler=_delete,
        ),
    )
    for definition in definitions:
        registry.register(definition)


def _search(arguments: dict[str, Any]) -> list[dict[str, Any]]:
    payload = MemorySearchInput.model_validate(arguments)
    with SessionLocal() as db:
        memories = memory_service.search_memories(
            db,
            query=payload.query,
            topic=payload.topic,
            memory_type=payload.memory_type,
            limit=payload.limit,
        )
        return _serialize_memories(memories)


def _write(arguments: dict[str, Any]) -> dict[str, Any]:
    payload = MemoryWriteInput.model_validate(arguments)
    with SessionLocal() as db:
        memory = memory_service.create_memory(
            db,
            MemoryCreate.model_validate(payload.model_dump()),
        )
        return _serialize_memory(memory)


def _update(arguments: dict[str, Any]) -> dict[str, Any]:
    payload = MemoryUpdateInput.model_validate(arguments)
    changes = payload.model_dump(exclude={"memory_id"}, exclude_unset=True)
    with SessionLocal() as db:
        memory = memory_service.update_memory(
            db,
            payload.memory_id,
            MemoryUpdate.model_validate(changes),
        )
        return _serialize_memory(memory)


def _list_due_reviews(
    arguments: dict[str, Any],
) -> list[dict[str, Any]]:
    payload = MemoryDueReviewsInput.model_validate(arguments)
    with SessionLocal() as db:
        memories = memory_service.list_due_reviews(
            db,
            target_date=payload.date,
            limit=payload.limit,
        )
        return _serialize_memories(memories)


def _delete(arguments: dict[str, Any]) -> dict[str, Any]:
    payload = MemoryDeleteInput.model_validate(arguments)
    with SessionLocal() as db:
        deleted_id = memory_service.delete_memory(db, payload.memory_id)
        return {"id": deleted_id, "deleted": True}


def _serialize_memory(memory: Any) -> dict[str, Any]:
    return MemoryRead.model_validate(memory).model_dump(mode="json")


def _serialize_memories(memories: list[Any]) -> list[dict[str, Any]]:
    return [_serialize_memory(memory) for memory in memories]
