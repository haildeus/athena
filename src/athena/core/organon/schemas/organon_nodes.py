import datetime
from abc import ABC
from enum import Enum
from typing import Any, ClassVar, TypeVar
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
    CREATE_TOPIC_NODE_QUERY,
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
    FETCH_TOPIC_NODE_QUERY,
    FETCH_TOPICS_NODE_QUERY,
    FETCH_USER_NODE_QUERY,
    FETCH_USERS_NODE_QUERY,
)


# --- Enums ---
class PlatformType(int, Enum):
    """
    Enumeration of supported platforms in the Organon system.

    Each platform is assigned a unique integer value for database storage.
    The enum provides conversion methods between string names, integer values,
    and enum instances to facilitate flexible usage across the system.

    Attributes:
        GLOBAL (1): Platform-agnostic or cross-platform content
        TELEGRAM (2): Telegram messaging platform
        DISCORD (3): Discord messaging platform
        TWITTER (4): Twitter/X social media platform
    """

    GLOBAL = 1
    TELEGRAM = 2
    DISCORD = 3
    TWITTER = 4

    @classmethod
    def from_string(cls, platform_str: str) -> "PlatformType":
        """
        Convert a string representation to a PlatformType enum.

        Args:
            platform_str: Case-insensitive string name of the platform (e.g., "telegram")

        Returns:
            The corresponding PlatformType enum value

        Raises:
            ValueError: If the input is not a string or not a supported platform
        """
        if not isinstance(platform_str, str):
            raise ValueError("Platform string must be a string")
        platform_str = platform_str.upper()

        supported_platforms = [platform.name.lower() for platform in cls]
        if platform_str not in supported_platforms:
            raise ValueError(f"Unsupported platform: {platform_str}")

        return cls[platform_str]

    @classmethod
    def from_int(cls, platform_int: int) -> "PlatformType":
        """
        Convert an integer value to a PlatformType enum.

        Args:
            platform_int: Integer value corresponding to a platform (e.g., 2 for TELEGRAM)

        Returns:
            The corresponding PlatformType enum value

        Raises:
            ValueError: If the input is not an integer or not a valid platform value
        """
        if not isinstance(platform_int, int):
            raise ValueError("Platform integer must be an integer")
        return cls(platform_int)


# Type for self-referencing generic
T = TypeVar("T", bound="OrganonNode")


