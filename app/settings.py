from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "task-scheduler-prod"
    ENV: str = "dev"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/postgres"
    REDIS_URL: str = "redis://redis:6379/0"

    API_KEY: str = "change-me"  
    RATE_LIMIT_PER_MINUTE: int = 120

    WORKER_DEFAULT_TIMEOUT_S: int = 30
    WORKER_MAX_RETRIES: int = 5

settings = Settings()