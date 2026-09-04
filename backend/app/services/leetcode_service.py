from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError, ServiceError
from app.models.enums import TaskType
from app.models.leetcode_record import LeetCodeRecord
from app.models.learning_task import LearningTask
from app.schemas.leetcode import LeetCodeRecordCreate
from app.services import cache_service, memory_service


def create_record(
    db: Session,
    payload: LeetCodeRecordCreate,
) -> LeetCodeRecord:
    task = db.get(LearningTask, payload.task_id)
    if task is None:
        raise ResourceNotFoundError(
            f"Learning task {payload.task_id} was not found."
        )
    if task.task_type != TaskType.LEETCODE:
        raise ServiceError(
            "LeetCode records can only be attached to a leetcode task."
        )

    record = LeetCodeRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    memory_topic = f"leetcode:{record.problem_number}"
    source = f"leetcode_record:{record.id}"
    if record.mistake_reason:
        memory_service.curate_leetcode_mistake(
            db,
            memory_topic,
            record.mistake_reason,
            source,
        )
    if record.insight:
        memory_service.curate_insights(
            db,
            memory_topic,
            [record.insight],
            source,
            "leetcode",
        )
    cache_service.invalidate_today_status()
    return record


def list_records(db: Session) -> list[LeetCodeRecord]:
    return list(
        db.scalars(
            select(LeetCodeRecord).order_by(
                LeetCodeRecord.created_at.desc(),
                LeetCodeRecord.id.desc(),
            )
        )
    )


def get_record(db: Session, record_id: int) -> LeetCodeRecord:
    record = db.get(LeetCodeRecord, record_id)
    if record is None:
        raise ResourceNotFoundError(
            f"LeetCode record {record_id} was not found."
        )
    return record
