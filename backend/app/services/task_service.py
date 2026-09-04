from datetime import date, datetime, timezone
from time import perf_counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.daily_goal import DailyGoal
from app.models.enums import TaskStatus, TaskType
from app.models.learning_task import LearningTask
from app.schemas.tasks import LearningTaskCreate
from app.services.goal_service import get_goal, refresh_goal_progress
from app.services import cache_service, harness_service, quiz_service


def list_today_tasks(db: Session) -> list[LearningTask]:
    statement = (
        select(LearningTask)
        .join(DailyGoal)
        .where(DailyGoal.date == date.today())
        .order_by(LearningTask.created_at, LearningTask.id)
    )
    return list(db.scalars(statement))


def get_task(db: Session, task_id: int) -> LearningTask:
    task = db.get(LearningTask, task_id)
    if task is None:
        raise ResourceNotFoundError(f"Learning task {task_id} was not found.")
    return task


def create_task(db: Session, payload: LearningTaskCreate) -> LearningTask:
    goal = get_goal(db, payload.goal_id)
    values = payload.model_dump()
    if payload.status == TaskStatus.COMPLETED:
        values["current_count"] = payload.target_count
        values["completed_at"] = datetime.now(timezone.utc)

    task = LearningTask(**values)
    db.add(task)
    db.flush()
    refresh_goal_progress(db, goal)
    db.commit()
    db.refresh(task)
    cache_service.invalidate_today_status()
    return task


def complete_task(db: Session, task_id: int) -> tuple[LearningTask, int | None]:
    started_at = perf_counter()
    task = get_task(db, task_id)
    previous_status = task.status.value
    task.status = TaskStatus.COMPLETED
    task.current_count = task.target_count
    task.completed_at = datetime.now(timezone.utc)
    refresh_goal_progress(db, task.goal)
    db.commit()
    db.refresh(task)
    cache_service.invalidate_today_status()
    harness_service.log_event(
        event_type="task_completed",
        entity_type="task",
        entity_id=task.id,
        input_payload={
            "task_type": task.task_type.value,
            "topic": task.topic,
            "previous_status": previous_status,
        },
        output_payload={
            "status": task.status.value,
            "current_count": task.current_count,
            "target_count": task.target_count,
        },
        latency_ms=(perf_counter() - started_at) * 1000,
    )

    quiz_session_id = None
    if task.task_type == TaskType.AGENT_KNOWLEDGE:
        quiz_session = quiz_service.generate_for_task(db, task.id)
        quiz_session_id = quiz_session.id

    return task, quiz_session_id


def skip_task(db: Session, task_id: int) -> LearningTask:
    task = get_task(db, task_id)
    task.status = TaskStatus.SKIPPED
    task.completed_at = None
    refresh_goal_progress(db, task.goal)
    db.commit()
    db.refresh(task)
    cache_service.invalidate_today_status()
    return task
