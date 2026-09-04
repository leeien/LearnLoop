from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.mastery import TopicMasteryRead
from app.services import mastery_service


router = APIRouter(prefix="/mastery", tags=["mastery"])


@router.get("", response_model=ApiResponse[list[TopicMasteryRead]])
def list_masteries(
    db: Session = Depends(get_db),
) -> ApiResponse[list[TopicMasteryRead]]:
    masteries = mastery_service.list_masteries(db)
    return ApiResponse(data=masteries, message="Topic masteries were retrieved.")


@router.get(
    "/{topic}",
    response_model=ApiResponse[TopicMasteryRead],
)
def get_mastery(
    topic: str,
    db: Session = Depends(get_db),
) -> ApiResponse[TopicMasteryRead]:
    mastery = mastery_service.get_mastery(db, topic)
    return ApiResponse(data=mastery, message="Topic mastery was retrieved.")

