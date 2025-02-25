from enum import Enum

import vertexai
from pydantic_ai import Agent
from pydantic_ai.models.vertexai import VertexAIModel
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

from src.athena.core.ai_models.shared import LLMBase
from src.athena.core.ai_models.vertexai.vertex_config import VertexConfig


class EmbeddingTaskType(Enum):
    RETRIEVAL_QUERY = "RETRIEVAL_QUERY"
    RETRIEVAL_DOCUMENT = "RETRIEVAL_DOCUMENT"
    SEMANTIC_SIMILARITY = "SEMANTIC_SIMILARITY"
    CLASSIFICATION = "CLASSIFICATION"
    CLUSTERING = "CLUSTERING"
    QUESTION_ANSWERING = "QUESTION_ANSWERING"
    FACT_VERIFICATION = "FACT_VERIFICATION"
    CODE_RETRIEVAL_QUERY = "CODE_RETRIEVAL_QUERY"


class VertexLLM(LLMBase):
    @property
    def provider_name(self) -> str:
        return "Vertex"

    @property
    def agent(self) -> Agent:
        return self._agent

    def __init__(self):
        config = VertexConfig()
        super().__init__(config)

        self.model = VertexAIModel(
            model_name=config.model_name,
            project_id=config.project_id,
            region=config.region,
        )

        self._agent = Agent(model=self.model, name=self.provider_name)
        self.embedding_model = TextEmbeddingModel.from_pretrained(
            config.embedding_model_name
        )

        vertexai.init(project=config.project_id)

    def embed_content(
        self,
        content: list[str],
        task_type: EmbeddingTaskType | str = EmbeddingTaskType.CLUSTERING,
        dimensionality: int = 768,
    ) -> list[float]:
        if dimensionality <= 0 or dimensionality > 768:
            raise ValueError(
                "Invalid dimensionality: choose an output dimensionality between 1 and 768"
            )
        if not isinstance(content, list):
            raise ValueError("Invalid content: must be a list of strings")

        if task_type is not None and isinstance(task_type, str):
            try:
                task_type = EmbeddingTaskType(task_type)
            except ValueError:
                raise ValueError(f"Invalid task type: {task_type}")

        inputs = [TextEmbeddingInput(text, task_type.value) for text in content]
        kwargs = {"output_dimensionality": dimensionality} if dimensionality else {}

        embeddings = self.embedding_model.get_embeddings(inputs, **kwargs)

        return [embedding.values for embedding in embeddings]
