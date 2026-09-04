from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceConflictError, ResourceNotFoundError
from app.models.daily_goal import DailyGoal
from app.models.enums import GoalStatus, TaskStatus
from app.schemas.goals import DailyGoalCreate, DailyGoalUpdate
from app.services import cache_service


def get_today_goal(db: Session) -> DailyGoal | None:
    return db.scalar(select(DailyGoal).where(DailyGoal.date == date.today()))


def get_goal(db: Session, goal_id: int) -> DailyGoal:
    goal = db.get(DailyGoal, goal_id)
    if goal is None:
        raise ResourceNotFoundError(f"Daily goal {goal_id} was not found.")
    return goal


def create_goal(db: Session, payload: DailyGoalCreate) -> DailyGoal:
    existing = db.scalar(select(DailyGoal).where(DailyGoal.date == payload.date))
    if existing is not None:
        raise ResourceConflictError(
            f"A daily goal already exists for {payload.date.isoformat()}."
        )

    goal = DailyGoal(**payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    cache_service.invalidate_today_status()
    return goal


def update_goal(
    db: Session,
    goal_id: int,
    payload: DailyGoalUpdate,
) -> DailyGoal:
    goal = get_goal(db, goal_id)
    changes = payload.model_dump(exclude_unset=True)

    new_date = changes.get("date")
    if new_date is not None and new_date != goal.date:
        existing = db.scalar(select(DailyGoal).where(DailyGoal.date == new_date))
        if existing is not None:
            raise ResourceConflictError(
                f"A daily goal already exists for {new_date.isoformat()}."
            )

    for field, value in changes.items():
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)
    cache_service.invalidate_today_status()
    return goal


def refresh_goal_progress(db: Session, goal: DailyGoal) -> None:
    tasks = goal.tasks
    if not tasks:
        goal.completion_rate = 0.0
        goal.status = GoalStatus.PENDING
        return

    completed = sum(task.status == TaskStatus.COMPLETED for task in tasks)
    goal.completion_rate = round(completed / len(tasks) * 100, 2)

    if completed == len(tasks):
        goal.status = GoalStatus.COMPLETED
    elif any(
        task.status != TaskStatus.PENDING or task.current_count > 0
        for task in tasks
    ):
        goal.status = GoalStatus.IN_PROGRESS
    else:
        goal.status = GoalStatus.PENDING
