from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    database_url: str = "sqlite:///boxgrove.db"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "boxgrove"
    embedding_model: str = "text-embedding-3-small"
    intent_model: str = "gpt-6-luna"
    main_model: str = "gpt-6-luna"
    main_reasoning_effort: str = "none"
    intent_threshold: float = 0.65
    intent_floor: float = 0.3
    max_tool_rounds: int = 6
    history_turns: int = 10


settings = Settings()
