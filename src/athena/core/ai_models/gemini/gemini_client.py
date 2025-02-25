from typing import List

import google.generativeai as genai
from google.generativeai.embedding import EmbeddingTaskType

from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

from src.athena.core.ai_models.shared import LLMBase
from src.athena.core.ai_models.gemini.gemini_config import GeminiConfig


class GeminiLLM(LLMBase):
    @property
    def provider_name(self) -> str:
        return "Gemini"

    @property
    def agent(self) -> Agent:
        return self._agent

    def __init__(self):
        config = GeminiConfig()
        super().__init__(config)
        print(config)

        self.model = GeminiModel(
            model_name=config.model_name,
            api_key=config.api_key,
        )
        self._agent = Agent(model=self.model, name=self.provider_name)
        self.embedding_model = f"{config.model_prefix}{config.embedding_model_name}"

        genai.configure(api_key=config.api_key)

    def embed_content(
        self, content: str, task_type: EmbeddingTaskType | str = None
    ) -> List[float]:
        if task_type is not None and isinstance(task_type, str):
            try:
                task_type = EmbeddingTaskType(task_type)
            except ValueError:
                raise ValueError(f"Invalid task type: {task_type}")

        response = genai.embed_content(
            model=self.embedding_model,
            content=content,
            task_type=task_type,
        )
        return response["embedding"]
