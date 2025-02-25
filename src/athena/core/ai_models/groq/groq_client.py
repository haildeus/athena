from typing import List
from ..shared import LLMBase
from .groq_config import GroqConfig
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel


class GroqLLM(LLMBase):
    @property
    def provider_name(self) -> str:
        return "Groq"

    @property
    def agent(self) -> Agent:
        return self._agent

    def __init__(self):
        config = GroqConfig()
        super().__init__(config)

        self.model = GroqModel(
            model_name=config.model_name,
            api_key=config.api_key,
        )
        self._agent = Agent(model=self.model, name=self.provider_name)

    def embed_content(self, content: str) -> List[float]:
        pass
