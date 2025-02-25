from ..shared.schemas import LLMConfig


class VertexConfig(LLMConfig):
    """Vertex-specific configuration with explicit environment binding"""

    embedding_model_name: str
    model_prefix: str = "models/"
    project_id: str
    region: str

    class Config(LLMConfig.Config):
        env_prefix = "VERTEX_"
