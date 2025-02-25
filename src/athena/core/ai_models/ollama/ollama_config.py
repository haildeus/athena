from typing import Optional

from ..shared.schemas import LLMConfig


class OllamaConfig(LLMConfig):
    """Ollama-specific configuration with proper prefixing"""

    base_url: str
    api_key: Optional[str] = None

    class Config(LLMConfig.Config):
        env_prefix = "OLLAMA_"
