from typing import List
from ..shared import LLMBase
from .openrouter_config import OpenRouterConfig
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel


class OpenRouterLLM(LLMBase):
    @property
    def provider_name(self) -> str:
        return "OpenRouter"

    @property
    def agent(self) -> Agent:
        return self._agent

    def __init__(self):
        config = OpenRouterConfig()
        super().__init__(config)

        self.model = OpenAIModel(
            model_name=config.model_name,
            base_url=config.base_url,
            api_key=config.api_key,
        )
        self._agent = Agent(model=self.model, name=self.provider_name)

    def embed_content(self, content: str) -> List[float]:
        pass
