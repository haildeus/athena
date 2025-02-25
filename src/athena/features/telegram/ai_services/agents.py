import json
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits

from src.athena.core.ai_models.shared import LLMBase
from src.athena.core.deus.schemas import Persona
from src.athena.features.telegram.ai_services.process import CommunityMessageProcessor
from src.athena.features.telegram.ai_services.prompts import (
    FOLLOW_UP_QUESTIONS_PROMPT,
    SUMMARIZE_AGENT_QUERY_COMMUNITY,
    SUMMARIZE_AGENT_SYSTEM_PROMPT,
)
from src.athena.features.telegram.schemas.telegram_schemas import (
    ChatMessage,
    ChatMessageReduced,
    ChatMessageReducedCluster,
    FollowUpQuestion,
    FollowUpResp,
    SummaryDependency,
    SumResp,
)

if TYPE_CHECKING:
    # Executed only during type checking by IDE
    from src.athena.core.deus.base.base_instance import Deus

from src.athena.core import logger


class ApolloSummarizeAgent:
    ANALYTICAL_TEMPERATURE = 0.45
    TOP_P = 0.8

    def __init__(self, model: LLMBase, persona: Persona, deus: "Deus"):
        self.model: LLMBase = model
        self.agent: Agent = model.agent
        self.persona: Persona = persona
        self.processor = CommunityMessageProcessor(model)
        self.deps = SummaryDependency(persona=self.persona)
        self.deus = deus

        self._inject_system_prompt(SUMMARIZE_AGENT_SYSTEM_PROMPT)

    def _inject_system_prompt(self, system_prompt: str):
        @self.agent.system_prompt
        async def message_summary_context(ctx: RunContext[SummaryDependency]) -> str:
            agent_persona = ctx.deps.persona
            bio_prompt = agent_persona.use_persona(system_prompt)
            return bio_prompt

    async def _transform_messages_into_clusters(
        self, messages: list[ChatMessage]
    ) -> list[ChatMessage]:
        try:
            important_messages, embeddings = await self.processor.analyze_messages(
                messages
            )
            clusters = await self.processor.cluster_messages(
                important_messages, embeddings
            )
            return clusters
        except Exception as e:
            logger.error(f"Error transforming messages into clusters: {e}")
            raise e

    def _reduce_chat_message_for_summary(
        self, chat_messages: list[ChatMessage]
    ) -> list[ChatMessageReduced]:
        reduced_chat_messages = []
        for message in chat_messages:
            reduced_chat_messages.append(ChatMessageReduced.from_chat_message(message))
        return reduced_chat_messages

    async def _execute_agent_query(
        self,
        query: str,
        deps: SummaryDependency,
        result_type: type[Any],
        model_settings: ModelSettings | None = None,
    ) -> Any:
        """Centralized method for executing agent queries and handling responses."""
        try:
            response = await self.agent.run(
                query,
                deps=deps,
                result_type=result_type,
                model_settings=model_settings,
            )
            return response
        except Exception as e:
            logger.error(f"Error executing agent query: {e}")
            raise e

    async def run_with_settings(
        self,
        query: str,
        result_type: type[Any],
        model_settings: ModelSettings | None = None,
    ) -> AsyncGenerator:
        """Runs the agent with streaming or non-streaming based on settings."""
        if self.deus.settings.streaming_response:
            async with self.agent.run_stream(
                query,
                deps=self.deps,
                result_type=result_type,
                model_settings=model_settings,
            ) as result:
                async for chunk in result.stream():
                    print(f"Chunk: {chunk}")
                    yield chunk
        else:
            yield await self._execute_agent_query(
                query, self.deps, result_type, model_settings
            )

    async def summarize_community_clusters(
        self, messages: list[ChatMessage]
    ) -> SumResp:
        try:
            clusters = await self._transform_messages_into_clusters(messages)
            clusters_string = ""

            for cluster_id, cluster in enumerate(clusters):
                reduced_cluster = self._reduce_chat_message_for_summary(cluster)
                clusters_string += f"**Cluster {cluster_id}:**\n"
                for message in reduced_cluster:
                    clusters_string += f"{json.dumps(message.model_dump())}, "
                clusters_string += "\n\n"
            query = SUMMARIZE_AGENT_QUERY_COMMUNITY.format(messages=clusters_string)
        except Exception as e:
            logger.error(f"Error formatting query: {e}")
            raise e

        # Await the result of run_with_settings, and then await the generator
        return await anext(
            self.run_with_settings(
                query,
                SumResp,
                model_settings=ModelSettings(
                    temperature=self.ANALYTICAL_TEMPERATURE, top_p=self.TOP_P
                ),
            )
        )

    async def summarize_community(self, messages: list[ChatMessage]) -> SumResp:
        try:
            reduced_chat_messages = self._reduce_chat_message_for_summary(messages)

            query = SUMMARIZE_AGENT_QUERY_COMMUNITY.format(
                messages=reduced_chat_messages
            )
        except Exception as e:
            logger.error(f"Error formatting query: {e}")
            raise e

        # Await the result of run_with_settings
        return await anext(self.run_with_settings(query, SumResp))

    async def generate_follow_up_questions(self, summary: SumResp) -> FollowUpResp:
        try:
            summary_string = "".join(
                [
                    f"**Topic {idx + 1}:**\n{topic.topic_name}\n{topic.summary}\n"
                    for idx, topic in enumerate(summary.topics)
                ]
            )
            summary_string = f"[{summary_string}]"

            query = FOLLOW_UP_QUESTIONS_PROMPT.format(summary=summary_string)
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {e}")
            raise e

        # Await the result of run_with_settings
        return await anext(
            self.run_with_settings(
                query,
                FollowUpResp,
                model_settings=ModelSettings(
                    temperature=self.ANALYTICAL_TEMPERATURE, top_p=self.TOP_P
                ),
            )
        )
