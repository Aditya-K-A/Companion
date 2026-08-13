from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root: loneliness-companion/
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    # --------------------------------------------------
    # Application
    # --------------------------------------------------

    app_name: str = "Loneliness Support Companion"
    user_id: str = "demo_user"

    # --------------------------------------------------
    # LLM
    # --------------------------------------------------

    llm_provider: str = "gemini"

    gemini_api_key: str
    gemini_model: str = "gemini-3.1-flash-lite"

    # --------------------------------------------------
    # Storage
    # --------------------------------------------------

    sqlite_path: Path = PROJECT_ROOT / "data" / "companion.db"

    chroma_path: Path = PROJECT_ROOT / "chroma_db"
    chroma_collection: str = "user_memories"

    # --------------------------------------------------
    # Memory
    # --------------------------------------------------

    conversation_window: int = 8
    memory_retrieval_top_k: int = 3
    mood_history_limit: int = 8

    # --------------------------------------------------
    # Development
    # --------------------------------------------------

    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()