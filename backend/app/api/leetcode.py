from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.leetcode import LeetCodeRecordCreate, LeetCodeRecordRead
from app.services import leetcode_service


router = APIRouter(prefix="/leetcode", tags=["leetcode"])


@router.post(
    "/records",
    response_model=ApiResponse[LeetCodeRecordRead],
    status_code=201,
)
def create_record(
    payload: LeetCodeRecordCreate,
    db: Session = Depends(get_db),
) -> ApiResponse[LeetCodeRecordRead]:
    record = leetcode_service.create_record(db, payload)
    return ApiResponse(data=record, message="LeetCode record was created.")


@router.get(
    "/records",
    response_model=ApiResponse[list[LeetCodeRecordRead]],
)
def list_records(
    db: Session = Depends(get_db),
) -> ApiResponse[list[LeetCodeRecordRead]]:
    records = leetcode_service.list_records(db)
    return ApiResponse(data=records, message="LeetCode records were retrieved.")


@router.get(
    "/records/{record_id}",
    response_model=ApiResponse[LeetCodeRecordRead],
)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[LeetCodeRecordRead]:
    record = leetcode_service.get_record(db, record_id)
    return ApiResponse(data=record, message="LeetCode record was retrieved.")

