"""
Organon Node Operations Module

This module provides a data-driven system for generating and managing Neo4j Cypher queries
for node operations in the Organon graph database. It uses a registry-based approach
to define node types and generate CRUD queries, reducing code duplication and
making the system more maintainable.

The module defines:
1. A NodeDefinition class to represent node types with their properties
2. A registry of node definitions with their metadata
3. Functions to dynamically generate Cypher queries for node operations

This approach allows for a flexible, type-safe way to define and enforce node properties
in the graph database.
"""

from typing import Literal, NamedTuple

# Define node types
NodeType = Literal[
    "User",
    "Room",
    "Message",
    "Cluster",
    "Community",
    "Entity",
    "Topic",
    "Preference",
]
"""
Literal type defining all valid node types in the Organon graph.

Each node type represents a specific entity in the graph database:
- User: A user in the system
- Room: A chat room or conversation space
- Message: An individual message sent by a user
- Cluster: A group of related messages
- Community: A group of related rooms
- Entity: A named entity mentioned in messages
- Topic: A subject or theme discussed in messages
- Preference: A user preference or setting
"""


class NodeProperty(NamedTuple):
    """
    Data structure defining a property of a node.

    Attributes:
        name: The name of the property
        required: Whether the property is required (always included in queries)
        default: Optional default value expression in Cypher
    """

    name: str
    required: bool = True
    default: str | None = None


class NodeDefinition(NamedTuple):
    """
    Data structure defining the metadata for a node type.

    This class encapsulates all the information needed to generate
    Cypher queries for a specific node type.

    Attributes:
        node_type: The type of node (e.g., "User")
        node_identifier: The identifier used in Cypher queries (e.g., "u")
        properties: List of properties for this node type
    """

    node_type: NodeType
    node_identifier: str
    properties: list[NodeProperty]


# Common properties for all node types
COMMON_PROPERTIES = [
    NodeProperty("uuid"),
    NodeProperty("name"),
    NodeProperty("platform"),
    NodeProperty("created_at"),
    NodeProperty("updated_at"),
]


# Registry of node definitions
NODE_DEFINITIONS = {
    "User": NodeDefinition(
        node_type="User",
        node_identifier="u",
        properties=COMMON_PROPERTIES
        + [
            NodeProperty("user_id"),
            NodeProperty("platform_handles"),
            NodeProperty("summary", required=False),
            NodeProperty("classification", required=False),
            NodeProperty("last_summary_update", required=False),
        ],
    ),
    "Room": NodeDefinition(
        node_type="Room",
        node_identifier="r",
        properties=COMMON_PROPERTIES
        + [
            NodeProperty("room_id"),
            NodeProperty("room_type"),
            NodeProperty("community_id", required=False),
            NodeProperty("summary", required=False),
        ],
    ),
    "Message": NodeDefinition(
        node_type="Message",
        node_identifier="m",
        properties=COMMON_PROPERTIES
        + [
            NodeProperty("message_id"),
            NodeProperty("room_id"),
            NodeProperty("user_id"),
            NodeProperty("content"),
            NodeProperty("engagement_score", required=False),
            NodeProperty("embedding", required=False),
        ],
    ),
    "Cluster": NodeDefinition(
        node_type="Cluster",
        node_identifier="c",
        properties=COMMON_PROPERTIES
        + [
            NodeProperty("room_id"),
            NodeProperty("start_time"),
            NodeProperty("end_time"),
            NodeProperty("keywords"),
            NodeProperty("messages"),
            NodeProperty("embeddings", required=False),
        ],
    ),
    "Community": NodeDefinition(
        node_type="Community",
        node_identifier="c",
        properties=COMMON_PROPERTIES
        + [
            NodeProperty("community_id"),
            NodeProperty("description"),
        ],
    ),
    "Entity": NodeDefinition(
        node_type="Entity",
        node_identifier="e",
        properties=COMMON_PROPERTIES
        + [
            NodeProperty("entity_type"),
            NodeProperty("embedding", required=False),
        ],
    ),
    "Topic": NodeDefinition(
        node_type="Topic",
        node_identifier="t",
        properties=COMMON_PROPERTIES
        + [
            NodeProperty("description"),
            NodeProperty("embedding", required=False),
        ],
    ),
    "Preference": NodeDefinition(
        node_type="Preference",
        node_identifier="p",
        properties=COMMON_PROPERTIES
        + [
            NodeProperty("preference_id"),
            NodeProperty("preference_type"),
            NodeProperty("description"),
            NodeProperty("embedding", required=False),
        ],
    ),
}
"""
Registry of all node definitions in the Organon graph.

This dictionary maps node types to NodeDefinition objects that contain
metadata about the node, including its properties and identifiers.

The registry serves as both documentation of node types and as a
runtime mechanism to generate Cypher queries for node operations.
"""


