from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "RepStash"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "repstash_user"
    POSTGRES_PASSWORD: str = "repstash_password"
    POSTGRES_DB: str = "repstash"
    POSTGRES_PORT: int = 5433
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    # Security
    CLERK_SECRET_KEY: str = ""
    
    # Gemini
    GEMINI_API_KEY: str = ""
    DAILY_AI_IMPORT_LIMIT: int = 10

    # Video scraping
    MAX_VIDEO_DOWNLOAD_BYTES: int = 40 * 1024 * 1024
    MAX_VIDEO_DURATION_SECONDS: int = 240
    VIDEO_DOWNLOAD_TIMEOUT_SECONDS: float = 20.0

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

settings = Settings()
