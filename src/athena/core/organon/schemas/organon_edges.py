"""
Organon Edges Module

This module defines the edge (relationship) classes for the Organon graph database system.
It provides a structured, object-oriented approach to creating and managing relationships
between nodes in the Neo4j graph database.

The module implements:
1. A base OrganonEdge class that handles common edge operations
2. Specialized edge classes for different relationship types
3. Methods for creating, retrieving, and managing edges in the database

The edge system works in conjunction with the organon_edge_op module, which provides
the underlying Cypher query generation for edge operations.
"""

import datetime
from typing import Any, ClassVar, TypeVar

from pydantic import BaseModel, Field

from ..operations.organon_edge_op import (
    EDGE_DEFINITIONS,
    EdgeType,
    get_edge_query,
)
from .organon_nodes import OrganonNode

# Type variable for self-referencing
E = TypeVar("E", bound="OrganonEdge")


class OrganonEdge(BaseModel):
    """
    Base class for all edge (relationship) types in the Organon graph database.

    This class provides the common structure and functionality for creating and
    managing relationships between nodes in the Neo4j graph database. It works with
    the query generation functions from organon_edge_op to execute the appropriate
    Cypher queries.

    Class Variables:
        RELATIONSHIP_TYPE: The type of relationship this edge represents (e.g., "POSTED_IN")
        FROM_NODE_CLASS: The class of the source node
        TO_NODE_CLASS: The class of the target node

    Attributes:
        from_node: The source node of the relationship
        to_node: The target node of the relationship
        created_at: Timestamp when the relationship was created
        updated_at: Timestamp when the relationship was last updated
    """

    # Class variables to be defined by subclasses
    RELATIONSHIP_TYPE: ClassVar[EdgeType]
    FROM_NODE_CLASS: ClassVar[type[OrganonNode]]
    TO_NODE_CLASS: ClassVar[type[OrganonNode]]

    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="Timestamp when the relationship was created.",
    )
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="Timestamp when the relationship was last updated.",
    )
    valid_from: datetime.datetime | None = Field(
        None, description="Start of relationship validity."
    )
    valid_to: datetime.datetime | None = Field(
        None, description="End of relationship validity."
    )

    def connect(
        self, source_node: OrganonNode, target_node: OrganonNode
    ) -> tuple[str, dict[str, Any]]:
        """
        Connect two nodes with this edge type and prepare the query for execution.

        This method validates that the provided nodes can be connected with this edge type
        by checking against the EDGE_DEFINITIONS registry. It then generates the appropriate
        Cypher query and parameters to create the relationship in the Neo4j database.

        The method does not execute the query itself but returns the query and parameters
        ready for execution, allowing for transaction management by the caller.

        Args:
            source_node: The source node of the relationship
            target_node: The target node of the relationship

        Returns:
            A tuple containing:
                - The Cypher query string to execute
                - A dictionary of parameters for the query

        Raises:
            ValueError: If the combination of source node type, target node type, and
                       relationship type is not registered in EDGE_DEFINITIONS

        Example:
            ```python
            edge = PostedIn()
            query, params = edge.connect(message, room)
            await session.run(query, params)
            ```
        """
        # Get the node type names
        source_type = source_node.__class__.__name__
        target_type = target_node.__class__.__name__

        # Check if this edge type supports this node pair
        key = (source_type, target_type, self.__class__.RELATIONSHIP_TYPE)
        if key not in EDGE_DEFINITIONS:
            raise ValueError(
                f"Invalid nodes for edge: {source_type} -> {self.__class__.RELATIONSHIP_TYPE} -> {target_type}"
            )

        # Get the query
        query = get_edge_query(
            source_type, target_type, self.__class__.RELATIONSHIP_TYPE
        )

        # Prepare parameters
        params = {
            f"{source_type[0].lower()}_uuid": source_node.uuid,
            f"{target_type[0].lower()}_uuid": target_node.uuid,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

        # Add optional validity parameters if present
        if self.valid_from:
            params["valid_from"] = self.valid_from.isoformat()
        if self.valid_to:
            params["valid_to"] = self.valid_to.isoformat()

        return query, params


# --- Concrete Edge Classes ---
class PostedIn(OrganonEdge):
    """
    Represents a POSTED_IN relationship from a node to another node.

    This edge indicates that the source node has posted content in the target node,
    establishing a content creation relationship. Typically used to connect:
    - Message -> Room: A message was posted in a room
    - User -> Room: A user posted content in a room

    The POSTED_IN relationship may include additional metadata such as:
    - count: Number of times the user has posted in the room
    - last_posted: Timestamp of the last post

    This relationship is crucial for content discovery and attribution in the graph.

    Example:
        ```python
        # Create a relationship between a message and a room
        message = Message(...)
        room = Room(...)
        edge = PostedIn()
        query, params = edge.connect(message, room)
        await session.run(query, params)
        ```
    """

    RELATIONSHIP_TYPE: ClassVar[EdgeType] = "POSTED_IN"
    FROM_NODE_CLASS: ClassVar[type[OrganonNode]] = None
    TO_NODE_CLASS: ClassVar[type[OrganonNode]] = None


class BelongsTo(OrganonEdge):
    """
    Represents a BELONGS_TO relationship from a node to another node.

    This edge indicates a membership or categorization relationship, where the source
    node is a member of or categorized under the target node. Typically used to connect:
    - Message -> Cluster: A message belongs to a message cluster
    - User -> Room: A user is a member of a room
    - Entity -> Topic: An entity belongs to a topic category

    The BELONGS_TO relationship establishes hierarchical structures in the graph,
    enabling efficient traversal of related content and membership queries.

    Example:
        ```python
        # Create a relationship between a message and a cluster
        message = Message(...)
        cluster = Cluster(...)
        edge = BelongsTo()
        query, params = edge.connect(message, cluster)
        await session.run(query, params)
        ```
    """

    RELATIONSHIP_TYPE: ClassVar[EdgeType] = "BELONGS_TO"
    FROM_NODE_CLASS: ClassVar[type[OrganonNode]] = None
    TO_NODE_CLASS: ClassVar[type[OrganonNode]] = None


class RelatedTo(OrganonEdge):
    """
    Represents a RELATED_TO relationship from a node to another node.

    This edge indicates a semantic or contextual relationship between nodes,
    without implying membership or containment. Typically used to connect:
    - Cluster -> Room: A message cluster is related to a room
    - Cluster -> Topic: A message cluster is related to a topic
    - User -> Topic: A user is related to a topic (has interest or expertise)
    - Room -> Topic: A room is related to a topic (discussion focus)

    The RELATED_TO relationship enables semantic navigation through the graph,
    connecting entities that share context or relevance without a strict hierarchy.
    It's particularly useful for recommendation systems and content discovery.

    Example:
        ```python
        # Create a relationship between a cluster and a topic
        cluster = Cluster(...)
        topic = Topic(...)
        edge = RelatedTo()
        query, params = edge.connect(cluster, topic)
        await session.run(query, params)
        ```
    """

    RELATIONSHIP_TYPE: ClassVar[EdgeType] = "RELATED_TO"
    FROM_NODE_CLASS: ClassVar[type[OrganonNode]] = None
    TO_NODE_CLASS: ClassVar[type[OrganonNode]] = None


class Mentions(OrganonEdge):
    """
    Represents a MENTIONS relationship from a node to another node.

    This edge indicates that the source node explicitly references or mentions
    the target node in its content. Typically used to connect:
    - Message -> User: A message mentions a user
    - Message -> Topic: A message mentions a topic
    - Message -> Entity: A message mentions an entity

    The MENTIONS relationship is crucial for tracking references and building
    a network of explicit connections between content and the entities it references.
    This enables features like notifications, content tagging, and reference tracking.

    Example:
        ```python
        # Create a relationship between a message and a user it mentions
        message = Message(...)
        user = User(...)
        edge = Mentions()
        query, params = edge.connect(message, user)
        await session.run(query, params)
        ```
    """

    RELATIONSHIP_TYPE: ClassVar[EdgeType] = "MENTIONS"
    FROM_NODE_CLASS: ClassVar[type[OrganonNode]] = None
    TO_NODE_CLASS: ClassVar[type[OrganonNode]] = None


class Includes(OrganonEdge):
    """
    Represents an INCLUDES relationship from a node to another node.

    This edge indicates a containment relationship, where the source node
    contains or encompasses the target node. Typically used to connect:
    - Cluster -> Message: A cluster includes multiple messages
    - Room -> Message: A room includes messages
    - Community -> Room: A community includes multiple rooms

    The INCLUDES relationship is the inverse of BELONGS_TO and establishes
    a top-down view of containment hierarchies in the graph. It's particularly
    useful for traversing from containers to their contents.

    Example:
        ```python
        # Create a relationship between a cluster and a message it includes
        cluster = Cluster(...)
        message = Message(...)
        edge = Includes()
        query, params = edge.connect(cluster, message)
        await session.run(query, params)
        ```
    """

    RELATIONSHIP_TYPE: ClassVar[EdgeType] = "INCLUDES"
    FROM_NODE_CLASS: ClassVar[type[OrganonNode]] = None
    TO_NODE_CLASS: ClassVar[type[OrganonNode]] = None


class ParticipatesIn(OrganonEdge):
    """
    Represents a PARTICIPATES_IN relationship from a node to another node.

    This edge indicates active participation or engagement, where the source node
    actively engages with the target node. Typically used to connect:
    - User -> Room: A user participates in discussions in a room
    - User -> Cluster: A user participates in a conversation cluster
    - User -> Community: A user participates in a community

    Unlike BELONGS_TO which indicates membership, PARTICIPATES_IN implies
    active engagement and interaction. This relationship can include metadata
    about the level of participation, such as frequency or recency.

    Example:
        ```python
        # Create a relationship between a user and a room they participate in
        user = User(...)
        room = Room(...)
        edge = ParticipatesIn()
        query, params = edge.connect(user, room)
        await session.run(query, params)
        ```
    """

    RELATIONSHIP_TYPE: ClassVar[EdgeType] = "PARTICIPATES_IN"
    FROM_NODE_CLASS: ClassVar[type[OrganonNode]] = None
    TO_NODE_CLASS: ClassVar[type[OrganonNode]] = None


class HasPreference(OrganonEdge):
    """
    Represents a HAS_PREFERENCE relationship from a node to another node.

    This edge indicates a preference or affinity that the source node has
    for the target node. Typically used to connect:
    - User -> Topic: A user has a preference for a topic
    - User -> Room: A user has a preference for a room
    - User -> Entity: A user has a preference for an entity

    The HAS_PREFERENCE relationship is essential for personalization systems,
    enabling the graph to represent user preferences and affinities. It often
    includes metadata such as preference strength, explicit vs. implicit, and
    recency.

    Example:
        ```python
        # Create a relationship representing a user's preference for a topic
        user = User(...)
        topic = Topic(...)
        edge = HasPreference()
        query, params = edge.connect(user, topic)
        await session.run(query, params)
        ```
    """

    RELATIONSHIP_TYPE: ClassVar[EdgeType] = "HAS_PREFERENCE"
    FROM_NODE_CLASS: ClassVar[type[OrganonNode]] = None
    TO_NODE_CLASS: ClassVar[type[OrganonNode]] = None


class For(OrganonEdge):
    """
    Represents a FOR relationship from a node to another node.

    This edge indicates that the source node is intended for, targeted at,
    or designed for the target node. Typically used to connect:
    - Message -> User: A message is intended for a specific user
    - Preference -> Topic: A preference setting is for a specific topic
    - Content -> Community: Content is created for a specific community

    The FOR relationship establishes intentionality and targeting in the graph,
    enabling queries that identify content or settings intended for specific
    entities.

    Example:
        ```python
        # Create a relationship showing a message is for a specific user
        message = Message(...)
        user = User(...)
        edge = For()
        query, params = edge.connect(message, user)
        await session.run(query, params)
        ```
    """

    RELATIONSHIP_TYPE: ClassVar[EdgeType] = "FOR"
    FROM_NODE_CLASS: ClassVar[type[OrganonNode]] = None
    TO_NODE_CLASS: ClassVar[type[OrganonNode]] = None


class Expresses(OrganonEdge):
    """
    Represents an EXPRESSES relationship from a node to another node.

    This edge indicates that the source node expresses, conveys, or embodies
    the target node. Typically used to connect:
    - Message -> Topic: A message expresses a topic
    - Message -> Entity: A message expresses an entity concept
    - User -> Preference: A user expresses a preference

    The EXPRESSES relationship captures semantic expression and embodiment,
    enabling the graph to represent what concepts or ideas are expressed by
    content or users. This is particularly useful for content analysis and
    semantic understanding.

    Example:
        ```python
        # Create a relationship showing a message expresses a topic
        message = Message(...)
        topic = Topic(...)
        edge = Expresses()
        query, params = edge.connect(message, topic)
        await session.run(query, params)
        ```
    """

    RELATIONSHIP_TYPE: ClassVar[EdgeType] = "EXPRESSES"
    FROM_NODE_CLASS: ClassVar[type[OrganonNode]] = None
    TO_NODE_CLASS: ClassVar[type[OrganonNode]] = None
