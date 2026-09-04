from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.reminder import ReminderStatusRead, ReminderStatusUpdate
from app.services import reminder_service


router = APIRouter(prefix="/reminder", tags=["reminder"])


@router.get(
    "/status",
    response_model=ApiResponse[ReminderStatusRead],
)
def get_reminder_status(
    db: Session = Depends(get_db),
) -> ApiResponse[ReminderStatusRead]:
    status, cache_hit = reminder_service.get_status(db)
    return ApiResponse(
        data=status,
        message="Reminder status was retrieved.",
        cache_hit=cache_hit,
    )


@router.patch(
    "/status",
    response_model=ApiResponse[ReminderStatusRead],
)
def update_reminder_status(
    payload: ReminderStatusUpdate,
    db: Session = Depends(get_db),
) -> ApiResponse[ReminderStatusRead]:
    status = reminder_service.update_status(db, payload)
    return ApiResponse(
        data=status,
        message="Reminder status was updated.",
        cache_hit=False,
    )

