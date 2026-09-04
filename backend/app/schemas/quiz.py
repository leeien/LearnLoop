from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import QuizQuestionType, QuizStatus


class QuizQuestionDraft(BaseModel):
    question: str = Field(min_length=1)
    question_type: QuizQuestionType


class QuizAgentOutput(BaseModel):
    topic: str = Field(min_length=1)
    questions: list[QuizQuestionDraft] = Field(min_length=3, max_length=5)


class QuizGenerateRequest(BaseModel):
    task_id: int = Field(gt=0)


class QuizAnswerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_session_id: int
    question: str
    question_type: QuizQuestionType
    user_answer: str | None
    score: float | None
    is_passed: bool | None
    concept_accuracy: float | None
    key_points_coverage: float | None
    engineering_understanding: float | None
    clarity: float | None
    strengths: list[str] | None
    weaknesses: list[str] | None
    feedback: str | None
    corrected_answer: str | None
    next_review_days: int | None
    created_at: datetime


class QuizSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    topic: str
    status: QuizStatus
    total_score: float | None
    is_passed: bool | None
    summary: str | None
    created_at: datetime
    evaluated_at: datetime | None
    answers: list[QuizAnswerRead]


class QuizAnswerSubmission(BaseModel):
    answer_id: int = Field(gt=0)
    user_answer: str = Field(min_length=1)


class QuizSubmitRequest(BaseModel):
    answers: list[QuizAnswerSubmission] = Field(min_length=1)
