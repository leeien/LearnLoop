import logging

from app.core.llm_client import call_llm
from app.core.llm_json import parse_json_object
from app.core.exceptions import RateLimitExceededError
from app.prompts.review_prompts import (
    REFLECTION_SYSTEM_PROMPT,
    build_reflection_user_prompt,
)
from app.schemas.review import ReflectionOutput
from app.services import cache_service


logger = logging.getLogger(__name__)


class ReflectionAgent:
    def generate_daily(
        self,
        context: dict,
        user_id: str = cache_service.DEFAULT_USER_ID,
    ) -> ReflectionOutput:
        try:
            cache_service.ensure_llm_allowed(user_id)
            response = call_llm(
                messages=[
                    {
                        "role": "system",
                        "content": REFLECTION_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": build_reflection_user_prompt(context),
                    },
                ],
                temperature=0.2,
                json_mode=True,
            )
            return ReflectionOutput.model_validate(
                parse_json_object(response, "Reflection")
            )
        except RateLimitExceededError:
            raise
        except Exception as error:
            logger.warning(
                "Daily reflection failed; using template fallback: %s",
                error,
            )
            return self._fallback(context)

    @staticmethod
    def _fallback(context: dict) -> ReflectionOutput:
        completed = context.get("completed_tasks", [])
        unfinished = context.get("unfinished_tasks", [])
        weaknesses = list(dict.fromkeys(context.get("weaknesses", [])))[:5]
        scores = context.get("quiz_scores", [])
        average = round(sum(scores) / len(scores), 2) if scores else None

        summary_parts = [
            f"今日完成 {len(completed)} 项任务",
            f"仍有 {len(unfinished)} 项未完成",
        ]
        if average is not None:
            summary_parts.append(f"Quiz 平均分 {average}")

        insights = []
        if completed:
            insights.append("完成任务后及时检测有助于发现理解缺口。")
        if weaknesses:
            insights.append("当前薄弱点需要进入后续复习计划。")
        if not insights:
            insights.append("今日数据较少，应先建立稳定的学习和记录节奏。")

        next_actions = [
            f"优先复习：{weaknesses[0]}" if weaknesses else "完成一项 Agent 知识学习任务。",
        ]
        if unfinished:
            next_actions.append(f"处理未完成任务：{unfinished[0]}")

        return ReflectionOutput(
            summary="；".join(summary_parts) + "。",
            weaknesses=weaknesses,
            insights=insights,
            next_actions=next_actions,
        )
