"""
Configuration centralisee de l'application.

Toutes les valeurs sensibles (secrets, credentials DB) doivent venir de
variables d'environnement / du fichier .env, jamais etre codees en dur.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "StageFlow"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "postgresql+psycopg2://stageflow:stageflow@localhost:5432/stageflow"

    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
