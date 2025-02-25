"""
Core AI Response Schemas

Shared data models for all AI service implementations
"""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from pydantic import model_validator
from dotenv import load_dotenv

load_dotenv()


class MissingCredentialsError(Exception):
    """Raised when required credentials are missing"""

    def __init__(self, provider: str):
        super().__init__(f"Missing credentials for {provider}")
        self.provider = provider


class LLMConfig(BaseSettings):
    """Base class for LLM configuration"""

    # Required fields
    model_name: str = Field(..., min_length=1)  # Make required field
    api_key: str = Field(..., min_length=1)  # Required base field

    # Default fields
    default_token_limit: int = Field(default=1024, gt=0)
    default_max_retries: int = Field(default=3, gt=0)
    default_temperature: float = Field(default=1.0, gt=0, lt=1.5)

    class Config:
        extra = "ignore"
        env_file = ".env"

    @model_validator(mode="before")
    def validate_base_fields(cls, values):
        if not values.get("model_name"):
            raise ValueError("model_name must be provided")
        if not values.get("api_key"):
            raise MissingCredentialsError("api_key must be provided")
        return values