def generate_create_node_query(node_type: NodeType) -> str:
    """
    Generate a Cypher query for creating or updating a node.

    This function dynamically generates a Neo4j Cypher query based on the
    node definition in the NODE_DEFINITIONS registry. The generated query
    uses MERGE to create or update a node with the specified properties.

    Args:
        node_type: The type of node to create (e.g., "User")

    Returns:
        A parameterized Cypher query string ready to be executed with parameters

    Raises:
        ValueError: If the node type is not registered in NODE_DEFINITIONS
    """
    if node_type not in NODE_DEFINITIONS:
        raise ValueError(f"Unsupported node type: {node_type}")

    node_def = NODE_DEFINITIONS[node_type]
    identifier = node_def.node_identifier

    # Build property assignments for CREATE and MATCH operations
    create_props = []
    match_props = []

    for prop in node_def.properties:
        if prop.required:
            create_props.append(f"{prop.name}: ${prop.name}")
            match_props.append(f"{prop.name}: ${prop.name}")
        else:
            # Optional properties use a different pattern
            create_props.append(f"{prop.name}: ${prop.name}")
            match_props.append(f"{prop.name}: ${prop.name}")

    create_props_str = ", ".join(create_props)
    match_props_str = ", ".join(match_props)

    # Build the query
    query = f"""
MERGE ({identifier}:{node_type} {{uuid: $uuid}})
ON CREATE SET {identifier} = {{
    {create_props_str}
}}
ON MATCH SET {identifier} += {{
    {match_props_str}
}}
RETURN {identifier}
"""

    return query


def generate_fetch_node_query(node_type: NodeType) -> str:
    """
    Generate a Cypher query for fetching a node by UUID.

    Args:
        node_type: The type of node to fetch (e.g., "User")

    Returns:
        A parameterized Cypher query string ready to be executed with parameters

    Raises:
        ValueError: If the node type is not registered in NODE_DEFINITIONS
    """
    if node_type not in NODE_DEFINITIONS:
        raise ValueError(f"Unsupported node type: {node_type}")

    node_def = NODE_DEFINITIONS[node_type]
    identifier = node_def.node_identifier

    query = f"""
MATCH ({identifier}:{node_type} {{uuid: $uuid}})
RETURN {identifier}
"""

    return query


def generate_fetch_nodes_query(node_type: NodeType) -> str:
    """
    Generate a Cypher query for fetching multiple nodes by UUIDs.

    Args:
        node_type: The type of nodes to fetch (e.g., "User")

    Returns:
        A parameterized Cypher query string ready to be executed with parameters

    Raises:
        ValueError: If the node type is not registered in NODE_DEFINITIONS
    """
    if node_type not in NODE_DEFINITIONS:
        raise ValueError(f"Unsupported node type: {node_type}")

    node_def = NODE_DEFINITIONS[node_type]
    identifier = node_def.node_identifier

    query = f"""
MATCH ({identifier}:{node_type})
WHERE {identifier}.uuid IN $uuids
RETURN {identifier}
"""

    return query


