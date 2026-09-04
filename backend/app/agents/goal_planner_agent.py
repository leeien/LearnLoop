import logging

from app.core.exceptions import RateLimitExceededError
from app.core.llm_client import call_llm
from app.core.llm_json import parse_json_object
from app.models.enums import TaskType
from app.prompts.goal_planner_prompts import (
    GOAL_PLANNER_SYSTEM_PROMPT,
    build_goal_planner_prompt,
)
from app.schemas.planning import GoalPlanOutput, PlannedTask
from app.services import cache_service


logger = logging.getLogger(__name__)


class GoalPlannerAgent:
    def generate(
        self,
        context: dict,
        user_id: str = cache_service.DEFAULT_USER_ID,
    ) -> GoalPlanOutput:
        try:
            cache_service.ensure_llm_allowed(user_id)
            response = call_llm(
                messages=[
                    {
                        "role": "system",
                        "content": GOAL_PLANNER_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": build_goal_planner_prompt(context),
                    },
                ],
                temperature=0.2,
                json_mode=True,
            )
            return GoalPlanOutput.model_validate(
                parse_json_object(response, "Goal Planner")
            )
        except RateLimitExceededError:
            raise
        except Exception as error:
            logger.warning(
                "Goal planning failed; using deterministic fallback: %s",
                error,
            )
            return self._fallback(context)

    @staticmethod
    def _fallback(context: dict) -> GoalPlanOutput:
        due_memories = context.get("due_memories", [])
        weakest_topics = context.get("weakest_topics", [])
        tasks: list[PlannedTask] = []

        if due_memories:
            memory = due_memories[0]
            tasks.append(
                PlannedTask(
                    task_type=TaskType.REVIEW,
                    title=f"复习薄弱点：{memory['topic']}",
                    topic=memory["topic"],
                )
            )

        topic = weakest_topics[0]["topic"] if weakest_topics else "react"
        tasks.append(
            PlannedTask(
                task_type=TaskType.AGENT_KNOWLEDGE,
                title=f"学习并检测 {topic}",
                topic=topic,
            )
        )
        tasks.append(
            PlannedTask(
                task_type=TaskType.LEETCODE,
                title="手动完成一道 LeetCode 并记录错因或收获",
            )
        )
        return GoalPlanOutput(
            title="完成今日 Agent 学习闭环",
            description=(
                "根据到期 Memory 和当前掌握度安排学习、检测与算法记录。"
            ),
            tasks=tasks,
        )
