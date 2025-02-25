from ..shared.schemas import LLMConfig


class ClaudeConfig(LLMConfig):
    """Claude-specific configuration with proper prefixing"""

    class Config(LLMConfig.Config):
        env_prefix = "CLAUDE_"
