from ..shared.schemas import LLMConfig


class OpenRouterConfig(LLMConfig):
    """OpenRouter-specific configuration with proper prefixing"""

    base_url: str = "https://openrouter.ai/api/v1"

    class Config(LLMConfig.Config):
        env_prefix = "OPENROUTER_"
