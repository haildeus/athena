from typing import Optional

from pydantic_ai import Agent

from .claude.claude_client import ClaudeLLM
from .deepseek.deepseek_client import DeepSeekLLM
from .gemini.gemini_client import GeminiLLM
from .groq.groq_client import GroqLLM
from .mistral.mistral_client import MistralLLM
from .ollama.ollama_client import OllamaLLM
from .openai.openai_client import OpenAILLM
from .openrouter.openrouter_client import OpenRouterLLM
from .shared import LLMBase, MissingCredentialsError
from .xai.xai_client import xAILLM

_SERVICE_REGISTRY = {
    "gemini": GeminiLLM,
    "claude": ClaudeLLM,
    "deepseek": DeepSeekLLM,
    "groq": GroqLLM,
    "mistral": MistralLLM,
    "ollama": OllamaLLM,
    "openai": OpenAILLM,
    "openrouter": OpenRouterLLM,
    "xai": xAILLM,
}


def get_ai_service(service_name: str | None = None) -> LLMBase:
    """Get AI service instance with fallback to first available provider"""
    if service_name:
        return _get_specific_service(service_name)
    return _find_first_available()


def get_agent(service_name: str | None = None) -> Agent:
    """Get AI agent instance with fallback to first available provider"""
    if service_name:
        return _get_specific_service(service_name)
    resposne = _find_first_available()
    return resposne.agent


def _get_specific_service(name: str) -> LLMBase:
    """Get service by explicit name"""
    name = name.lower()
    if name not in _SERVICE_REGISTRY:
        available = ", ".join(_SERVICE_REGISTRY.keys())
        raise ValueError(f"Unknown service '{name}'. Available: {available}")

    try:
        return _SERVICE_REGISTRY[name]()
    except MissingCredentialsError:
        raise ValueError(f"Missing credentials for {name}")


def _find_first_available() -> LLMBase:
    """Find first service with valid credentials"""
    errors = []

    for name, service_class in _SERVICE_REGISTRY.items():
        try:
            return service_class()
        except MissingCredentialsError as e:
            errors.append(f"{name}: {e}")
        except Exception as e:
            errors.append(f"{name}: {str(e)}")

    error_list = "\n- ".join(errors)
    raise RuntimeError(f"No available AI providers:\n- {error_list}")
