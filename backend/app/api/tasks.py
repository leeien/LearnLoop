from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.tasks import (
    LearningTaskCreate,
    LearningTaskRead,
    TaskCompletionResult,
)
from app.services import task_service


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/today", response_model=ApiResponse[list[LearningTaskRead]])
def list_today_tasks(
    db: Session = Depends(get_db),
) -> ApiResponse[list[LearningTaskRead]]:
    tasks = task_service.list_today_tasks(db)
    return ApiResponse(data=tasks, message="Today's tasks were retrieved.")


@router.post("", response_model=ApiResponse[LearningTaskRead], status_code=201)
def create_task(
    payload: LearningTaskCreate,
    db: Session = Depends(get_db),
) -> ApiResponse[LearningTaskRead]:
    task = task_service.create_task(db, payload)
    return ApiResponse(data=task, message="Learning task was created.")


@router.patch(
    "/{task_id}/complete",
    response_model=ApiResponse[TaskCompletionResult],
)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[TaskCompletionResult]:
    task, quiz_session_id = task_service.complete_task(db, task_id)
    return ApiResponse(
        data=TaskCompletionResult(
            task=LearningTaskRead.model_validate(task),
            quiz_session_id=quiz_session_id,
        ),
        message="Learning task was completed.",
    )


@router.patch(
    "/{task_id}/skip",
    response_model=ApiResponse[LearningTaskRead],
)
def skip_task(
    task_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[LearningTaskRead]:
    task = task_service.skip_task(db, task_id)
    return ApiResponse(data=task, message="Learning task was skipped.")
