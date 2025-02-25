"""
This file contains the schemas for the capabilities of an diety
"""

from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import List

from src.athena.core.ai_models.claude.claude_client import ClaudeLLM
from src.athena.core.ai_models.deepseek.deepseek_client import DeepSeekLLM
from src.athena.core.ai_models.gemini.gemini_client import GeminiLLM
from src.athena.core.ai_models.groq.groq_client import GroqLLM
from src.athena.core.ai_models.mistral.mistral_client import MistralLLM
from src.athena.core.ai_models.ollama.ollama_client import OllamaLLM
from src.athena.core.ai_models.openai.openai_client import OpenAILLM
from src.athena.core.ai_models.openrouter.openrouter_client import OpenRouterLLM
from src.athena.core.ai_models.xai.xai_client import xAILLM
from src.athena.core.ai_models.vertexai.vertex_client import VertexLLM


class SupportedClients(Enum):
    TELEGRAM_USER = "TELEGRAM_USER"
    TELEGRAM_BOT = "TELEGRAM_BOT"


class SupportedModels(Enum):
    CLAUDE = ClaudeLLM
    DEEPSEEK = DeepSeekLLM
    GEMINI = GeminiLLM
    GROQ = GroqLLM
    MISTRAL = MistralLLM
    OLLAMA = OllamaLLM
    OPENAI = OpenAILLM
    OPENROUTER = OpenRouterLLM
    VERTEX = VertexLLM
    XAI = xAILLM


class Powers(BaseModel):
    """
    Powers represent the capabilities of the Pantheon diety
    """

    selected_clients: List[SupportedClients] = Field(
        ..., description="Clients to use the persona"
    )
    selected_model: SupportedModels = Field(..., description="Model to use the persona")

    @model_validator(mode="before")
    def validate_selected_clients(cls, values):
        selected_clients = values.get("selected_clients")
        selected_model = values.get("selected_model")

        if selected_clients is None or len(selected_clients) == 0:
            raise ValueError("At least one client must be selected")
        if selected_model is None:
            raise ValueError("A model must be selected")

        return values

    @classmethod
    def from_dict(cls, data: dict) -> "Powers":
        return cls(**data)
