import datetime
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from src.athena.core.ai_models.shared import LLMBase

from ..operations.organon_node_op import (
    CREATE_CLUSTER_NODE_QUERY,
    CREATE_COMMUNITY_NODE_QUERY,
    CREATE_ENTITY_NODE_QUERY,
    CREATE_MESSAGE_NODE_QUERY,
    CREATE_PREFERENCE_NODE_QUERY,
    CREATE_ROOM_NODE_QUERY,
    CREATE_USER_NODE_QUERY,
    FETCH_CLUSTER_NODE_QUERY,
    FETCH_CLUSTERS_NODE_QUERY,
    FETCH_COMMUNITIES_NODE_QUERY,
    FETCH_COMMUNITY_NODE_QUERY,
    FETCH_ENTITIES_NODE_QUERY,
    FETCH_ENTITY_NODE_QUERY,
    FETCH_MESSAGE_NODE_QUERY,
    FETCH_MESSAGES_NODE_QUERY,
    FETCH_PREFERENCE_NODE_QUERY,
    FETCH_PREFERENCES_NODE_QUERY,
    FETCH_ROOM_NODE_QUERY,
    FETCH_ROOMS_NODE_QUERY,
    FETCH_USER_NODE_QUERY,
    FETCH_USERS_NODE_QUERY,
)


# --- Enums ---
class PlatformType(int, Enum):
    GLOBAL = 1
    TELEGRAM = 2
    DISCORD = 3
    TWITTER = 4

    @classmethod
    def from_string(cls, platform_str: str) -> "PlatformType":
        """Convert a string to a PlatformType."""
        if not isinstance(platform_str, str):
            raise ValueError("Platform string must be a string")
        platform_str = platform_str.upper()

        supported_platforms = [platform.name.lower() for platform in cls]
        if platform_str not in supported_platforms:
            raise ValueError(f"Unsupported platform: {platform_str}")

        return cls[platform_str]

    @classmethod
    def from_int(cls, platform_int: int) -> "PlatformType":
        """Convert an integer to a PlatformType."""
        if not isinstance(platform_int, int):
            raise ValueError("Platform integer must be an integer")
        return cls(platform_int)


# --- Base Classes (for common properties and methods) ---
class OrganonNode(BaseModel, ABC):
    """Base class for all Organon nodes."""

    uuid: str = Field(
        default_factory=lambda: str(uuid4()), description="Globally unique identifier."
    )
    name: str = Field(..., description="Name of the node.")
    platform: PlatformType = Field(..., description="Platform.")

    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="Timestamp when the node was created.",
    )
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="Timestamp when the node was last updated.",
    )

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrganonNode):
            return False
        return self.uuid == other.uuid

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @abstractmethod
    async def get_by_uuid(self, uuid: str) -> "OrganonNode":
        """Get the node by its globally unique identifier."""
        pass

    @abstractmethod
    async def get_by_uuids(self, uuids: list[str]) -> list["OrganonNode"]:
        """Get the nodes by their globally unique identifiers."""
        pass

    @abstractmethod
    async def save(self) -> tuple[str, dict[str, Any]]:
        """Save the node to the database."""
        pass

    @abstractmethod
    async def delete(self) -> tuple[str, dict[str, Any]]:
        """Delete the node from the database."""
        pass

    @abstractmethod
    async def update(self) -> tuple[str, dict[str, Any]]:
        """Update the node in the database."""
        pass

    async def embed_content(self, content: str | list[str]) -> list[float]:
        """Embed the content using the LLM."""
        return await LLMBase.embed_content(content)