# --- Create Queries ---
CREATE_USER_NODE_QUERY = generate_create_node_query("User")
CREATE_ROOM_NODE_QUERY = generate_create_node_query("Room")
CREATE_MESSAGE_NODE_QUERY = generate_create_node_query("Message")
CREATE_CLUSTER_NODE_QUERY = generate_create_node_query("Cluster")
CREATE_COMMUNITY_NODE_QUERY = generate_create_node_query("Community")
CREATE_ENTITY_NODE_QUERY = generate_create_node_query("Entity")
CREATE_TOPIC_NODE_QUERY = generate_create_node_query("Topic")
CREATE_PREFERENCE_NODE_QUERY = generate_create_node_query("Preference")

# --- Fetch Queries ---
FETCH_USER_NODE_QUERY = generate_fetch_node_query("User")
FETCH_ROOM_NODE_QUERY = generate_fetch_node_query("Room")
FETCH_MESSAGE_NODE_QUERY = generate_fetch_node_query("Message")
FETCH_CLUSTER_NODE_QUERY = generate_fetch_node_query("Cluster")
FETCH_COMMUNITY_NODE_QUERY = generate_fetch_node_query("Community")
FETCH_ENTITY_NODE_QUERY = generate_fetch_node_query("Entity")
FETCH_TOPIC_NODE_QUERY = generate_fetch_node_query("Topic")
FETCH_PREFERENCE_NODE_QUERY = generate_fetch_node_query("Preference")

# --- Fetch Multiple Queries ---
FETCH_USERS_NODE_QUERY = generate_fetch_nodes_query("User")
FETCH_ROOMS_NODE_QUERY = generate_fetch_nodes_query("Room")
FETCH_MESSAGES_NODE_QUERY = generate_fetch_nodes_query("Message")
FETCH_CLUSTERS_NODE_QUERY = generate_fetch_nodes_query("Cluster")
FETCH_COMMUNITIES_NODE_QUERY = generate_fetch_nodes_query("Community")
FETCH_ENTITIES_NODE_QUERY = generate_fetch_nodes_query("Entity")
FETCH_TOPICS_NODE_QUERY = generate_fetch_nodes_query("Topic")
FETCH_PREFERENCES_NODE_QUERY = generate_fetch_nodes_query("Preference")


# Main entry point for getting node creation queries
def get_create_node_query(node_type: NodeType) -> str:
    """
    Get the appropriate node creation query for the given node type.

    This is a convenience wrapper around generate_create_node_query that
    provides a simpler interface for getting node creation queries.

    Args:
        node_type: The type of node to create (e.g., "User")

    Returns:
        A parameterized Cypher query string ready to be executed with parameters

    Raises:
        ValueError: If the node type is not registered in NODE_DEFINITIONS
    """
    return generate_create_node_query(node_type)


# Main entry point for getting node fetch queries
def get_fetch_node_query(node_type: NodeType) -> str:
    """
    Get the appropriate node fetch query for the given node type.

    This is a convenience wrapper around generate_fetch_node_query that
    provides a simpler interface for getting node fetch queries.

    Args:
        node_type: The type of node to fetch (e.g., "User")

    Returns:
        A parameterized Cypher query string ready to be executed with parameters

    Raises:
        ValueError: If the node type is not registered in NODE_DEFINITIONS
    """
    return generate_fetch_node_query(node_type)


# Main entry point for getting multi-node fetch queries
def get_fetch_nodes_query(node_type: NodeType) -> str:
    """
    Get the appropriate multi-node fetch query for the given node type.

    This is a convenience wrapper around generate_fetch_nodes_query that
    provides a simpler interface for getting multi-node fetch queries.

    Args:
        node_type: The type of nodes to fetch (e.g., "User")

    Returns:
        A parameterized Cypher query string ready to be executed with parameters

    Raises:
        ValueError: If the node type is not registered in NODE_DEFINITIONS
    """
    return generate_fetch_nodes_query(node_type)
