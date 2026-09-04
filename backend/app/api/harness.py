from fastapi import APIRouter, Query

from app.schemas.common import ApiResponse
from app.schemas.harness import LearningHarnessLogRead
from app.services import harness_service


router = APIRouter(prefix="/harness", tags=["harness"])


@router.get(
    "/logs",
    response_model=ApiResponse[list[LearningHarnessLogRead]],
)
def list_logs(
    event_type: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
) -> ApiResponse[list[LearningHarnessLogRead]]:
    logs = harness_service.list_logs(
        event_type=event_type,
        entity_type=entity_type,
        status=status,
        limit=limit,
    )
    return ApiResponse(data=logs, message="Harness logs were retrieved.")


@router.get(
    "/logs/{entity_type}/{entity_id}",
    response_model=ApiResponse[list[LearningHarnessLogRead]],
)
def list_logs_by_entity(
    entity_type: str,
    entity_id: str,
    limit: int = Query(default=100, ge=1, le=500),
) -> ApiResponse[list[LearningHarnessLogRead]]:
    logs = harness_service.list_logs_by_entity(
        entity_type,
        entity_id,
        limit=limit,
    )
    return ApiResponse(
        data=logs,
        message="Entity harness logs were retrieved.",
    )


@router.get(
    "/recent-trace",
    response_model=ApiResponse[list[LearningHarnessLogRead]],
)
def list_recent_trace(
    limit: int = Query(default=50, ge=1, le=200),
) -> ApiResponse[list[LearningHarnessLogRead]]:
    logs = harness_service.list_recent_trace(limit)
    return ApiResponse(data=logs, message="Recent trace was retrieved.")