# --- Message Node Models ---
class User(OrganonNode):
    user_id: str = Field(..., description="Globally unique user ID.")  # Required
    platform_handles: dict[PlatformType, str] = Field(
        default_factory=dict, description="Platform-specific user handles."
    )
    name: str | None = Field(None, description="User's name.")

    summary: str | None = Field(None, description="Summary of user activity.")
    classification: str | None = Field(
        None, description="User classification (e.g., 'business', 'personal')."
    )
    last_summary_update: datetime.datetime | None = Field(
        None, description="Last time the summary was updated."
    )

    async def get_by_uuid(self, uuid: str) -> "User":
        """Get the user by its globally unique identifier."""
        return FETCH_USER_NODE_QUERY, {"uuid": uuid}

    async def get_by_uuids(self, uuids: list[str]) -> list["User"]:
        """Get users by their globally unique identifiers."""
        return FETCH_USERS_NODE_QUERY, {"uuids": uuids}

    async def save(self) -> tuple[str, dict[str, Any]]:
        """Save or update the user to the database."""
        params = {
            "uuid": self.uuid,
            "user_id": self.user_id,
            "platform_handles": self.platform_handles,
            "name": self.name,
            "platform": self.platform.value,  # Store as integer
            "summary": self.summary,
            "classification": self.classification,
            "last_summary_update": self.last_summary_update.isoformat()
            if self.last_summary_update
            else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return CREATE_USER_NODE_QUERY, params

    async def delete(self) -> tuple[str, dict[str, Any]]:
        """Delete the user from the database."""
        query = """
            MATCH (u:User {uuid: $uuid})
            DETACH DELETE u
        """
        params = {"uuid": self.uuid}
        return query, params

    async def update(self) -> tuple[str, dict[str, Any]]:
        """Update the user in the database (same as save for now)."""
        return await self.save()  # Reuse save logic


class Room(OrganonNode):
    room_id: str = Field(..., description="Globally unique chat ID.")  # Required
    platform: PlatformType = Field(..., description="Platform.")  # Required
    name: str = Field(..., description="Chat name.")  # Required
    room_type: str = Field(
        ..., description="Chat type (e.g., 'personal', 'group')."
    )  # Required

    community_id: str | None = Field(None, description="Community ID.")
    summary: str | None = Field(None, description="Chat summary.")

    async def get_by_uuid(self, uuid: str) -> "Room":
        """Get the room by its globally unique identifier."""
        return FETCH_ROOM_NODE_QUERY, {"uuid": uuid}

    async def get_by_uuids(self, uuids: list[str]) -> list["Room"]:
        """Get rooms by their globally unique identifiers."""
        return FETCH_ROOMS_NODE_QUERY, {"uuids": uuids}

    async def save(self) -> tuple[str, dict[str, Any]]:
        """Save or update the room to the database."""
        params = {
            "uuid": self.uuid,
            "room_id": self.room_id,
            "platform": self.platform.value,
            "name": self.name,
            "room_type": self.room_type,
            "community_id": self.community_id,
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return CREATE_ROOM_NODE_QUERY, params

    async def delete(self) -> tuple[str, dict[str, Any]]:
        """Delete the room from the database."""
        query = """
            MATCH (r:Room {uuid: $uuid})
            DETACH DELETE r
        """
        params = {"uuid": self.uuid}
        return query, params

    async def update(self) -> tuple[str, dict[str, Any]]:
        """Update the room in the database (same as save)."""
        return await self.save()


class Message(OrganonNode):
    message_id: str = Field(..., description="Globally unique message ID.")  # Required
    room_id: str = Field(..., description="Chat ID.")  # Required
    user_id: str = Field(..., description="User ID.")  # Required
    platform: PlatformType = Field(..., description="Platform.")  # Required
    content: str = Field(..., description="Message content.")  # Required

    engagement_score: float = Field(default=0, description="Engagement score.")
    embedding: list[float] | None = Field(None, description="Message embedding.")

    async def get_by_uuid(self, uuid: str) -> "Message":
        """Get the message by its globally unique identifier."""
        return FETCH_MESSAGE_NODE_QUERY, {"uuid": uuid}

    async def get_by_uuids(self, uuids: list[str]) -> list["Message"]:
        """Get messages by their globally unique identifiers."""
        return FETCH_MESSAGES_NODE_QUERY, {"uuids": uuids}

    async def save(self) -> tuple[str, dict[str, Any]]:
        """Save or update the message to the database."""
        params = {
            "uuid": self.uuid,
            "message_id": self.message_id,
            "room_id": self.room_id,
            "user_id": self.user_id,
            "platform": self.platform.value,
            "content": self.content,
            "engagement_score": self.engagement_score,
            "embedding": self.embedding,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        query = CREATE_MESSAGE_NODE_QUERY
        # Add embedding setting to the query
        if self.embedding:
            query = query.replace(
                "RETURN m",
                "WITH m CALL db.create.setNodeVectorProperty(m, 'embedding', $embedding) RETURN m",
            )
        return query, params

    async def delete(self) -> tuple[str, dict[str, Any]]:
        """Delete the message from the database."""
        query = """
            MATCH (m:Message {uuid: $uuid})
            DETACH DELETE m
        """
        params = {"uuid": self.uuid}
        return query, params

    async def update(self) -> tuple[str, dict[str, Any]]:
        """Update the message in the database (same as save)."""
        return await self.save()


class Cluster(OrganonNode):
    room_id: str = Field(..., description="Chat ID.")  # Required

    start_time: datetime.datetime = Field(
        ..., description="Start time of aggregation period."
    )  # Required
    end_time: datetime.datetime = Field(
        ..., description="End time of aggregation period."
    )  # Required

    keywords: list[str] = Field(
        ..., description="Keywords for the cluster."
    )  # Required
    messages: list[int] = Field(
        ..., description="Message IDs in the cluster."
    )  # Required
    embeddings: list[float] = Field(None, description="Cluster embeddings.")  # Required

    platform: PlatformType = Field(..., description="Platform.")  # Required

    async def get_by_uuid(self, uuid: str) -> "Cluster":
        """Get the cluster by its globally unique identifier."""
        return FETCH_CLUSTER_NODE_QUERY, {"uuid": uuid}

    async def get_by_uuids(self, uuids: list[str]) -> list["Cluster"]:
        """Get clusters by their globally unique identifiers."""
        return FETCH_CLUSTERS_NODE_QUERY, {"uuids": uuids}

    async def save(self) -> tuple[str, dict[str, Any]]:
        """Save or update the cluster to the database."""
        params = {
            "uuid": self.uuid,
            "room_id": self.room_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "keywords": self.keywords,
            "messages": self.messages,
            "embeddings": self.embeddings,
            "platform": self.platform.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return CREATE_CLUSTER_NODE_QUERY, params

    async def delete(self) -> tuple[str, dict[str, Any]]:
        """Delete the cluster from the database."""
        query = """
            MATCH (c:Cluster {uuid: $uuid})
            DETACH DELETE c
        """
        params = {"uuid": self.uuid}
        return query, params

    async def update(self) -> tuple[str, dict[str, Any]]:
        """Update the cluster in the database (same as save)."""
        return await self.save()


class Community(OrganonNode):
    community_id: str = Field(
        ..., description="Globally unique community ID."
    )  # Required
    name: str = Field(..., description="Community name.")  # Required
    description: str | None = Field(None, description="Community description.")

    async def get_by_uuid(self, uuid: str) -> "Community":
        """Get the community by its globally unique identifier."""
        return FETCH_COMMUNITY_NODE_QUERY, {"uuid": uuid}

    async def get_by_uuids(self, uuids: list[str]) -> list["Community"]:
        """Get communities by their globally unique identifiers."""
        return FETCH_COMMUNITIES_NODE_QUERY, {"uuids": uuids}

    async def save(self) -> tuple[str, dict[str, Any]]:
        """Save or update the community to the database."""
        params = {
            "uuid": self.uuid,
            "community_id": self.community_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "platform": self.platform.value,
        }
        return CREATE_COMMUNITY_NODE_QUERY, params

    async def delete(self) -> tuple[str, dict[str, Any]]:
        """Delete the community from the database."""
        query = """
            MATCH (c:Community {uuid: $uuid})
            DETACH DELETE c
        """
        params = {"uuid": self.uuid}
        return query, params

    async def update(self) -> tuple[str, dict[str, Any]]:
        """Update the community in the database (same as save)."""
        return await self.save()


# --- Entity Models ---
class Entity(OrganonNode):
    name: str = Field(..., description="Entity name.")
    entity_type: str = Field(
        ..., description="Entity type (e.g., 'person', 'product', 'topic')."
    )

    embedding: list[float] | None = Field(None, description="Name embedding.")

    async def get_by_uuid(self, uuid: str) -> "Entity":
        """Get the entity by its globally unique identifier."""
        return FETCH_ENTITY_NODE_QUERY, {"uuid": uuid}

    async def get_by_uuids(self, uuids: list[str]) -> list["Entity"]:
        """Get entities by their globally unique identifiers."""
        return FETCH_ENTITIES_NODE_QUERY, {"uuids": uuids}

    async def save(self) -> tuple[str, dict[str, Any]]:
        """Save or update the entity to the database."""
        params = {
            "uuid": self.uuid,
            "name": self.name,
            "entity_type": self.entity_type,
            "embedding": self.embedding,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "platform": self.platform.value,
        }
        query = CREATE_ENTITY_NODE_QUERY
        # Add embedding setting to the query.
        if self.embedding:
            query = query.replace(
                "RETURN e",
                "WITH e CALL db.create.setNodeVectorProperty(e, 'embedding', $embedding) RETURN e",
            )

        return query, params

    async def delete(self) -> tuple[str, dict[str, Any]]:
        """Delete the entity from the database."""
        query = """
            MATCH (e:Entity {uuid: $uuid})
            DETACH DELETE e
        """
        params = {"uuid": self.uuid}
        return query, params

    async def update(self) -> tuple[str, dict[str, Any]]:
        """Update the entity in the database (same as save)."""
        return await self.save()


class Topic(Entity):
    entity_type: Literal["topic"] = Field(default="topic", description="Entity type.")


class Preference(OrganonNode):
    preference_id: str = Field(..., description="Unique preference ID.")
    preference_type: Literal["like", "dislike", "habit", "goal", "value", "other"] = (
        Field(..., description="Type of preference.")
    )
    description: str | None = Field(None, description="Description of the preference.")
    embedding: list[float] | None = Field(
        None, description="Embedding for the preference."
    )
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="Creation timestamp.",
    )
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="Last update timestamp.",
    )

    async def get_by_uuid(self, uuid: str) -> "Preference":
        """Get the preference by its globally unique identifier."""
        return FETCH_PREFERENCE_NODE_QUERY, {"uuid": uuid}

    async def get_by_uuids(self, uuids: list[str]) -> list["Preference"]:
        """Get preferences by their globally unique identifiers."""
        return FETCH_PREFERENCES_NODE_QUERY, {"uuids": uuids}

    async def save(self) -> tuple[str, dict[str, Any]]:
        """Save or update the preference to the database."""
        params = {
            "uuid": self.uuid,
            "preference_id": self.preference_id,
            "preference_type": self.preference_type,
            "description": self.description,
            "embedding": self.embedding,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "platform": self.platform.value,
        }
        query = CREATE_PREFERENCE_NODE_QUERY
        if self.embedding:
            query = query.replace(
                "RETURN p",
                "WITH p CALL db.create.setNodeVectorProperty(p, 'embedding', $embedding) RETURN p",
            )
        return query, params

    async def delete(self) -> tuple[str, dict[str, Any]]:
        """Delete the preference from the database."""
        query = """
            MATCH (p:Preference {uuid: $uuid})
            DETACH DELETE p
        """
        params = {"uuid": self.uuid}
        return query, params

    async def update(self) -> tuple[str, dict[str, Any]]:
        """Update the preference in the database (same as save)."""
        return await self.save()
