from ..shared.schemas import LLMConfig


class xAIConfig(LLMConfig):
    """xAI-specific configuration with proper prefixing"""

    base_url: str = "https://api.xai.com"

    class Config(LLMConfig.Config):
        env_prefix = "XAI_"
