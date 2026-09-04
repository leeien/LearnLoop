from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.health import HealthData


router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse[HealthData])
def health_check(db: Session = Depends(get_db)) -> ApiResponse[HealthData]:
    db.execute(text("SELECT 1"))
    return ApiResponse(
        data=HealthData(
            status="ok",
            service="learnloop-api",
            database="connected",
        ),
        message="Service is healthy.",
    )
