from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class OrganonConnectionSettings(BaseSettings):
    """Settings for connecting to the Organon Neo4j database."""

    host: str = "localhost"
    port: int = 7687
    user: str = "neo4j"
    password: str = "neo4j"
    database: str = "neo4j"
    model_config = SettingsConfigDict(env_prefix="ORGANON_")


class OrganonConfig(BaseModel):
    SEMAPHORE_LIMIT: int = 10
    PAGE_LIMIT: int = 10
