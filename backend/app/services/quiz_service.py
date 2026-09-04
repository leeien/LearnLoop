from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from time import perf_counter

from app.agents.quiz_agent import QuizAgent
from app.core.exceptions import ResourceNotFoundError, ServiceError
from app.models.enums import QuizStatus, TaskType
from app.models.knowledge_topic import KnowledgeTopic
from app.models.learning_task import LearningTask
from app.models.quiz_answer import QuizAnswer
from app.models.quiz_session import QuizSession
from app.schemas.quiz import QuizSubmitRequest
from app.schemas.quiz import QuizSessionRead
from app.schemas.quiz import QuizAgentOutput
from app.services import cache_service, harness_service, reminder_service


quiz_agent = QuizAgent()


def _session_statement(session_id: int):
    return (
        select(QuizSession)
        .options(selectinload(QuizSession.answers))
        .where(QuizSession.id == session_id)
    )


def get_session(db: Session, session_id: int) -> QuizSession:
    quiz_session = db.scalar(_session_statement(session_id))
    if quiz_session is None:
        raise ResourceNotFoundError(
            f"Quiz session {session_id} was not found."
        )
    return quiz_session


def get_session_cached(
    db: Session,
    session_id: int,
) -> tuple[QuizSessionRead, bool]:
    cached = cache_service.get_quiz_session(session_id)
    if cached is not None:
        try:
            return QuizSessionRead.model_validate(cached), True
        except Exception:
            pass
    quiz_session = get_session(db, session_id)
    schema = _cache_session(quiz_session)
    return schema, False


def generate_for_task(db: Session, task_id: int) -> QuizSession:
    started_at = perf_counter()
    task = db.get(LearningTask, task_id)
    if task is None:
        raise ResourceNotFoundError(f"Learning task {task_id} was not found.")
    if task.task_type != TaskType.AGENT_KNOWLEDGE:
        raise ServiceError(
            "Quiz sessions can only be generated for agent_knowledge tasks."
        )

    existing = db.scalar(
        select(QuizSession)
        .options(selectinload(QuizSession.answers))
        .where(QuizSession.task_id == task_id)
    )
    if existing is not None:
        _cache_session(existing)
        reminder_service.refresh_status(db)
        return existing

    knowledge_topic = None
    if task.topic:
        knowledge_topic = db.scalar(
            select(KnowledgeTopic).where(
                KnowledgeTopic.topic_id == task.topic
            )
        )

    topic_title = (
        knowledge_topic.title
        if knowledge_topic is not None
        else (task.topic or task.title)
    )
    learning_content = (
        knowledge_topic.learning_content
        if knowledge_topic is not None
        else task.title
    )
    key_points = (
        knowledge_topic.key_points if knowledge_topic is not None else []
    )
    generated = quiz_agent.generate(
        topic=topic_title,
        learning_content=learning_content,
        key_points=key_points,
        difficulty=(
            knowledge_topic.difficulty.value
            if knowledge_topic is not None
            else "default"
        ),
    )

    return create_generated_session(
        db,
        task=task,
        generated=generated,
        input_payload={
            "task_id": task.id,
            "topic": topic_title,
            "difficulty": (
                knowledge_topic.difficulty.value
                if knowledge_topic is not None
                else "default"
            ),
            "key_point_count": len(key_points),
        },
        started_at=started_at,
    )


def create_generated_session(
    db: Session,
    *,
    task: LearningTask,
    generated: QuizAgentOutput,
    input_payload: dict,
    started_at: float | None = None,
) -> QuizSession:
    timer = started_at if started_at is not None else perf_counter()
    quiz_session = QuizSession(
        task_id=task.id,
        topic=generated.topic,
        status=QuizStatus.PENDING,
    )
    quiz_session.answers = [
        QuizAnswer(
            question=question.question,
            question_type=question.question_type,
        )
        for question in generated.questions
    ]
    db.add(quiz_session)
    db.commit()
    created = get_session(db, quiz_session.id)
    _cache_session(created)
    reminder_service.refresh_status(db)
    harness_service.log_event(
        event_type="quiz_generated",
        entity_type="quiz_session",
        entity_id=created.id,
        input_payload=input_payload,
        output_payload={
            "question_count": len(created.answers),
            "questions": [
                {
                    "id": answer.id,
                    "question": answer.question,
                    "question_type": answer.question_type.value,
                }
                for answer in created.answers
            ],
        },
        latency_ms=(perf_counter() - timer) * 1000,
    )
    return created


def submit_answers(
    db: Session,
    session_id: int,
    payload: QuizSubmitRequest,
) -> QuizSession:
    started_at = perf_counter()
    quiz_session = get_session(db, session_id)
    expected_ids = {answer.id for answer in quiz_session.answers}
    submitted_ids = [answer.answer_id for answer in payload.answers]

    if len(submitted_ids) != len(set(submitted_ids)):
        raise ServiceError("Each quiz answer can only be submitted once.")
    if set(submitted_ids) != expected_ids:
        raise ServiceError("Answers must be provided for every quiz question.")

    cleaned_answers = {
        submission.answer_id: submission.user_answer.strip()
        for submission in payload.answers
    }
    if any(not answer for answer in cleaned_answers.values()):
        raise ServiceError("Quiz answers cannot be empty.")

    answer_map = {answer.id: answer for answer in quiz_session.answers}
    for answer_id, user_answer in cleaned_answers.items():
        answer_map[answer_id].user_answer = user_answer

    quiz_session.status = QuizStatus.ANSWERED
    db.commit()
    answered = get_session(db, session_id)
    _cache_session(answered)
    reminder_service.refresh_status(db)
    harness_service.log_event(
        event_type="answer_submitted",
        entity_type="quiz_session",
        entity_id=answered.id,
        input_payload={
            "answers": [
                {
                    "answer_id": answer_id,
                    "character_count": len(user_answer),
                }
                for answer_id, user_answer in cleaned_answers.items()
            ],
        },
        output_payload={
            "status": answered.status.value,
            "answer_count": len(answered.answers),
        },
        latency_ms=(perf_counter() - started_at) * 1000,
    )
    return answered


def refresh_session_cache(quiz_session: QuizSession) -> None:
    _cache_session(quiz_session)


def _cache_session(quiz_session: QuizSession) -> QuizSessionRead:
    schema = QuizSessionRead.model_validate(quiz_session)
    cache_service.set_quiz_session(
        quiz_session.id,
        schema.model_dump(mode="json"),
    )
    return schema
