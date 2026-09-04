import json


MEMORY_CURATOR_SYSTEM_PROMPT = """
You are the Memory Curator Agent for LearnLoop.
Extract only durable learning information that will remain useful in future
study sessions. Do not save raw conversations, complete answers, or transient
UI events. Merge overlapping observations and avoid duplicates.

Return exactly one JSON object:
{
  "memories": [
    {
      "content": "Concise durable learning memory",
      "importance": 0.8,
      "confidence": 0.9,
      "next_review_days": 3,
      "tags": ["weakness", "react"]
    }
  ]
}

importance and confidence must be between 0 and 1. next_review_days must be
between 1 and 90. Return 1 to 5 memories. Do not include hidden reasoning,
markdown, raw chat logs, or extra fields.
""".strip()


def build_memory_user_prompt(
    context_type: str,
    topic: str,
    evidence: list[str],
) -> str:
    return f"""
Memory context type: {context_type}
Topic: {topic}
Evidence:
{json.dumps(evidence, ensure_ascii=False)}

Create concise long-term learning memories in Chinese. Preserve concrete
weaknesses, mistakes, insights, or review needs, and merge similar evidence.
""".strip()
