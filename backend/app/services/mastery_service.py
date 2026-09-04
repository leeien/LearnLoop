from datetime import datetime, timedelta, timezone
from time import perf_counter

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.enums import MemoryType, QuizStatus, TaskStatus, TaskType
from app.models.knowledge_topic import KnowledgeTopic
from app.models.learning_task import LearningTask
from app.models.memory import Memory
from app.models.quiz_session import QuizSession
from app.models.topic_mastery import TopicMastery
from app.services import harness_service


def list_masteries(db: Session) -> list[TopicMastery]:
    return list(
        db.scalars(
            select(TopicMastery).order_by(
                TopicMastery.mastery_score.desc(),
                TopicMastery.topic,
            )
        )
    )


def get_mastery(db: Session, topic: str) -> TopicMastery:
    mastery = db.scalar(
        select(TopicMastery).where(TopicMastery.topic == topic)
    )
    if mastery is None:
        raise ResourceNotFoundError(
            f"Topic mastery '{topic}' was not found."
        )
    return mastery


def update_after_quiz(
    db: Session,
    quiz_session: QuizSession,
) -> TopicMastery:
    started_at = perf_counter()
    task = db.get(LearningTask, quiz_session.task_id)
    topic = (
        task.topic if task is not None and task.topic else quiz_session.topic
    )
    knowledge_topic = db.scalar(
        select(KnowledgeTopic).where(KnowledgeTopic.topic_id == topic)
    )
    category = (
        knowledge_topic.category
        if knowledge_topic is not None
        else "uncategorized"
    )

    total_tasks = (
        db.scalar(
            select(func.count(LearningTask.id)).where(
                LearningTask.task_type == TaskType.AGENT_KNOWLEDGE,
                LearningTask.topic == topic,
            )
        )
        or 0
    )
    completed_count = (
        db.scalar(
            select(func.count(LearningTask.id)).where(
                LearningTask.task_type == TaskType.AGENT_KNOWLEDGE,
                LearningTask.topic == topic,
                LearningTask.status == TaskStatus.COMPLETED,
            )
        )
        or 0
    )
    quiz_count, average_quiz_score = db.execute(
        select(
            func.count(QuizSession.id),
            func.coalesce(func.avg(QuizSession.total_score), 0.0),
        )
        .join(LearningTask, QuizSession.task_id == LearningTask.id)
        .where(
            LearningTask.topic == topic,
            QuizSession.status == QuizStatus.EVALUATED,
        )
    ).one()

    review_count = (
        db.scalar(
            select(func.count(Memory.id)).where(
                Memory.topic == topic,
                Memory.memory_type == MemoryType.REVIEW,
            )
        )
        or 0
    )
    insight_count = (
        db.scalar(
            select(func.count(Memory.id)).where(
                Memory.topic == topic,
                Memory.memory_type == MemoryType.INSIGHT,
            )
        )
        or 0
    )

    completion_rate = (
        completed_count / total_tasks * 100 if total_tasks else 50.0
    )
    quiz_average = float(average_quiz_score) if quiz_count else 50.0
    review_score = min(100.0, 50.0 + review_count * 10)
    self_summary_score = min(100.0, 50.0 + insight_count * 10)
    mastery_score = round(
        0.3 * completion_rate
        + 0.4 * quiz_average
        + 0.2 * review_score
        + 0.1 * self_summary_score,
        2,
    )

    review_days = min(
        answer.next_review_days or 3 for answer in quiz_session.answers
    )
    now = datetime.now(timezone.utc)
    mastery = db.scalar(
        select(TopicMastery).where(TopicMastery.topic == topic)
    )
    if mastery is None:
        mastery = TopicMastery(topic=topic, category=category)
        db.add(mastery)

    mastery.category = category
    mastery.mastery_score = mastery_score
    mastery.completed_count = completed_count
    mastery.quiz_count = quiz_count
    mastery.average_quiz_score = round(float(average_quiz_score), 2)
    mastery.review_count = review_count
    mastery.last_reviewed_at = now
    mastery.next_review_at = now + timedelta(days=review_days)

    if knowledge_topic is not None:
        knowledge_topic.mastery_score = mastery_score
        knowledge_topic.next_review_at = mastery.next_review_at

    db.commit()
    db.refresh(mastery)
    harness_service.log_event(
        event_type="mastery_updated",
        entity_type="mastery",
        entity_id=mastery.id,
        input_payload={
            "topic": topic,
            "completed_count": completed_count,
            "quiz_count": quiz_count,
            "quiz_average_score": quiz_average,
            "review_count": review_count,
        },
        output_payload={
            "mastery_score": mastery.mastery_score,
            "next_review_at": mastery.next_review_at,
            "formula_weights": {
                "completion_rate": 0.3,
                "quiz_average_score": 0.4,
                "review_score": 0.2,
                "self_summary_score": 0.1,
            },
        },
        latency_ms=(perf_counter() - started_at) * 1000,
    )
    harness_service.log_event(
        event_type="review_scheduled",
        entity_type="mastery",
        entity_id=mastery.id,
        input_payload={
            "topic": topic,
            "recommended_review_days": review_days,
        },
        output_payload={
            "next_review_at": mastery.next_review_at,
        },
        latency_ms=0,
    )
    return mastery
