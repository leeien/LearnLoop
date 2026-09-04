from datetime import date
from time import perf_counter

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agents.reflection_agent import ReflectionAgent
from app.models.daily_goal import DailyGoal
from app.models.enums import (
    QuizStatus,
    ReviewReportType,
    TaskStatus,
)
from app.models.learning_task import LearningTask
from app.models.leetcode_record import LeetCodeRecord
from app.models.memory import Memory
from app.models.quiz_session import QuizSession
from app.models.review_report import ReviewReport
from app.models.topic_mastery import TopicMastery
from app.services import (
    cache_service,
    harness_service,
    memory_service,
    reminder_service,
)


reflection_agent = ReflectionAgent()


def generate_daily_report(db: Session) -> ReviewReport:
    started_at = perf_counter()
    today = date.today()
    existing = db.scalar(
        select(ReviewReport).where(
            ReviewReport.report_type == ReviewReportType.DAILY,
            ReviewReport.date == today,
        )
    )
    if existing is not None:
        reminder_service.refresh_status(db)
        return existing

    tasks = list(
        db.scalars(
            select(LearningTask)
            .join(DailyGoal)
            .where(DailyGoal.date == today)
            .order_by(LearningTask.id)
        )
    )
    completed_tasks = [
        task.title for task in tasks if task.status == TaskStatus.COMPLETED
    ]
    unfinished_tasks = [
        task.title for task in tasks if task.status != TaskStatus.COMPLETED
    ]

    quiz_sessions = list(
        db.scalars(
            select(QuizSession)
            .join(LearningTask)
            .join(DailyGoal)
            .where(
                DailyGoal.date == today,
                QuizSession.status == QuizStatus.EVALUATED,
            )
        )
    )
    memories = list(
        db.scalars(
            select(Memory).where(
                func.date(Memory.created_at) == today.isoformat()
            )
        )
    )
    leetcode_records = list(
        db.scalars(
            select(LeetCodeRecord).where(
                func.date(LeetCodeRecord.created_at) == today.isoformat()
            )
        )
    )
    masteries = list(db.scalars(select(TopicMastery)))

    weakness_values = list(
        dict.fromkeys(
            memory.content
            for memory in memories
            if memory.memory_type.value in (
                "weakness_memory",
                "mistake_memory",
            )
        )
    )
    context = {
        "date": today.isoformat(),
        "completed_tasks": completed_tasks,
        "unfinished_tasks": unfinished_tasks,
        "quiz_scores": [
            session.total_score
            for session in quiz_sessions
            if session.total_score is not None
        ],
        "weaknesses": weakness_values,
        "memories": [memory.content for memory in memories[:10]],
        "leetcode_records": [
            {
                "problem": record.problem_title,
                "solved": record.is_solved,
                "mistake_reason": record.mistake_reason,
                "insight": record.insight,
            }
            for record in leetcode_records
        ],
        "mastery": [
            {
                "topic": mastery.topic,
                "score": mastery.mastery_score,
            }
            for mastery in masteries
        ],
    }
    reflection = reflection_agent.generate_daily(context)
    report = ReviewReport(
        report_type=ReviewReportType.DAILY,
        date=today,
        summary=reflection.summary,
        completed_tasks=completed_tasks,
        unfinished_tasks=unfinished_tasks,
        weaknesses=reflection.weaknesses,
        insights=reflection.insights,
        next_actions=reflection.next_actions,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    harness_service.log_event(
        event_type="review_generated",
        entity_type="review",
        entity_id=report.id,
        input_payload={
            "date": today,
            "completed_task_count": len(completed_tasks),
            "unfinished_task_count": len(unfinished_tasks),
            "quiz_count": len(quiz_sessions),
            "memory_count": len(memories),
            "leetcode_record_count": len(leetcode_records),
        },
        output_payload={
            "summary": report.summary,
            "weaknesses": report.weaknesses,
            "insights": report.insights,
            "next_actions": report.next_actions,
        },
        latency_ms=(perf_counter() - started_at) * 1000,
    )

    memory_service.curate_insights(
        db=db,
        topic="daily-review",
        insights=report.insights,
        source=f"review_report:{report.id}",
        source_kind="reflection",
    )
    cache_service.invalidate_today_status()
    reminder_service.refresh_status(db)
    return report


def list_daily_reports(db: Session) -> list[ReviewReport]:
    return _list_reports(db, ReviewReportType.DAILY)


def list_weekly_reports(db: Session) -> list[ReviewReport]:
    return _list_reports(db, ReviewReportType.WEEKLY)


def _list_reports(
    db: Session,
    report_type: ReviewReportType,
) -> list[ReviewReport]:
    return list(
        db.scalars(
            select(ReviewReport)
            .where(ReviewReport.report_type == report_type)
            .order_by(ReviewReport.date.desc())
        )
    )
