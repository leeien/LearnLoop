import logging

from app.core.llm_client import call_llm
from app.core.llm_json import parse_json_object
from app.core.exceptions import RateLimitExceededError
from app.prompts.memory_prompts import (
    MEMORY_CURATOR_SYSTEM_PROMPT,
    build_memory_user_prompt,
)
from app.schemas.memory import (
    CuratedMemoryCandidate,
    MemoryCuratorOutput,
)
from app.services import cache_service


logger = logging.getLogger(__name__)


class MemoryCuratorAgent:
    def curate_quiz_weaknesses(
        self,
        topic: str,
        weaknesses: list[str],
        score: float,
    ) -> MemoryCuratorOutput:
        importance = max(0.5, min(1.0, (100 - score) / 100 + 0.3))
        fallback = [
            CuratedMemoryCandidate(
                content=weakness,
                importance=importance,
                confidence=0.9,
                next_review_days=1 if score < 50 else 3,
                tags=["quiz", "weakness"],
            )
            for weakness in list(dict.fromkeys(weaknesses))[:5]
        ]
        return self._curate(
            context_type="quiz_weakness",
            topic=topic,
            evidence=weaknesses,
            fallback=fallback,
        )

    def curate_leetcode_mistake(
        self,
        topic: str,
        mistake_reason: str,
    ) -> MemoryCuratorOutput:
        return self._curate(
            context_type="leetcode_mistake",
            topic=topic,
            evidence=[mistake_reason],
            fallback=[
                CuratedMemoryCandidate(
                    content=mistake_reason,
                    importance=0.75,
                    confidence=0.95,
                    next_review_days=3,
                    tags=["leetcode", "mistake"],
                )
            ],
        )

    def curate_insights(
        self,
        topic: str,
        insights: list[str],
        source_kind: str,
    ) -> MemoryCuratorOutput:
        fallback = [
            CuratedMemoryCandidate(
                content=insight,
                importance=0.65,
                confidence=0.8,
                next_review_days=7,
                tags=[source_kind, "insight"],
            )
            for insight in list(dict.fromkeys(insights))[:5]
        ]
        return self._curate(
            context_type=f"{source_kind}_insight",
            topic=topic,
            evidence=insights,
            fallback=fallback,
        )

    def _curate(
        self,
        context_type: str,
        topic: str,
        evidence: list[str],
        fallback: list[CuratedMemoryCandidate],
        user_id: str = cache_service.DEFAULT_USER_ID,
    ) -> MemoryCuratorOutput:
        if not evidence:
            raise ValueError("Memory evidence cannot be empty.")
        try:
            cache_service.ensure_llm_allowed(user_id)
            response = call_llm(
                messages=[
                    {
                        "role": "system",
                        "content": MEMORY_CURATOR_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": build_memory_user_prompt(
                            context_type,
                            topic,
                            evidence,
                        ),
                    },
                ],
                temperature=0.1,
                json_mode=True,
            )
            return MemoryCuratorOutput.model_validate(
                parse_json_object(response, "Memory Curator")
            )
        except RateLimitExceededError:
            raise
        except Exception as error:
            logger.warning(
                "Memory curation failed; using fallback: %s",
                error,
            )
            return MemoryCuratorOutput(memories=fallback)
