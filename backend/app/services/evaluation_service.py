from datetime import datetime, timezone
from time import perf_counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.evaluator_agent import EvaluatorAgent
from app.core.exceptions import ServiceError
from app.models.enums import QuizStatus
from app.models.knowledge_topic import KnowledgeTopic
from app.models.knowledge_document import KnowledgeDocument
from app.models.learning_task import LearningTask
from app.models.quiz_session import QuizSession
from app.prompts.evaluator_prompts import DEFAULT_EVALUATION_RUBRIC
from app.services import (
    cache_service,
    harness_service,
    quiz_service,
    reminder_service,
)
from app.services import mastery_service, memory_service


evaluator_agent = EvaluatorAgent()


def evaluate_session(db: Session, session_id: int) -> QuizSession:
    quiz_session = quiz_service.get_session(db, session_id)
    if quiz_session.status == QuizStatus.PENDING:
        raise ServiceError(
            "Quiz answers must be submitted before evaluation."
        )
    if quiz_session.status == QuizStatus.EVALUATED:
        return quiz_session

    task = db.get(LearningTask, quiz_session.task_id)
    knowledge_topic = None
    if task is not None and task.topic:
        knowledge_topic = db.scalar(
            select(KnowledgeTopic).where(
                KnowledgeTopic.topic_id == task.topic
            )
        )

    reference_points = [quiz_session.topic]
    if knowledge_topic is not None:
        reference_points.extend(knowledge_topic.key_points)
        if knowledge_topic.description:
            reference_points.append(knowledge_topic.description)
        if knowledge_topic.learning_content:
            reference_points.append(knowledge_topic.learning_content)
    elif (
        task is not None
        and task.topic
        and task.topic.startswith("rag-document:")
    ):
        try:
            document_id = int(task.topic.split(":", 1)[1])
        except ValueError:
            document_id = 0
        rag_document = db.get(KnowledgeDocument, document_id)
        if rag_document is not None:
            reference_points.append(rag_document.title)
            reference_points.append(rag_document.content)

    evaluation_traces = []
    for answer in quiz_session.answers:
        if not answer.user_answer:
            raise ServiceError(
                "Every quiz question must have a user answer."
            )
        started_at = perf_counter()
        result = evaluator_agent.evaluate(
            topic=quiz_session.topic,
            question=answer.question,
            user_answer=answer.user_answer,
            reference_points=reference_points,
            rubric=DEFAULT_EVALUATION_RUBRIC,
        )
        answer.score = result.score
        answer.is_passed = result.is_passed
        answer.concept_accuracy = result.concept_accuracy
        answer.key_points_coverage = result.key_points_coverage
        answer.engineering_understanding = (
            result.engineering_understanding
        )
        answer.clarity = result.clarity
        answer.strengths = result.strengths
        answer.weaknesses = result.weaknesses
        answer.feedback = _format_feedback(
            result.strengths,
            result.weaknesses,
        )
        answer.corrected_answer = result.corrected_answer
        answer.next_review_days = result.next_review_days
        evaluation_traces.append(
            {
                "answer": answer,
                "result": result,
                "latency_ms": (perf_counter() - started_at) * 1000,
            }
        )

    scores = [answer.score or 0.0 for answer in quiz_session.answers]
    quiz_session.total_score = round(sum(scores) / len(scores), 2)
    quiz_session.is_passed = quiz_session.total_score >= 70
    quiz_session.status = QuizStatus.EVALUATED
    quiz_session.evaluated_at = datetime.now(timezone.utc)

    all_weaknesses = list(
        dict.fromkeys(
            weakness
            for answer in quiz_session.answers
            for weakness in (answer.weaknesses or [])
        )
    )
    review_days = min(
        answer.next_review_days or 1 for answer in quiz_session.answers
    )
    pass_text = "通过" if quiz_session.is_passed else "未通过"
    weakness_summary = "；".join(all_weaknesses[:3])
    quiz_session.summary = (
        f"平均分 {quiz_session.total_score}，检测{pass_text}。"
        f"建议 {review_days} 天后复习。"
        f"主要薄弱点：{weakness_summary}"
    )

    db.commit()
    for trace in evaluation_traces:
        answer = trace["answer"]
        result = trace["result"]
        harness_service.log_event(
            event_type="answer_evaluated",
            entity_type="quiz_answer",
            entity_id=answer.id,
            input_payload={
                "quiz_session_id": quiz_session.id,
                "topic": quiz_session.topic,
                "question": answer.question,
                "answer_character_count": len(answer.user_answer or ""),
                "rubric": {
                    "concept_accuracy": 40,
                    "key_points_coverage": 30,
                    "engineering_understanding": 20,
                    "clarity": 10,
                },
            },
            output_payload={
                "score": result.score,
                "is_passed": result.is_passed,
                "strengths": result.strengths,
                "weaknesses": result.weaknesses,
                "next_review_days": result.next_review_days,
            },
            latency_ms=trace["latency_ms"],
        )
    evaluated = quiz_service.get_session(db, session_id)
    task = db.get(LearningTask, evaluated.task_id)
    topic = (
        task.topic if task is not None and task.topic else evaluated.topic
    )
    memory_service.curate_quiz_weaknesses(db, evaluated, topic)
    mastery_service.update_after_quiz(db, evaluated)
    result = quiz_service.get_session(db, session_id)
    quiz_service.refresh_session_cache(result)
    cache_service.invalidate_today_status()
    reminder_service.refresh_status(db)
    return result


def _format_feedback(
    strengths: list[str],
    weaknesses: list[str],
) -> str:
    return (
        f"优点：{'；'.join(strengths)}\n"
        f"薄弱点：{'；'.join(weaknesses)}"
    )
