from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.review import ReviewReportRead
from app.services import review_service


router = APIRouter(prefix="/review", tags=["review"])


@router.post(
    "/daily/generate",
    response_model=ApiResponse[ReviewReportRead],
    status_code=201,
)
def generate_daily_review(
    db: Session = Depends(get_db),
) -> ApiResponse[ReviewReportRead]:
    report = review_service.generate_daily_report(db)
    return ApiResponse(data=report, message="Daily review is ready.")


@router.get(
    "/daily",
    response_model=ApiResponse[list[ReviewReportRead]],
)
def list_daily_reviews(
    db: Session = Depends(get_db),
) -> ApiResponse[list[ReviewReportRead]]:
    reports = review_service.list_daily_reports(db)
    return ApiResponse(data=reports, message="Daily reviews were retrieved.")


@router.get(
    "/weekly",
    response_model=ApiResponse[list[ReviewReportRead]],
)
def list_weekly_reviews(
    db: Session = Depends(get_db),
) -> ApiResponse[list[ReviewReportRead]]:
    reports = review_service.list_weekly_reports(db)
    return ApiResponse(data=reports, message="Weekly reviews were retrieved.")

