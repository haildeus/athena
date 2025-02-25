from typing import List
from ..shared import LLMBase
from .ollama_config import OllamaConfig
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel


class OllamaLLM(LLMBase):
    @property
    def provider_name(self) -> str:
        return "Ollama"

    @property
    def agent(self) -> Agent:
        return self._agent

    def __init__(self):
        config = OllamaConfig()
        super().__init__(config)

        self.model = OpenAIModel(
            model_name=config.model_name,
            api_key=config.api_key,
            base_url=config.base_url,
        )
        self._agent = Agent(model=self.model, name=self.provider_name)

    def embed_content(self, content: str) -> List[float]:
        pass
