from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.dashboard import DashboardSummary
from app.services import dashboard_service


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=ApiResponse[DashboardSummary])
def get_summary(
    db: Session = Depends(get_db),
) -> ApiResponse[DashboardSummary]:
    summary, cache_hit = dashboard_service.get_summary(db)
    return ApiResponse(
        data=summary,
        message="Dashboard summary was retrieved.",
        cache_hit=cache_hit,
    )
