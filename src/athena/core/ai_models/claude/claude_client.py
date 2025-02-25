from typing import List
from ..shared import LLMBase
from .claude_config import ClaudeConfig
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel


class ClaudeLLM(LLMBase):
    @property
    def provider_name(self) -> str:
        return "Claude"

    @property
    def agent(self) -> Agent:
        return self._agent

    def __init__(self):
        config = ClaudeConfig()
        super().__init__(config)

        self.model = AnthropicModel(
            model_name=config.model_name,
            api_key=config.api_key,
        )
        self._agent = Agent(model=self.model, name=self.provider_name)

    def embed_content(self, content: str) -> List[float]:
        pass
