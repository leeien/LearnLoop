import json


GOAL_PLANNER_SYSTEM_PROMPT = """
You are LearnLoop Goal Planner. Build one realistic daily learning plan from
due memories and topic mastery. Return JSON only with title, description and
1-4 tasks. Task types are agent_knowledge, leetcode, review or reflection.
Agent knowledge tasks must use a provided topic ID. Keep the workload small.
Do not include code execution, automatic LeetCode submission or hidden
reasoning.
""".strip()


def build_goal_planner_prompt(context: dict) -> str:
    return (
        "Create today's LearnLoop learning plan from this context:\n"
        f"{json.dumps(context, ensure_ascii=False, default=str)}\n"
        "Return: {\"title\": string, \"description\": string, "
        "\"tasks\": [{\"task_type\": string, \"title\": string, "
        "\"topic\": string|null, \"target_count\": integer}]}."
    )
