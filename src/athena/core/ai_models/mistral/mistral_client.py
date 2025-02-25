from typing import List
from ..shared import LLMBase
from .mistral_config import MistralConfig
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel


class MistralLLM(LLMBase):
    @property
    def provider_name(self) -> str:
        return "Mistral"

    @property
    def agent(self) -> Agent:
        return self._agent

    def __init__(self):
        config = MistralConfig()
        super().__init__(config)

        self.model = MistralModel(
            model_name=config.model_name,
            api_key=config.api_key,
        )
        self._agent = Agent(model=self.model, name=self.provider_name)

    def embed_content(self, content: str) -> List[float]:
        pass
