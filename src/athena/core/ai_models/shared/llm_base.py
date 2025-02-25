"""
Core LLM Interface Definitions

Defines abstract base classes for all AI service implementations
"""

from abc import ABC, abstractmethod

from pydantic_ai import Agent

from .schemas import LLMConfig, MissingCredentialsError


class LLMBase(ABC):
    """Abstract base class for all LLM implementations"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._validate_credentials()

    def _validate_credentials(self):
        """Validate credentials using Pydantic validation"""
        if not self.config.api_key:
            raise MissingCredentialsError(self.provider_name)
        if not self.config.model_name:
            raise MissingCredentialsError(self.provider_name)

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name for error messages"""
        pass

    @property
    @abstractmethod
    def agent(self) -> Agent:
        """Return the agent for the LLM"""
        pass

    @abstractmethod
    def embed_content(self, content: str) -> list[float]:
        """Embed content using the LLM"""
        pass
