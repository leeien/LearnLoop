from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.quiz import (
    QuizGenerateRequest,
    QuizSessionRead,
    QuizSubmitRequest,
)
from app.services import quiz_service
from app.services import evaluation_service


router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post(
    "/generate",
    response_model=ApiResponse[QuizSessionRead],
    status_code=201,
)
def generate_quiz(
    payload: QuizGenerateRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[QuizSessionRead]:
    quiz_session = quiz_service.generate_for_task(db, payload.task_id)
    return ApiResponse(
        data=quiz_session,
        message="Quiz session is ready.",
    )


@router.get(
    "/{session_id}",
    response_model=ApiResponse[QuizSessionRead],
)
def get_quiz(
    session_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[QuizSessionRead]:
    quiz_session, cache_hit = quiz_service.get_session_cached(db, session_id)
    return ApiResponse(
        data=quiz_session,
        message="Quiz session was retrieved.",
        cache_hit=cache_hit,
    )


@router.post(
    "/{session_id}/answer",
    response_model=ApiResponse[QuizSessionRead],
)
def submit_quiz_answers(
    session_id: int,
    payload: QuizSubmitRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[QuizSessionRead]:
    quiz_session = quiz_service.submit_answers(db, session_id, payload)
    return ApiResponse(
        data=quiz_session,
        message="Quiz answers were saved.",
    )


@router.post(
    "/{session_id}/evaluate",
    response_model=ApiResponse[QuizSessionRead],
)
def evaluate_quiz(
    session_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[QuizSessionRead]:
    quiz_session = evaluation_service.evaluate_session(db, session_id)
    return ApiResponse(
        data=quiz_session,
        message="Quiz evaluation was completed.",
    )
