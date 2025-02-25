from ..shared.schemas import LLMConfig


class DeepSeekConfig(LLMConfig):
    """DeepSeek-specific configuration with proper prefixing"""

    base_url: str = "https://api.deepseek.com"

    class Config(LLMConfig.Config):
        env_prefix = "DEEPSEEK_"
