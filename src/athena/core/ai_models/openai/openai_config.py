from ..shared.schemas import LLMConfig


class OpenAIConfig(LLMConfig):
    """OpenAI-specific configuration with proper prefixing"""

    class Config(LLMConfig.Config):
        env_prefix = "OPENAI_"
