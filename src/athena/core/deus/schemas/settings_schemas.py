from pydantic import BaseModel, Field

from src.athena.features.telegram.schemas.telegram_settings import TelegramSettings


class Settings(BaseModel):
    """
    The settings for the persona and the powers
    """

    streaming_response: bool = Field(
        default=True,
        description="Whether to stream the response to the user",
    )

    telegram_settings: TelegramSettings = Field(
        default_factory=TelegramSettings,
        description="The settings for the telegram client",
    )

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        return cls(**data)
