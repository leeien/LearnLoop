import json


DEFAULT_EVALUATION_RUBRIC = {
    "concept_accuracy": {
        "max_score": 40,
        "description": "Core concepts are factually correct and contain no major misconception.",
    },
    "key_points_coverage": {
        "max_score": 30,
        "description": "The answer covers the supplied reference points.",
    },
    "engineering_understanding": {
        "max_score": 20,
        "description": "The answer explains practical use, boundaries, risks, or trade-offs.",
    },
    "clarity": {
        "max_score": 10,
        "description": "The answer is structured, precise, and easy to understand.",
    },
}


EVALUATOR_SYSTEM_PROMPT = """
You are the Evaluator Agent for LearnLoop.
Evaluate one learner answer using only the supplied question, reference points,
and rubric. Return auditable feedback, not hidden reasoning or chain-of-thought.

Return exactly one JSON object:
{
  "score": 82,
  "is_passed": true,
  "concept_accuracy": 35,
  "key_points_coverage": 25,
  "engineering_understanding": 15,
  "clarity": 7,
  "strengths": ["Specific strength"],
  "weaknesses": ["Specific missing or incorrect point"],
  "corrected_answer": "A concise corrected reference answer.",
  "next_review_days": 3
}

Score limits:
- concept_accuracy: 0 to 40
- key_points_coverage: 0 to 30
- engineering_understanding: 0 to 20
- clarity: 0 to 10

The total score must equal the four dimension scores. A score of 70 or above
passes. Do not output markdown, private reasoning, or extra fields.
""".strip()


def build_evaluator_user_prompt(
    topic: str,
    question: str,
    user_answer: str,
    reference_points: list[str],
    rubric: dict,
) -> str:
    return f"""
Topic: {topic}

Question:
{question}

User answer:
{user_answer}

Reference points:
{json.dumps(reference_points, ensure_ascii=False)}

Rubric:
{json.dumps(rubric, ensure_ascii=False)}

Evaluate the answer in Chinese. Keep strengths, weaknesses, and the corrected
answer concrete and concise.
""".strip()
