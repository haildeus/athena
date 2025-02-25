from typing import List
from ..shared import LLMBase
from .openai_config import OpenAIConfig
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel


class OpenAILLM(LLMBase):
    @property
    def provider_name(self) -> str:
        return "OpenAI"

    @property
    def agent(self) -> Agent:
        return self._agent

    def __init__(self):
        config = OpenAIConfig()
        super().__init__(config)

        self.model = OpenAIModel(
            model_name=config.model_name,
            api_key=config.api_key,
        )
        self._agent = Agent(model=self.model, name=self.provider_name)

    def embed_content(self, content: str) -> List[float]:
        pass