# --- Base Classes (for common properties and methods) ---
class OrganonNode(BaseModel, ABC):
    """
    Base class for all nodes in the Organon graph database system.

    This abstract class defines the common structure, properties, and behaviors
    for all node types in the system. It provides a unified interface for database
    operations like creation, retrieval, updating, and deletion of nodes.

    The class uses class variables for metadata that define how each node type
    interacts with the database, making it easy to customize behavior in subclasses
    while maintaining a consistent interface.

    Class Variables:
        NODE_LABEL: The Neo4j node label used in Cypher queries
        FETCH_QUERY: Query template for fetching a single node by UUID
        FETCH_MULTI_QUERY: Query template for fetching multiple nodes by UUIDs
        CREATE_QUERY: Query template for creating or updating a node
        HAS_EMBEDDING: Whether this node type supports vector embeddings
        EMBEDDING_RETURN_IDENTIFIER: The identifier used in embedding queries

    Attributes:
        uuid: Globally unique identifier for the node
        name: Human-readable name of the node
        platform: The platform this node belongs to
        created_at: Timestamp when the node was first created
        updated_at: Timestamp when the node was last updated
    """

    # Class variables for node metadata
    NODE_LABEL: ClassVar[str] = ""  # Override in subclasses
    FETCH_QUERY: ClassVar[str] = ""  # Single-node fetch query
    FETCH_MULTI_QUERY: ClassVar[str] = ""  # Multi-node fetch query
    CREATE_QUERY: ClassVar[str] = ""  # Node creation/update query
    HAS_EMBEDDING: ClassVar[bool] = False  # Whether the node has an embedding property
    EMBEDDING_RETURN_IDENTIFIER: ClassVar[str] = (
        ""  # The return identifier for embedding queries
    )

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
        """
        Generate a hash value for the node based on its UUID.

        This allows nodes to be used in sets and as dictionary keys.

        Returns:
            Hash value of the node's UUID
        """
        return hash(self.uuid)

    def __eq__(self, other: object) -> bool:
        """
        Compare two nodes for equality based on their UUIDs.

        Two nodes are considered equal if they have the same UUID,
        regardless of their other attributes or even node types.

        Args:
            other: Another object to compare with

        Returns:
            True if the other object is an OrganonNode with the same UUID
        """
        if not isinstance(other, OrganonNode):
            return False
        return self.uuid == other.uuid

    def __ne__(self, other: object) -> bool:
        """
        Compare two nodes for inequality based on their UUIDs.

        Args:
            other: Another object to compare with

        Returns:
            True if the other object is not an OrganonNode or has a different UUID
        """
        return not self.__eq__(other)

    async def get_by_uuid(self, uuid: str) -> tuple[str, dict[str, Any]]:
        """
        Get the query and parameters to fetch a node by its UUID.

        Args:
            uuid: The UUID of the node to fetch

        Returns:
            A tuple of (query_string, parameters_dict) to execute against the database

        Raises:
            NotImplementedError: If the subclass doesn't define FETCH_QUERY
        """
        if not self.__class__.FETCH_QUERY:
            raise NotImplementedError(
                f"FETCH_QUERY not defined for {self.__class__.__name__}"
            )
        return self.__class__.FETCH_QUERY, {"uuid": uuid}

    async def get_by_uuids(self, uuids: list[str]) -> tuple[str, dict[str, Any]]:
        """
        Get the query and parameters to fetch multiple nodes by their UUIDs.

        Args:
            uuids: List of UUIDs of the nodes to fetch

        Returns:
            A tuple of (query_string, parameters_dict) to execute against the database

        Raises:
            NotImplementedError: If the subclass doesn't define FETCH_MULTI_QUERY
        """
        if not self.__class__.FETCH_MULTI_QUERY:
            raise NotImplementedError(
                f"FETCH_MULTI_QUERY not defined for {self.__class__.__name__}"
            )
        return self.__class__.FETCH_MULTI_QUERY, {"uuids": uuids}

    async def delete(self) -> tuple[str, dict[str, Any]]:
        """
        Get the query and parameters to delete this node from the database.

        The query uses DETACH DELETE to ensure that relationships are also removed.

        Returns:
            A tuple of (query_string, parameters_dict) to execute against the database

        Raises:
            NotImplementedError: If the subclass doesn't define NODE_LABEL
        """
        if not self.__class__.NODE_LABEL:
            raise NotImplementedError(
                f"NODE_LABEL not defined for {self.__class__.__name__}"
            )

        label = self.__class__.NODE_LABEL
        identifier = label[0].lower()  # First letter of label as identifier

        query = f"""
            MATCH ({identifier}:{label} {{uuid: $uuid}})
            DETACH DELETE {identifier}
        """
        params = {"uuid": self.uuid}
        return query, params

    async def update(self) -> tuple[str, dict[str, Any]]:
        """
        Get the query and parameters to update this node in the database.

        This is an alias for save() since the save operation handles both
        creation and updates via MERGE.

        Returns:
            A tuple of (query_string, parameters_dict) to execute against the database
        """
        return await self.save()

    async def embed_content(self, content: str | list[str]) -> list[float]:
        """
        Generate vector embeddings for the given content using the LLM.

        This method can be used to create embeddings for node properties
        that support vector search in the database.

        Args:
            content: Text content or list of text contents to embed

        Returns:
            A list of floating-point values representing the embedding vector
        """
        return await LLMBase.embed_content(content)

    def get_save_params(self) -> dict[str, Any]:
        """
        Get the parameters for saving this node to the database.

        This method collects the common parameters for all node types.
        Subclasses should override this method to add their specific parameters
        by calling super().get_save_params() and updating the returned dict.

        Returns:
            Dictionary of parameters for the save query
        """
        params = {
            "uuid": self.uuid,
            "name": self.name,
            "platform": self.platform.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return params

    async def save(self) -> tuple[str, dict[str, Any]]:
        """
        Get the query and parameters to save this node to the database.

        This method handles both creation of new nodes and updates to existing ones
        by using Neo4j's MERGE operation. It also handles special processing for
        nodes with embeddings.

        Returns:
            A tuple of (query_string, parameters_dict) to execute against the database

        Raises:
            NotImplementedError: If the subclass doesn't define CREATE_QUERY
        """
        if not self.__class__.CREATE_QUERY:
            raise NotImplementedError(
                f"CREATE_QUERY not defined for {self.__class__.__name__}"
            )

        params = self.get_save_params()
        query = self.__class__.CREATE_QUERY

        # Handle embedding if necessary
        if (
            self.__class__.HAS_EMBEDDING
            and hasattr(self, "embedding")
            and getattr(self, "embedding")
        ):
            identifier = self.__class__.EMBEDDING_RETURN_IDENTIFIER
            query = query.replace(
                f"RETURN {identifier}",
                f"WITH {identifier} CALL db.create.setNodeVectorProperty({identifier}, 'embedding', $embedding) RETURN {identifier}",
            )

        return query, params


# --- Message Node Models ---
class User(OrganonNode):
    """
    Represents a user in the Organon system.

    The User node is a fundamental entity in the graph database that represents
    an individual user across various platforms. It stores basic user information
    and serves as a connection point for relationships to rooms, messages, topics,
    and other entities.

    Users can be connected to:
    - Rooms via BELONGS_TO or POSTED_IN relationships
    - Topics via RELATED_TO relationships
    - Messages via POSTED relationships
    - Preferences via HAS_PREFERENCE relationships

    Class Variables:
        NODE_LABEL: "User" - The Neo4j label for this node type
        FETCH_QUERY: Query to fetch a single user by UUID
        FETCH_MULTI_QUERY: Query to fetch multiple users by UUIDs
        CREATE_QUERY: Query to create or update a user
        HAS_EMBEDDING: True - Users support vector embeddings for similarity search
        EMBEDDING_RETURN_IDENTIFIER: "u" - Identifier used in embedding queries

    Attributes:
        uuid: Globally unique identifier for the user
        name: Display name or username
        platform: The platform this user belongs to (e.g., TELEGRAM, DISCORD)
        platform_id: Platform-specific user identifier
        embedding: Optional vector embedding for semantic search
        created_at: Timestamp when the user was first created
        updated_at: Timestamp when the user was last updated

    Example:
        ```python
        # Create a new user
        user = User(
            name="john_doe",
            platform=PlatformType.TELEGRAM,
            platform_id="12345678"
        )

        # Save to database
        query, params = await user.save()
        await session.run(query, params)
        ```
    """

    NODE_LABEL: ClassVar[str] = "User"
    FETCH_QUERY: ClassVar[str] = FETCH_USER_NODE_QUERY
    FETCH_MULTI_QUERY: ClassVar[str] = FETCH_USERS_NODE_QUERY
    CREATE_QUERY: ClassVar[str] = CREATE_USER_NODE_QUERY
    HAS_EMBEDDING: ClassVar[bool] = True
    EMBEDDING_RETURN_IDENTIFIER: ClassVar[str] = "u"

    platform_id: str = Field(..., description="Platform-specific user identifier.")
    embedding: list[float] | None = Field(
        None, description="Vector embedding for semantic search."
    )

    def get_save_params(self) -> dict[str, Any]:
        """
        Get parameters for saving this user to the database.

        Extends the base implementation to include user-specific parameters
        like platform_id and embedding.

        Returns:
            Dictionary of parameters for the save query
        """
        params = super().get_save_params()
        params["platform_id"] = self.platform_id
        if self.embedding:
            params["embedding"] = self.embedding
        return params


class Room(OrganonNode):
    """
    Represents a chat room or conversation space in the Organon system.

    The Room node represents a container for messages and users, such as a chat room,
    channel, group chat, or any other space where communication occurs. It serves as
    a primary organizational unit for conversations.

    Rooms can be connected to:
    - Users via BELONGS_TO relationships (membership)
    - Messages via POSTED_IN relationships (content)
    - Topics via RELATED_TO relationships (subject matter)
    - Communities via BELONGS_TO relationships (higher-level grouping)

    Class Variables:
        NODE_LABEL: "Room" - The Neo4j label for this node type
        FETCH_QUERY: Query to fetch a single room by UUID
        FETCH_MULTI_QUERY: Query to fetch multiple rooms by UUIDs
        CREATE_QUERY: Query to create or update a room
        HAS_EMBEDDING: True - Rooms support vector embeddings for similarity search
        EMBEDDING_RETURN_IDENTIFIER: "r" - Identifier used in embedding queries

    Attributes:
        uuid: Globally unique identifier for the room
        name: Display name of the room
        platform: The platform this room belongs to (e.g., TELEGRAM, DISCORD)
        platform_id: Platform-specific room identifier
        description: Optional text description of the room's purpose or content
        embedding: Optional vector embedding for semantic search
        created_at: Timestamp when the room was first created
        updated_at: Timestamp when the room was last updated

    Example:
        ```python
        # Create a new room
        room = Room(
            name="Python Developers",
            platform=PlatformType.DISCORD,
            platform_id="server123_channel456",
            description="Discussion about Python programming"
        )

        # Save to database
        query, params = await room.save()
        await session.run(query, params)
        ```
    """

    NODE_LABEL: ClassVar[str] = "Room"
    FETCH_QUERY: ClassVar[str] = FETCH_ROOM_NODE_QUERY
    FETCH_MULTI_QUERY: ClassVar[str] = FETCH_ROOMS_NODE_QUERY
    CREATE_QUERY: ClassVar[str] = CREATE_ROOM_NODE_QUERY
    HAS_EMBEDDING: ClassVar[bool] = True
    EMBEDDING_RETURN_IDENTIFIER: ClassVar[str] = "r"

    platform_id: str = Field(..., description="Platform-specific room identifier.")
    description: str | None = Field(None, description="Description of the room.")
    embedding: list[float] | None = Field(
        None, description="Vector embedding for semantic search."
    )

    def get_save_params(self) -> dict[str, Any]:
        """
        Get parameters for saving this room to the database.

        Extends the base implementation to include room-specific parameters
        like platform_id, description, and embedding.

        Returns:
            Dictionary of parameters for the save query
        """
        params = super().get_save_params()
        params["platform_id"] = self.platform_id
        params["description"] = self.description
        if self.embedding:
            params["embedding"] = self.embedding
        return params


class Message(OrganonNode):
    """
    Represents a message or content item in the Organon system.

    The Message node represents an individual message, post, or content item
    sent by a user in a room. It contains the actual content text and metadata
    about the message, forming the core data unit for analysis and clustering.

    Messages can be connected to:
    - Users via POSTED_BY relationships (authorship)
    - Rooms via POSTED_IN relationships (location)
    - Clusters via BELONGS_TO relationships (categorization)
    - Topics via RELATED_TO relationships (subject matter)
    - Entities via MENTIONS relationships (references)

    Class Variables:
        NODE_LABEL: "Message" - The Neo4j label for this node type
        FETCH_QUERY: Query to fetch a single message by UUID
        FETCH_MULTI_QUERY: Query to fetch multiple messages by UUIDs
        CREATE_QUERY: Query to create or update a message
        HAS_EMBEDDING: True - Messages support vector embeddings for similarity search
        EMBEDDING_RETURN_IDENTIFIER: "m" - Identifier used in embedding queries

    Attributes:
        uuid: Globally unique identifier for the message
        name: Short identifier or title for the message (often auto-generated)
        platform: The platform this message was posted on (e.g., TELEGRAM, DISCORD)
        platform_id: Platform-specific message identifier
        content: The actual text content of the message
        embedding: Vector embedding for semantic search and clustering
        created_at: Timestamp when the message was first created
        updated_at: Timestamp when the message was last updated

    Example:
        ```python
        # Create a new message
        message = Message(
            name="msg_12345",
            platform=PlatformType.TELEGRAM,
            platform_id="msg123456789",
            content="Hello world! This is a test message."
        )

        # Generate and set embedding
        message.embedding = await message.embed_content(message.content)

        # Save to database
        query, params = await message.save()
        await session.run(query, params)
        ```
    """

    NODE_LABEL: ClassVar[str] = "Message"
    FETCH_QUERY: ClassVar[str] = FETCH_MESSAGE_NODE_QUERY
    FETCH_MULTI_QUERY: ClassVar[str] = FETCH_MESSAGES_NODE_QUERY
    CREATE_QUERY: ClassVar[str] = CREATE_MESSAGE_NODE_QUERY
    HAS_EMBEDDING: ClassVar[bool] = True
    EMBEDDING_RETURN_IDENTIFIER: ClassVar[str] = "m"

    platform_id: str = Field(..., description="Platform-specific message identifier.")
    content: str = Field(..., description="Content of the message.")
    embedding: list[float] | None = Field(
        None, description="Vector embedding for semantic search."
    )

    def get_save_params(self) -> dict[str, Any]:
        """
        Get parameters for saving this message to the database.

        Extends the base implementation to include message-specific parameters
        like platform_id, content, and embedding.

        Returns:
            Dictionary of parameters for the save query
        """
        params = super().get_save_params()
        params["platform_id"] = self.platform_id
        params["content"] = self.content
        if self.embedding:
            params["embedding"] = self.embedding
        return params


class Cluster(OrganonNode):
    """
    Represents a cluster of related messages in the Organon system.

    The Cluster node represents a grouping of semantically related messages,
    typically created through embedding-based clustering algorithms. Clusters
    help organize large volumes of messages into coherent topics or themes.

    Clusters can be connected to:
    - Messages via INCLUDES relationships (containment)
    - Topics via RELATED_TO relationships (subject matter)
    - Rooms via RELATED_TO relationships (context)

    Class Variables:
        NODE_LABEL: "Cluster" - The Neo4j label for this node type
        FETCH_QUERY: Query to fetch a single cluster by UUID
        FETCH_MULTI_QUERY: Query to fetch multiple clusters by UUIDs
        CREATE_QUERY: Query to create or update a cluster
        HAS_EMBEDDING: True - Clusters support vector embeddings (typically centroids)
        EMBEDDING_RETURN_IDENTIFIER: "c" - Identifier used in embedding queries

    Attributes:
        uuid: Globally unique identifier for the cluster
        name: Display name or title for the cluster
        platform: The platform this cluster belongs to (e.g., TELEGRAM, DISCORD)
        description: Text description of the cluster's theme or content
        embedding: Vector embedding representing the cluster centroid
        created_at: Timestamp when the cluster was first created
        updated_at: Timestamp when the cluster was last updated

    Example:
        ```python
        # Create a new cluster
        cluster = Cluster(
            name="Python Error Handling",
            platform=PlatformType.DISCORD,
            description="Discussions about Python exception handling and best practices"
        )

        # Generate and set embedding (e.g., from message embeddings)
        message_embeddings = [...]  # List of message embeddings in this cluster
        cluster.embedding = calculate_centroid(message_embeddings)

        # Save to database
        query, params = await cluster.save()
        await session.run(query, params)
        ```
    """

    NODE_LABEL: ClassVar[str] = "Cluster"
    FETCH_QUERY: ClassVar[str] = FETCH_CLUSTER_NODE_QUERY
    FETCH_MULTI_QUERY: ClassVar[str] = FETCH_CLUSTERS_NODE_QUERY
    CREATE_QUERY: ClassVar[str] = CREATE_CLUSTER_NODE_QUERY
    HAS_EMBEDDING: ClassVar[bool] = True
    EMBEDDING_RETURN_IDENTIFIER: ClassVar[str] = "c"

    description: str = Field(..., description="Description of the cluster.")
    embedding: list[float] | None = Field(
        None, description="Vector embedding for semantic search."
    )

    def get_save_params(self) -> dict[str, Any]:
        """
        Get parameters for saving this cluster to the database.

        Extends the base implementation to include cluster-specific parameters
        like description and embedding.

        Returns:
            Dictionary of parameters for the save query
        """
        params = super().get_save_params()
        params["description"] = self.description
        if self.embedding:
            params["embedding"] = self.embedding
        return params


class Community(OrganonNode):
    """
    Represents a community or group of related rooms in the Organon system.

    The Community node represents a higher-level organizational unit that contains
    multiple related rooms. It can represent a server, a forum, or any other
    grouping of conversation spaces that share a common theme or purpose.

    Communities can be connected to:
    - Rooms via INCLUDES relationships (containment)
    - Topics via RELATED_TO relationships (subject matter)
    - Users via BELONGS_TO relationships (membership)

    Class Variables:
        NODE_LABEL: "Community" - The Neo4j label for this node type
        FETCH_QUERY: Query to fetch a single community by UUID
        FETCH_MULTI_QUERY: Query to fetch multiple communities by UUIDs
        CREATE_QUERY: Query to create or update a community
        HAS_EMBEDDING: False - Communities typically don't have embeddings
        EMBEDDING_RETURN_IDENTIFIER: "cm" - Identifier used in embedding queries

    Attributes:
        uuid: Globally unique identifier for the community
        name: Display name of the community
        platform: The platform this community belongs to (e.g., TELEGRAM, DISCORD)
        platform_id: Platform-specific community identifier
        description: Text description of the community's purpose or content
        created_at: Timestamp when the community was first created
        updated_at: Timestamp when the community was last updated

    Example:
        ```python
        # Create a new community
        community = Community(
            name="Python Developers Network",
            platform=PlatformType.DISCORD,
            platform_id="server123",
            description="A network of rooms for Python developers of all levels"
        )

        # Save to database
        query, params = await community.save()
        await session.run(query, params)
        ```
    """

    NODE_LABEL: ClassVar[str] = "Community"
    FETCH_QUERY: ClassVar[str] = FETCH_COMMUNITY_NODE_QUERY
    FETCH_MULTI_QUERY: ClassVar[str] = FETCH_COMMUNITIES_NODE_QUERY
    CREATE_QUERY: ClassVar[str] = CREATE_COMMUNITY_NODE_QUERY
    HAS_EMBEDDING: ClassVar[bool] = False
    EMBEDDING_RETURN_IDENTIFIER: ClassVar[str] = "cm"

    platform_id: str = Field(..., description="Platform-specific community identifier.")
    description: str = Field(..., description="Description of the community.")

    def get_save_params(self) -> dict[str, Any]:
        """
        Get parameters for saving this community to the database.

        Extends the base implementation to include community-specific parameters
        like platform_id and description.

        Returns:
            Dictionary of parameters for the save query
        """
        params = super().get_save_params()
        params["platform_id"] = self.platform_id
        params["description"] = self.description
        return params


# --- Entity Models ---
class Entity(OrganonNode):
    """
    Represents a named entity in the Organon system.

    The Entity node represents a real-world entity that is mentioned or discussed
    in messages, such as a person, organization, product, or location. Entities
    help track references to important objects across conversations.

    Entities can be connected to:
    - Messages via MENTIONED_IN relationships (references)
    - Topics via RELATED_TO relationships (categorization)
    - Users via RELATED_TO relationships (association)

    Class Variables:
        NODE_LABEL: "Entity" - The Neo4j label for this node type
        FETCH_QUERY: Query to fetch a single entity by UUID
        FETCH_MULTI_QUERY: Query to fetch multiple entities by UUIDs
        CREATE_QUERY: Query to create or update an entity
        HAS_EMBEDDING: True - Entities support vector embeddings for similarity search
        EMBEDDING_RETURN_IDENTIFIER: "e" - Identifier used in embedding queries

    Attributes:
        uuid: Globally unique identifier for the entity
        name: Display name of the entity
        platform: The platform this entity was identified on (e.g., TELEGRAM, DISCORD)
        entity_type: The type of entity (e.g., "PERSON", "ORGANIZATION", "PRODUCT")
        description: Optional text description of the entity
        embedding: Optional vector embedding for semantic search
        created_at: Timestamp when the entity was first created
        updated_at: Timestamp when the entity was last updated

    Example:
        ```python
        # Create a new entity
        entity = Entity(
            name="Python",
            platform=PlatformType.GLOBAL,
            entity_type="TECHNOLOGY",
            description="The Python programming language"
        )

        # Generate and set embedding
        entity.embedding = await entity.embed_content(entity.name + " " + entity.description)

        # Save to database
        query, params = await entity.save()
        await session.run(query, params)
        ```
    """

    NODE_LABEL: ClassVar[str] = "Entity"
    FETCH_QUERY: ClassVar[str] = FETCH_ENTITY_NODE_QUERY
    FETCH_MULTI_QUERY: ClassVar[str] = FETCH_ENTITIES_NODE_QUERY
    CREATE_QUERY: ClassVar[str] = CREATE_ENTITY_NODE_QUERY
    HAS_EMBEDDING: ClassVar[bool] = True
    EMBEDDING_RETURN_IDENTIFIER: ClassVar[str] = "e"

    entity_type: str = Field(..., description="Type of entity.")
    description: str | None = Field(None, description="Description of the entity.")
    embedding: list[float] | None = Field(
        None, description="Vector embedding for semantic search."
    )

    def get_save_params(self) -> dict[str, Any]:
        """
        Get parameters for saving this entity to the database.

        Extends the base implementation to include entity-specific parameters
        like entity_type, description, and embedding.

        Returns:
            Dictionary of parameters for the save query
        """
        params = super().get_save_params()
        params["entity_type"] = self.entity_type
        params["description"] = self.description
        if self.embedding:
            params["embedding"] = self.embedding
        return params


class Topic(OrganonNode):
    """
    Represents a topic or subject matter in the Organon system.

    The Topic node represents a subject, theme, or concept that is discussed
    across messages, rooms, and communities. Topics help organize content
    semantically and enable cross-cutting views of conversations.

    Topics can be connected to:
    - Messages via RELATED_TO relationships (subject matter)
    - Rooms via RELATED_TO relationships (focus)
    - Clusters via RELATED_TO relationships (theme)
    - Users via RELATED_TO relationships (interest)
    - Entities via RELATED_TO relationships (association)

    Class Variables:
        NODE_LABEL: "Topic" - The Neo4j label for this node type
        FETCH_QUERY: Query to fetch a single topic by UUID
        FETCH_MULTI_QUERY: Query to fetch multiple topics by UUIDs
        CREATE_QUERY: Query to create or update a topic
        HAS_EMBEDDING: True - Topics support vector embeddings for similarity search
        EMBEDDING_RETURN_IDENTIFIER: "t" - Identifier used in embedding queries

    Attributes:
        uuid: Globally unique identifier for the topic
        name: Display name of the topic
        platform: The platform this topic was identified on (e.g., TELEGRAM, DISCORD)
        description: Text description of the topic
        embedding: Vector embedding for semantic search and similarity
        created_at: Timestamp when the topic was first created
        updated_at: Timestamp when the topic was last updated

    Example:
        ```python
        # Create a new topic
        topic = Topic(
            name="Async Programming",
            platform=PlatformType.GLOBAL,
            description="Asynchronous programming patterns and techniques"
        )

        # Generate and set embedding
        topic.embedding = await topic.embed_content(topic.name + " " + topic.description)

        # Save to database
        query, params = await topic.save()
        await session.run(query, params)
        ```
    """

    NODE_LABEL: ClassVar[str] = "Topic"
    FETCH_QUERY: ClassVar[str] = FETCH_TOPIC_NODE_QUERY
    FETCH_MULTI_QUERY: ClassVar[str] = FETCH_TOPICS_NODE_QUERY
    CREATE_QUERY: ClassVar[str] = CREATE_TOPIC_NODE_QUERY
    HAS_EMBEDDING: ClassVar[bool] = True
    EMBEDDING_RETURN_IDENTIFIER: ClassVar[str] = "t"

    description: str = Field(..., description="Description of the topic.")
    embedding: list[float] | None = Field(
        None, description="Vector embedding for semantic search."
    )

    def get_save_params(self) -> dict[str, Any]:
        """
        Get parameters for saving this topic to the database.

        Extends the base implementation to include topic-specific parameters
        like description and embedding.

        Returns:
            Dictionary of parameters for the save query
        """
        params = super().get_save_params()
        params["description"] = self.description
        if self.embedding:
            params["embedding"] = self.embedding
        return params


class Preference(OrganonNode):
    """
    Represents a user preference or setting in the Organon system.

    The Preference node represents a user's preference, setting, or configuration
    option. It can be used to store personalization data, feature flags, or
    any other user-specific settings.

    Preferences can be connected to:
    - Users via HAS_PREFERENCE relationships (ownership)
    - Topics via FOR relationships (subject)

    Class Variables:
        NODE_LABEL: "Preference" - The Neo4j label for this node type
        FETCH_QUERY: Query to fetch a single preference by UUID
        FETCH_MULTI_QUERY: Query to fetch multiple preferences by UUIDs
        CREATE_QUERY: Query to create or update a preference
        HAS_EMBEDDING: False - Preferences typically don't have embeddings
        EMBEDDING_RETURN_IDENTIFIER: "p" - Identifier used in embedding queries

    Attributes:
        uuid: Globally unique identifier for the preference
        name: Name of the preference setting
        platform: The platform this preference applies to (e.g., TELEGRAM, DISCORD)
        preference_type: The type of preference (e.g., "NOTIFICATION", "PRIVACY")
        value: The value of the preference, stored as a string
        created_at: Timestamp when the preference was first created
        updated_at: Timestamp when the preference was last updated

    Example:
        ```python
        # Create a new preference
        preference = Preference(
            name="daily_digest",
            platform=PlatformType.GLOBAL,
            preference_type="NOTIFICATION",
            value="enabled"
        )

        # Save to database
        query, params = await preference.save()
        await session.run(query, params)
        ```
    """

    NODE_LABEL: ClassVar[str] = "Preference"
    FETCH_QUERY: ClassVar[str] = FETCH_PREFERENCE_NODE_QUERY
    FETCH_MULTI_QUERY: ClassVar[str] = FETCH_PREFERENCES_NODE_QUERY
    CREATE_QUERY: ClassVar[str] = CREATE_PREFERENCE_NODE_QUERY
    HAS_EMBEDDING: ClassVar[bool] = False
    EMBEDDING_RETURN_IDENTIFIER: ClassVar[str] = "p"

    preference_type: str = Field(..., description="Type of preference.")
    value: str = Field(..., description="Value of the preference.")

    def get_save_params(self) -> dict[str, Any]:
        """
        Get parameters for saving this preference to the database.

        Extends the base implementation to include preference-specific parameters
        like preference_type and value.

        Returns:
            Dictionary of parameters for the save query
        """
        params = super().get_save_params()
        params["preference_type"] = self.preference_type
        params["value"] = self.value
        return params
