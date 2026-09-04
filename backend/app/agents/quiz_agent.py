import logging

from app.core.llm_client import call_llm
from app.core.llm_json import parse_json_object
from app.core.exceptions import RateLimitExceededError
from app.models.enums import QuizQuestionType
from app.prompts.quiz_prompts import QUIZ_SYSTEM_PROMPT, build_quiz_user_prompt
from app.schemas.quiz import QuizAgentOutput, QuizQuestionDraft
from app.services import cache_service


logger = logging.getLogger(__name__)


class QuizAgent:
    def generate(
        self,
        topic: str,
        learning_content: str,
        key_points: list[str],
        difficulty: str = "default",
        user_id: str = cache_service.DEFAULT_USER_ID,
    ) -> QuizAgentOutput:
        cached = cache_service.get_quiz_llm(topic, difficulty)
        if cached is not None:
            try:
                result = QuizAgentOutput.model_validate(cached)
                return QuizAgentOutput(
                    topic=topic,
                    questions=result.questions,
                )
            except Exception:
                pass
        try:
            cache_service.ensure_llm_allowed(user_id)
            raw_response = call_llm(
                messages=[
                    {"role": "system", "content": QUIZ_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": build_quiz_user_prompt(
                            topic,
                            learning_content,
                            key_points,
                        ),
                    },
                ],
                temperature=0.2,
                json_mode=True,
            )
            payload = parse_json_object(raw_response, "Quiz Agent")
            result = QuizAgentOutput.model_validate(payload)
            normalized = QuizAgentOutput(
                topic=topic,
                questions=result.questions,
            )
            cache_service.set_quiz_llm(
                topic,
                difficulty,
                normalized.model_dump(mode="json"),
            )
            return normalized
        except RateLimitExceededError:
            raise
        except Exception as error:
            logger.warning(
                "Quiz generation failed; using fallback questions: %s",
                error,
            )
            return self.fallback(topic)

    @staticmethod
    def fallback(topic: str) -> QuizAgentOutput:
        return QuizAgentOutput(
            topic=topic,
            questions=[
                QuizQuestionDraft(
                    question=f"请用自己的话解释 {topic} 的核心概念和主要用途。",
                    question_type=QuizQuestionType.CONCEPT,
                ),
                QuizQuestionDraft(
                    question=f"请将 {topic} 与一种相近方案进行对比，并说明适用边界。",
                    question_type=QuizQuestionType.COMPARISON,
                ),
                QuizQuestionDraft(
                    question=f"在真实 AI Agent 工程中，你会如何应用 {topic}？请给出场景和步骤。",
                    question_type=QuizQuestionType.SCENARIO,
                ),
                QuizQuestionDraft(
                    question=f"分析 {topic} 的主要优点、缺点和风险。",
                    question_type=QuizQuestionType.PROS_CONS,
                ),
                QuizQuestionDraft(
                    question=f"如果面试官要求你在两分钟内介绍 {topic}，你会如何回答？",
                    question_type=QuizQuestionType.INTERVIEW,
                ),
            ],
        )
