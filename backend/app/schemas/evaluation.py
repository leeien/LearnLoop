from pydantic import BaseModel, Field, model_validator


class EvaluationResult(BaseModel):
    score: float = Field(ge=0, le=100)
    is_passed: bool
    concept_accuracy: float = Field(ge=0, le=40)
    key_points_coverage: float = Field(ge=0, le=30)
    engineering_understanding: float = Field(ge=0, le=20)
    clarity: float = Field(ge=0, le=10)
    strengths: list[str] = Field(min_length=1, max_length=5)
    weaknesses: list[str] = Field(min_length=1, max_length=5)
    corrected_answer: str = Field(min_length=1)
    next_review_days: int = Field(ge=1, le=30)

    @model_validator(mode="after")
    def normalize_total(self) -> "EvaluationResult":
        self.score = round(
            self.concept_accuracy
            + self.key_points_coverage
            + self.engineering_understanding
            + self.clarity,
            2,
        )
        self.is_passed = self.score >= 70
        return self

