import json


REFLECTION_SYSTEM_PROMPT = """
You are the Reflection Agent for LearnLoop.
Generate a concise daily learning review from structured facts. Distinguish
observed facts from suggestions. Do not invent completed work and do not expose
hidden reasoning.

Return exactly one JSON object:
{
  "summary": "Daily review summary",
  "weaknesses": ["Observed weakness"],
  "insights": ["Durable learning insight"],
  "next_actions": ["Concrete next action"]
}

Return JSON only, without markdown or extra fields.
""".strip()


def build_reflection_user_prompt(context: dict) -> str:
    return (
        "Generate today's review in Chinese from this structured context:\n"
        + json.dumps(context, ensure_ascii=False, default=str)
    )
