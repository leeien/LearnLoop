import logging
import re

from app.core.llm_client import call_eval_llm
from app.core.llm_json import parse_json_object
from app.core.exceptions import RateLimitExceededError
from app.prompts.evaluator_prompts import (
    DEFAULT_EVALUATION_RUBRIC,
    EVALUATOR_SYSTEM_PROMPT,
    build_evaluator_user_prompt,
)
from app.schemas.evaluation import EvaluationResult
from app.services import cache_service


logger = logging.getLogger(__name__)


class EvaluatorAgent:
    def evaluate(
        self,
        topic: str,
        question: str,
        user_answer: str,
        reference_points: list[str],
        rubric: dict | None = None,
        user_id: str = cache_service.DEFAULT_USER_ID,
    ) -> EvaluationResult:
        active_rubric = rubric or DEFAULT_EVALUATION_RUBRIC
        cached = cache_service.get_evaluation_llm(
            topic,
            question,
            user_answer,
            reference_points,
        )
        if cached is not None:
            try:
                return EvaluationResult.model_validate(cached)
            except Exception:
                pass
        try:
            cache_service.ensure_llm_allowed(user_id)
            raw_response = call_eval_llm(
                messages=[
                    {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": build_evaluator_user_prompt(
                            topic,
                            question,
                            user_answer,
                            reference_points,
                            active_rubric,
                        ),
                    },
                ],
                temperature=0.1,
                json_mode=True,
            )
            result = EvaluationResult.model_validate(
                parse_json_object(raw_response, "Evaluator")
            )
            cache_service.set_evaluation_llm(
                topic,
                question,
                user_answer,
                reference_points,
                result.model_dump(mode="json"),
            )
            return result
        except RateLimitExceededError:
            raise
        except Exception as error:
            logger.warning(
                "LLM evaluation failed; using rule-based fallback: %s",
                error,
            )
            return self._rule_based_evaluate(
                topic=topic,
                question=question,
                user_answer=user_answer,
                reference_points=reference_points,
            )

    def _rule_based_evaluate(
        self,
        topic: str,
        question: str,
        user_answer: str,
        reference_points: list[str],
    ) -> EvaluationResult:
        answer = user_answer.strip()
        compact_length = len(re.sub(r"\s+", "", answer))
        reference_terms = self._extract_reference_terms(
            topic,
            reference_points,
        )
        normalized_answer = answer.lower()
        matched_terms = [
            term for term in reference_terms if term in normalized_answer
        ]

        if compact_length < 20:
            concept_accuracy = 8
            clarity = 3
        elif compact_length < 60:
            concept_accuracy = 20
            clarity = 6
        elif compact_length < 140:
            concept_accuracy = 30
            clarity = 8
        else:
            concept_accuracy = 34
            clarity = 9

        concept_accuracy = min(
            40,
            concept_accuracy + min(6, len(matched_terms) * 2),
        )

        if reference_terms:
            coverage_ratio = min(
                1.0,
                len(matched_terms) / min(len(reference_terms), 6),
            )
            coverage_base = 3 if compact_length < 20 else 8
            coverage_range = 12 if compact_length < 20 else 22
            key_points_coverage = round(
                coverage_base + coverage_range * coverage_ratio,
                2,
            )
        else:
            key_points_coverage = min(24, max(5, compact_length / 6))

        engineering_terms = (
            "工具",
            "环境",
            "反馈",
            "流程",
            "状态",
            "边界",
            "风险",
            "场景",
            "实现",
            "tool",
            "environment",
            "feedback",
            "state",
            "risk",
            "trade-off",
            "scenario",
        )
        engineering_hits = sum(
            term in normalized_answer for term in engineering_terms
        )
        engineering_base = 3 if compact_length < 40 else 7
        engineering_understanding = min(
            20,
            engineering_base + engineering_hits * 3,
        )

        if any(mark in answer for mark in ("。", "；", ".", ";", "\n")):
            clarity = min(10, clarity + 1)

        if compact_length < 20:
            concept_accuracy = min(concept_accuracy, 12)
            key_points_coverage = min(key_points_coverage, 10)
            engineering_understanding = min(engineering_understanding, 6)

        strengths: list[str] = []
        if concept_accuracy >= 28:
            strengths.append("回答对核心概念有较准确的描述。")
        if key_points_coverage >= 20:
            strengths.append("回答覆盖了多项参考关键点。")
        if engineering_understanding >= 12:
            strengths.append("能够联系工程场景、边界或风险。")
        if not strengths:
            strengths.append("已经尝试围绕问题给出直接回答。")

        weaknesses: list[str] = []
        if concept_accuracy < 28:
            weaknesses.append("核心概念说明不够准确或完整。")
        if key_points_coverage < 20:
            missing = [
                term for term in reference_terms if term not in matched_terms
            ][:3]
            suffix = f"建议补充：{', '.join(missing)}。" if missing else ""
            weaknesses.append(f"关键点覆盖不足。{suffix}")
        if engineering_understanding < 12:
            weaknesses.append("缺少工程场景、边界条件或风险分析。")
        if clarity < 7:
            weaknesses.append("表达较短或结构不够清晰。")
        if not weaknesses:
            weaknesses.append("可进一步补充反例和适用边界。")

        reference_summary = "；".join(reference_points[:4])
        corrected_answer = (
            f"回答 {question} 时，应先准确说明 {topic} 的定义和目的，"
            f"再覆盖关键点：{reference_summary or topic}，"
            "最后结合具体工程场景说明使用方式、边界和风险。"
        )

        raw_score = (
            concept_accuracy
            + key_points_coverage
            + engineering_understanding
            + clarity
        )
        if raw_score >= 85:
            next_review_days = 7
        elif raw_score >= 70:
            next_review_days = 3
        elif raw_score >= 50:
            next_review_days = 2
        else:
            next_review_days = 1

        return EvaluationResult(
            score=raw_score,
            is_passed=raw_score >= 70,
            concept_accuracy=concept_accuracy,
            key_points_coverage=key_points_coverage,
            engineering_understanding=engineering_understanding,
            clarity=clarity,
            strengths=strengths,
            weaknesses=weaknesses,
            corrected_answer=corrected_answer,
            next_review_days=next_review_days,
        )

    @staticmethod
    def _extract_reference_terms(
        topic: str,
        reference_points: list[str],
    ) -> list[str]:
        source = [topic, *reference_points]
        terms: list[str] = []
        for item in source:
            normalized = item.strip().lower()
            if normalized and len(normalized) <= 40:
                terms.append(normalized)
            terms.extend(
                re.findall(
                    r"[a-z][a-z0-9_-]{2,}|[\u4e00-\u9fff]{2,8}",
                    normalized,
                )
            )
        return list(dict.fromkeys(term for term in terms if len(term) >= 2))
