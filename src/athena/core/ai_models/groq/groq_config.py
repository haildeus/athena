from ..shared.schemas import LLMConfig


class GroqConfig(LLMConfig):
    """Groq-specific configuration with proper prefixing"""

    class Config(LLMConfig.Config):
        env_prefix = "GROQ_"
