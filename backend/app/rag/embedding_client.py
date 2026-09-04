from functools import lru_cache
from typing import Protocol

from openai import OpenAI

from app.core.config import get_settings
from app.core.exceptions import DependencyUnavailableError


class EmbeddingClient(Protocol):
    provider_name: str

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class LocalSentenceTransformerClient:
    provider_name = "sentence-transformers"

    def __init__(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise DependencyUnavailableError(
                "Local embedding is unavailable. Install "
                "'sentence-transformers' from backend/requirements.txt."
            ) from error
        try:
            self._model = SentenceTransformer(model_name)
        except Exception as error:
            raise DependencyUnavailableError(
                f"Embedding model '{model_name}' could not be loaded: {error}"
            ) from error

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        try:
            vectors = self._model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
        except Exception as error:
            raise DependencyUnavailableError(
                f"Local embedding generation failed: {error}"
            ) from error
        return [vector.tolist() for vector in vectors]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class OpenAICompatibleEmbeddingClient:
    provider_name = "openai-compatible"

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model_name: str,
    ) -> None:
        if not api_key:
            raise DependencyUnavailableError(
                "OPENAI_API_KEY is required for the OpenAI-compatible "
                "embedding provider."
            )
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model_name = model_name

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        try:
            response = self._client.embeddings.create(
                model=self._model_name,
                input=texts,
            )
        except Exception as error:
            raise DependencyUnavailableError(
                f"Embedding API call failed: {error}"
            ) from error
        ordered = sorted(response.data, key=lambda item: item.index)
        return [item.embedding for item in ordered]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


@lru_cache
def get_embedding_client() -> EmbeddingClient:
    settings = get_settings()
    provider = settings.embedding_provider.strip().lower()
    if provider == "local":
        return LocalSentenceTransformerClient(settings.embedding_model_name)
    if provider in {"openai", "openai-compatible"}:
        return OpenAICompatibleEmbeddingClient(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model_name=settings.openai_embedding_model_name,
        )
    raise DependencyUnavailableError(
        "Unsupported EMBEDDING_PROVIDER. Use 'local' or 'openai-compatible'."
    )
