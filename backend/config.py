from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/todo.db"
    timezone: str = "UTC"

    anthropic_api_key: str | None = None
    ai_model_parse: str = "claude-haiku-4-5-20251001"
    ai_model_categorize: str = "claude-haiku-4-5-20251001"
    ai_model_digest: str = "claude-sonnet-5"
    ai_model_escalation: str = "claude-sonnet-5"

    google_credentials_path: str = "./credentials/google_credentials.json"
    google_token_path: str = "./credentials/google_token.json"


settings = Settings()
