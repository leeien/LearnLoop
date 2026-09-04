QUIZ_SYSTEM_PROMPT = """
You are the Quiz Agent for LearnLoop.
Generate 3 to 5 concise questions that test whether a learner genuinely
understands the supplied AI Agent topic.

Use only these question_type values:
- concept
- comparison
- scenario
- pros_cons
- interview

Return one JSON object only, with this exact shape:
{
  "topic": "Readable topic title",
  "questions": [
    {
      "question": "Question text",
      "question_type": "concept"
    }
  ]
}

Do not include answers, scores, markdown fences, or extra fields.
""".strip()


def build_quiz_user_prompt(
    topic: str,
    learning_content: str,
    key_points: list[str],
) -> str:
    points = "\n".join(f"- {point}" for point in key_points) or "- No key points provided"
    return f"""
Topic: {topic}

Learning content:
{learning_content or "No learning content provided."}

Key points:
{points}

Generate a balanced quiz in Chinese. Cover conceptual understanding and at
least one practical engineering scenario.
""".strip()
