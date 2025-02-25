from ..shared.schemas import LLMConfig


class MistralConfig(LLMConfig):
    """Mistral-specific configuration with proper prefixing"""

    class Config(LLMConfig.Config):
        env_prefix = "MISTRAL_"
