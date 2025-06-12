import os
from enum import Enum
from functools import lru_cache
from typing import Optional, Set

from pydantic import AnyHttpUrl, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentEnum(str, Enum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOP = "develop"
    TEST = "test"


class GlobalSettings(BaseSettings):
    PROJECT_NAME: str = "Hey Ceddy - AI Voice Golf Assistant"
    API_V1_STR: str = "/v1"

    DOCS_USERNAME: str = "docs_user"
    DOCS_PASSWORD: str = "simple_password"

    TRUSTED_HOSTS: Set[str] = {"app", "localhost", "0.0.0.0"}
    BACKEND_CORS_ORIGINS: Set[AnyHttpUrl] = set()

    ENVIRONMENT: EnvironmentEnum
    DEBUG: bool = False

    DATABASE_URL: Optional[PostgresDsn] = ""
    DB_ECHO_LOG: bool = False

    # OpenAI API settings
    OPENAI_API_KEY: Optional[
        SecretStr] = ""
    OPENAI_ASSISTANT_ID: Optional[str] = None

    # ElevenLabs API settings (optional)
    ELEVENLABS_API_KEY: Optional[SecretStr] = None
    ELEVENLABS_VOICE_ID: Optional[str] = None

    # LiveKit settings
    LIVEKIT_API_KEY: Optional[SecretStr] = ""
    LIVEKIT_API_SECRET: Optional[SecretStr] = ""
    LIVEKIT_URL: Optional[str] = ""

    # Wake word settings
    WAKE_WORD: str = "Hey Ceddy"

    @property
    def async_database_url(self) -> Optional[str]:
        return (
            str(self.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
            if self.DATABASE_URL
            else str(self.DATABASE_URL)
        )

    model_config = SettingsConfigDict(case_sensitive=True)


class TestSettings(GlobalSettings):
    DEBUG: bool = True
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.TEST


class DevelopSettings(GlobalSettings):
    DEBUG: bool = True
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.DEVELOP


class StagingSettings(GlobalSettings):
    DEBUG: bool = False
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.STAGING


class ProductionSettings(GlobalSettings):
    DEBUG: bool = False
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.PRODUCTION


class FactoryConfig:
    def __init__(self, environment: Optional[str]):
        self.environment = environment

    def __call__(self) -> GlobalSettings:
        match self.environment:
            case EnvironmentEnum.PRODUCTION:
                return ProductionSettings()
            case EnvironmentEnum.STAGING:
                return StagingSettings()
            case EnvironmentEnum.TEST:
                return TestSettings()
            case _:
                return DevelopSettings()


@lru_cache()
def get_configuration() -> GlobalSettings:
    return FactoryConfig(os.environ.get("ENVIRONMENT"))()


settings = get_configuration()
