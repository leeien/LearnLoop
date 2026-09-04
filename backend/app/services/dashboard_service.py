from datetime import date

from sqlalchemy import Integer, func, select
from sqlalchemy.orm import Session

from app.models.daily_goal import DailyGoal
from app.models.enums import TaskStatus
from app.models.knowledge_topic import KnowledgeTopic
from app.models.leetcode_record import LeetCodeRecord
from app.models.learning_task import LearningTask
from app.schemas.dashboard import (
    DashboardSummary,
    KnowledgeSummary,
    LeetCodeSummary,
    TaskSummary,
)
from app.services import cache_service


def get_summary(db: Session) -> tuple[DashboardSummary, bool]:
    cached = cache_service.get_today_status()
    if cached is not None:
        try:
            return DashboardSummary.model_validate(cached), True
        except Exception:
            pass

    summary = _build_summary(db)
    cache_service.set_today_status(summary.model_dump(mode="json"))
    return summary, False


def _build_summary(db: Session) -> DashboardSummary:
    goal = db.scalar(select(DailyGoal).where(DailyGoal.date == date.today()))

    task_counts = {status.value: 0 for status in TaskStatus}
    if goal is not None:
        rows = db.execute(
            select(LearningTask.status, func.count(LearningTask.id))
            .where(LearningTask.goal_id == goal.id)
            .group_by(LearningTask.status)
        )
        for status, count in rows:
            task_counts[status.value] = count

    total_topics, average_mastery = db.execute(
        select(
            func.count(KnowledgeTopic.id),
            func.coalesce(func.avg(KnowledgeTopic.mastery_score), 0.0),
        )
    ).one()

    leetcode_total, leetcode_solved, leetcode_review = db.execute(
        select(
            func.count(LeetCodeRecord.id),
            func.coalesce(
                func.sum(func.cast(LeetCodeRecord.is_solved, Integer)),
                0,
            ),
            func.coalesce(
                func.sum(func.cast(LeetCodeRecord.need_review, Integer)),
                0,
            ),
        )
    ).one()

    return DashboardSummary(
        today_goal=goal,
        tasks=TaskSummary(
            total=sum(task_counts.values()),
            pending=task_counts[TaskStatus.PENDING.value],
            completed=task_counts[TaskStatus.COMPLETED.value],
            skipped=task_counts[TaskStatus.SKIPPED.value],
        ),
        knowledge=KnowledgeSummary(
            total_topics=total_topics,
            average_mastery=round(float(average_mastery), 2),
        ),
        leetcode=LeetCodeSummary(
            total_records=leetcode_total,
            solved_records=leetcode_solved,
            need_review=leetcode_review,
        ),
    )
