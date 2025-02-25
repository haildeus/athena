import asyncio
from typing import Any

from neo4j import AsyncGraphDatabase

from src.athena.core import logger
from src.athena.core.ai_models import LLMBase

from .operations.organon_init_op import (
    CLEAR_ORGANON_QUERIES,
    DROP_CONSTRAINT_QUERY,
    DROP_INDEX_QUERY,
    GET_CONSTRAINTS_QUERY,
    GET_INDEXES_QUERY,
    ORGANON_INIT_QUERIES,
)
from .organon_config import OrganonConfig, OrganonConnectionSettings


class OrganonModel:
    def __init__(
        self,
        model: LLMBase,
        settings: OrganonConnectionSettings = None,
        config: OrganonConfig = None,
    ):
        """
        Initialize the OrganonModel.

        Note: Direct instantiation does not perform asynchronous initialization.
        Use the `create` class method to ensure proper initialization.
        """
        self.settings = settings if settings else OrganonConnectionSettings()
        self.config = config if config else OrganonConfig()
        self.model = model
        self.semaphore = asyncio.Semaphore(self.config.SEMAPHORE_LIMIT)
        self.driver = AsyncGraphDatabase.driver(
            f"bolt://{self.settings.host}:{self.settings.port}",
            auth=(self.settings.user, self.settings.password),
            database=self.settings.database,
        )

    async def __ainit__(self):
        """Asynchronous initializer."""
        await self.initialize_organon()

    @classmethod
    async def create(
        cls,
        model: LLMBase,
        settings: OrganonConnectionSettings = None,
        config: OrganonConfig = None,
    ):
        """Factory method for asynchronous initialization."""
        instance = cls(model, settings, config)
        await instance.__ainit__()
        return instance

    async def run_query(self, query: str, params: dict[str, Any] | None = None):
        logger.debug(f"Executing query: {query} with params: {params}")
        async with self.semaphore:
            async with self.driver.session() as session:
                try:
                    result = await session.run(query, params)
                    return await result.data()
                except Exception as e:
                    logger.error(
                        f"Unexpected error running query '{query}' with params {params}: {e}"
                    )
                    raise e

    async def run_queries(
        self,
        queries: list[str],
        params: dict[str, Any] | None = None,
        sequential: bool = False,
    ):
        if isinstance(params, dict) or params is None:
            params = [params] * len(queries)  # Reuse same params if single dict or None
        elif len(params) != len(queries):
            raise ValueError("Number of parameter sets must match number of queries")

        if sequential:
            results = []
            async with self.semaphore:
                async with self.driver.session() as session:
                    for query, param in zip(queries, params, strict=True):
                        result = await session.run(query, param)
                        results.append(await result.data())
            return results

        results = await asyncio.gather(
            *[
                self.run_query(query, param)
                for query, param in zip(queries, params, strict=True)
            ]
        )
        return results

    async def update_settings(self, **kwargs):
        new_settings = self.settings.model_copy(update=kwargs)
        if (
            new_settings.host != self.settings.host
            or new_settings.port != self.settings.port
            or new_settings.user != self.settings.user
            or new_settings.password != self.settings.password
        ):
            await self.driver.close()
            self.driver = AsyncGraphDatabase.driver(
                f"bolt://{new_settings.host}:{new_settings.port}",
                auth=(new_settings.user, new_settings.password),
                database=new_settings.database,
            )
        self.settings = new_settings

    async def update_config(self, **kwargs):
        new_config = self.config.model_copy(update=kwargs)
        if new_config.SEMAPHORE_LIMIT != self.config.SEMAPHORE_LIMIT:
            self.semaphore = asyncio.Semaphore(new_config.SEMAPHORE_LIMIT)
        self.config = new_config

    async def initialize_organon(self):
        await self.run_queries(ORGANON_INIT_QUERIES, sequential=True)
        logger.info("Organon initialized: constraints and indexes created.")

    async def delete_organon(self):
        """
        Asynchronously deletes all entries and drops constraints/indexes.
        """
        logger.info("Dropping constraints...")
        fetched_constraints = await self.run_query(GET_CONSTRAINTS_QUERY)
        logger.info(f"Found {len(fetched_constraints)} constraints to drop.")
        for row in fetched_constraints:
            name = row["name"]
            query = DROP_CONSTRAINT_QUERY.format(name=name)
            await self.run_query(query)
        logger.info("All constraints dropped.")

        logger.info("Dropping indexes...")
        fetched_indexes = await self.run_query(GET_INDEXES_QUERY)
        logger.info(f"Found {len(fetched_indexes)} indexes to drop.")
        for row in fetched_indexes:
            name = row["name"]
            query = DROP_INDEX_QUERY.format(name=name)
            await self.run_query(query)
        logger.info("All constraints and indexes dropped.")

    async def clear_organon(self):
        """
        Asynchronously clears all data from the database.
        """
        await self.run_queries(CLEAR_ORGANON_QUERIES, sequential=True)
        logger.info("All nodes and relationships cleared.")
