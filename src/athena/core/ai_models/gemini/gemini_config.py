import os

from pydantic_settings import SettingsConfigDict

from ..shared.schemas import LLMConfig


class GeminiConfig(LLMConfig):
    """Gemini-specific configuration with explicit environment binding"""

    embedding_model_name: str
    model_prefix: str = "models/"

    class Config(LLMConfig.Config):
        env_prefix = "GEMINI_"
