import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


class Settings(BaseModel):
    app_name: str = "LearnLoop API"
    app_version: str = "0.10.0"
    api_prefix: str = "/api"
    database_url: str = Field(
        default_factory=lambda: (
            f"sqlite:///{(BACKEND_DIR / 'learnloop.db').as_posix()}"
        )
    )
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "tauri://localhost",
        "http://tauri.localhost",
    ]

    openai_api_key: str = ""
    openai_base_url: str = "https://api.deepseek.com"
    model_name: str = "deepseek-v4-flash"
    eval_model_name: str = "deepseek-v4-flash"
    advanced_model_name: str = "deepseek-v4-pro"
    embedding_provider: str = "local"
    embedding_model_name: str = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    openai_embedding_model_name: str = "text-embedding-3-small"
    chroma_persist_dir: str = str(BACKEND_DIR / "chroma_data")
    rag_min_similarity: float = 0.25


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "LearnLoop API"),
        app_version=os.getenv("APP_VERSION", "0.10.0"),
        api_prefix=os.getenv("API_PREFIX", "/api"),
        database_url=os.getenv(
            "DATABASE_URL",
            f"sqlite:///{(BACKEND_DIR / 'learnloop.db').as_posix()}",
        ),
        redis_url=os.getenv(
            "REDIS_URL",
            "redis://localhost:6379/0",
        ),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_base_url=os.getenv(
            "OPENAI_BASE_URL", "https://api.deepseek.com"
        ),
        model_name=os.getenv("MODEL_NAME", "deepseek-v4-flash"),
        eval_model_name=os.getenv(
            "EVAL_MODEL_NAME", "deepseek-v4-flash"
        ),
        advanced_model_name=os.getenv(
            "ADVANCED_MODEL_NAME", "deepseek-v4-pro"
        ),
        embedding_provider=os.getenv("EMBEDDING_PROVIDER", "local"),
        embedding_model_name=os.getenv(
            "EMBEDDING_MODEL_NAME",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        ),
        openai_embedding_model_name=os.getenv(
            "OPENAI_EMBEDDING_MODEL_NAME",
            "text-embedding-3-small",
        ),
        chroma_persist_dir=os.getenv(
            "CHROMA_PERSIST_DIR",
            str(BACKEND_DIR / "chroma_data"),
        ),
        rag_min_similarity=float(
            os.getenv("RAG_MIN_SIMILARITY", "0.25")
        ),
    )
