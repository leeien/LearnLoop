from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.enums import MemoryType
from app.schemas.common import ApiResponse
from app.schemas.memory import (
    MemoryCreate,
    MemoryDeleteResult,
    MemoryRead,
    MemoryUpdate,
)
from app.services import memory_service


router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("", response_model=ApiResponse[list[MemoryRead]])
def list_memories(
    memory_type: MemoryType | None = Query(default=None),
    topic: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> ApiResponse[list[MemoryRead]]:
    memories = memory_service.list_memories(db, memory_type, topic)
    return ApiResponse(data=memories, message="Memories were retrieved.")


@router.post("", response_model=ApiResponse[MemoryRead], status_code=201)
def create_memory(
    payload: MemoryCreate,
    db: Session = Depends(get_db),
) -> ApiResponse[MemoryRead]:
    memory = memory_service.create_memory(db, payload)
    return ApiResponse(data=memory, message="Memory was created.")


@router.patch(
    "/{memory_id}",
    response_model=ApiResponse[MemoryRead],
)
def update_memory(
    memory_id: int,
    payload: MemoryUpdate,
    db: Session = Depends(get_db),
) -> ApiResponse[MemoryRead]:
    memory = memory_service.update_memory(db, memory_id, payload)
    return ApiResponse(data=memory, message="Memory was updated.")


@router.delete(
    "/{memory_id}",
    response_model=ApiResponse[MemoryDeleteResult],
)
def delete_memory(
    memory_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[MemoryDeleteResult]:
    deleted_id = memory_service.delete_memory(db, memory_id)
    return ApiResponse(
        data=MemoryDeleteResult(id=deleted_id),
        message="Memory was deleted.",
    )

