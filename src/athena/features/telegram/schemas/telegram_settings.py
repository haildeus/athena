from pydantic import BaseModel, Field


class TelegramSettings(BaseModel):
    """
    The settings for the telegram client
    """

    BOT_DRAFT_WAITING_TIME: int = Field(
        default=1, description="The time to wait for a draft message", ge=1, le=10
    )
    BOT_DRAFT_FRESHNESS_WINDOW: int = Field(
        default=2, description="The time to wait for a fresh mention", ge=1, le=10
    )

    BOT_WELCOME_MESSAGE: str = Field(
        default="🤖 Welcome to Athena AI Assistant!\n\n"
        "Use /help to see available commands\n"
        "Press @ to access inline features",
        description="The welcome message for the bot",
    )

    MESSAGE_BATCH_SUMMARY_SIZE: int = Field(
        default=500,
        description="The number of messages to summarize at once",
        ge=1,
    )

    MESSAGE_BATCH_SUMMARY_HOURS: int = Field(
        default=24,
        description="The number of hours to summarize at once",
        ge=1,
    )
