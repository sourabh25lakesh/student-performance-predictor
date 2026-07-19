from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    PROJECT_NAME: str = "Student Performance Predictor"
    API_V1_PREFIX: str = ""
    ENVIRONMENT: str = "development"

    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "StrongPass@123"
    DB_NAME: str = "student_performance_db"

    # Optional: if provided, overrides the individual DB_* fields above.
    # Useful for Render/Railway which usually inject a single DATABASE_URL.
    DATABASE_URL: str | None = None

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str | URL:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return URL.create(
            drivername="mysql+pymysql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )

    # ------------------------------------------------------------------
    # JWT Authentication
    # ------------------------------------------------------------------
    JWT_SECRET_KEY: str = "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    CORS_ORIGINS: List[str] = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://student-performance-frontend-41sh.onrender.com",
]

    # ------------------------------------------------------------------
    # ML Model
    # ------------------------------------------------------------------
    MODEL_PATH: str = "app/ml/model.pkl"
    DATASET_PATH: str = "../dataset/students.csv"
    PASS_MARKS: float = 40.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance so the .env file is parsed only once."""
    return Settings()


settings = get_settings()
