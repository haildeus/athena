from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import model_validator


@dataclass
class ClientData:
    user_id: Optional[int] = None
    is_premium: Optional[bool] = None
    username: Optional[str] = None
    first_name: Optional[str] = None


@dataclass
class BotClientData:
    bot_id: Optional[int] = None
    bot_username: Optional[str] = None


class TelegramConfig(BaseSettings):
    # Required fields
    API_ID: int
    API_HASH: str

    # Optional fields (can be set in .env)
    BOT_TOKEN: Optional[str]
    PHONE_NUMBER: Optional[str]

    # Non-sensitive defaults (can be overridden by .env)
    SESSION_NAME: str = "ai_assistant"
    SESSION_DIR: Path = Path(__file__).parent.parent / "sessions"
    IN_MEMORY_SESSION: bool = False
    HIDE_PASSWORD: bool = True

    APP_VERSION: str = "0.0.1"
    DEVICE_MODEL: str = "Athena"
    SYSTEM_VERSION: str = "Elysium Protocol 0.0.1"

    @model_validator(mode="before")
    def validate_auth_method(cls, values):
        if not values.get("BOT_TOKEN") and not values.get("PHONE_NUMBER"):
            raise ValueError("Either BOT_TOKEN or PHONE_NUMBER must be provided")
        return values

    class Config:
        env_file = ".env"
        env_prefix = "TELEGRAM_"
        extra = "ignore"


def load_config() -> TelegramConfig:
    return TelegramConfig()


def load_common_args():
    config = load_config()
    return {
        "api_id": config.API_ID,
        "api_hash": config.API_HASH,
        "in_memory": config.IN_MEMORY_SESSION,
        "app_version": config.APP_VERSION,
        "device_model": config.DEVICE_MODEL,
        "system_version": config.SYSTEM_VERSION,
        "workdir": str(config.SESSION_DIR),
        "hide_password": config.HIDE_PASSWORD,
    }
