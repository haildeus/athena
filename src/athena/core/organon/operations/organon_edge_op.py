"""
Organon Edge Operations Module

This module provides a data-driven system for generating and managing Neo4j Cypher queries
for edge (relationship) operations in the Organon graph database. It uses a registry-based
approach to define valid edge types between node types, reducing code duplication and
making the system more maintainable.

The module defines:
1. Edge relationship types as a Literal type
2. A registry of valid edge definitions with their metadata
3. Functions to dynamically generate Cypher queries for edge operations

This approach allows for a flexible, type-safe way to define and enforce valid
relationships between different node types in the graph database.
"""

from typing import Literal, NamedTuple

# Define edge relationship types
EdgeType = Literal[
    "POSTED_IN",
    "BELONGS_TO",
    "RELATED_TO",
    "MENTIONS",
    "INCLUDES",
    "PARTICIPATES_IN",
    "HAS_PREFERENCE",
    "FOR",
    "EXPRESSES",
]
"""
Literal type defining all valid relationship types in the Organon graph.

Each relationship type represents a specific semantic connection between nodes:
- POSTED_IN: A message or user posted in a room
- BELONGS_TO: A message belongs to a cluster, or a user belongs to a room
- RELATED_TO: A node is related to another node (topic, entity, etc.)
- MENTIONS: A message mentions a user, entity, or topic
- INCLUDES: A container node includes other nodes
- PARTICIPATES_IN: A user participates in a room or event
- HAS_PREFERENCE: A user has a specific preference
- FOR: A node is intended for another node
- EXPRESSES: A node expresses a sentiment or opinion
"""


# Define a structure to hold edge type metadata
class EdgeDefinition(NamedTuple):
    """
    Data structure defining the metadata for a valid edge type between two node types.

    This class encapsulates all the information needed to validate and generate
    Cypher queries for a specific relationship between two node types.

    Attributes:
        from_node_label: The label of the source node (e.g., "User")
        to_node_label: The label of the target node (e.g., "Room")
        relationship_type: The type of relationship (e.g., "POSTED_IN")
        extra_props: Optional dictionary of extra properties to set on the relationship
                    with their Cypher expressions for values
    """

    from_node_label: str
    to_node_label: str
    relationship_type: EdgeType
    extra_props: dict[str, str] | None = None


# Registry of allowed edge definitions
EDGE_DEFINITIONS = {
    # Message edges
    ("Message", "Room", "POSTED_IN"): EdgeDefinition("Message", "Room", "POSTED_IN"),
    ("Message", "Cluster", "BELONGS_TO"): EdgeDefinition(
        "Message", "Cluster", "BELONGS_TO"
    ),
    # User edges
    ("User", "Room", "BELONGS_TO"): EdgeDefinition("User", "Room", "BELONGS_TO"),
    ("User", "Room", "POSTED_IN"): EdgeDefinition(
        "User", "Room", "POSTED_IN", {"count": "coalesce(p.count, 0) + 1"}
    ),
    ("User", "Topic", "RELATED_TO"): EdgeDefinition("User", "Topic", "RELATED_TO"),
    # Cluster edges
    ("Cluster", "Room", "RELATED_TO"): EdgeDefinition("Cluster", "Room", "RELATED_TO"),
    ("Cluster", "Topic", "RELATED_TO"): EdgeDefinition(
        "Cluster", "Topic", "RELATED_TO"
    ),
    # Room edges
    ("Room", "Topic", "RELATED_TO"): EdgeDefinition("Room", "Topic", "RELATED_TO"),
}
"""
Registry of all valid edge definitions in the Organon graph.

This dictionary maps tuples of (source_node_type, target_node_type, relationship_type)
to EdgeDefinition objects that contain metadata about the relationship.

The registry serves as both documentation of valid relationships and as a
runtime validation mechanism to ensure only valid relationships can be created.

Examples of valid relationships:
- (Message, Room, POSTED_IN): A message was posted in a room
- (User, Room, BELONGS_TO): A user belongs to a room
- (Cluster, Topic, RELATED_TO): A message cluster is related to a topic
"""


def generate_edge_query(
    from_node_label: str, to_node_label: str, relationship_type: EdgeType
) -> str:
    """
    Generate a Cypher query for creating an edge between two nodes.

    This function dynamically generates a Neo4j Cypher query to create or update
    a relationship between two nodes. It uses the EDGE_DEFINITIONS registry to
    validate that the relationship is allowed and to get any special properties
    that should be set on the relationship.

    The generated query:
    1. Matches the source and target nodes by their UUIDs
    2. Creates or updates the relationship with the specified type
    3. Sets created_at and updated_at timestamps
    4. Sets any additional properties defined for this relationship type
    5. Returns the source node, relationship, and target node

    Args:
        from_node_label: The label of the source node (e.g., "User")
        to_node_label: The label of the target node (e.g., "Room")
        relationship_type: The type of relationship to create (e.g., "POSTED_IN")

    Returns:
        A parameterized Cypher query string ready to be executed with parameters

    Raises:
        ValueError: If the edge definition is not registered in EDGE_DEFINITIONS

    Example:
        >>> query = generate_edge_query("User", "Room", "POSTED_IN")
        >>> # The query will look like:
        >>> # MATCH (u:User {uuid: $u_uuid}), (r:Room {uuid: $r_uuid})
        >>> # MERGE (u)-[p:POSTED_IN]->(r)
        >>> # ON CREATE SET p.created_at = $created_at, p.updated_at = $updated_at, p.count = 1
        >>> # ON MATCH SET p.updated_at = $updated_at, p.count = coalesce(p.count, 0) + 1
        >>> # RETURN u, p, r
    """
    key = (from_node_label, to_node_label, relationship_type)
    if key not in EDGE_DEFINITIONS:
        raise ValueError(f"Unsupported edge definition: {key}")

    edge_def = EDGE_DEFINITIONS[key]

    # Create node identifiers (first lowercase letter of each label)
    from_id = from_node_label[0].lower()
    to_id = to_node_label[0].lower()
    rel_id = relationship_type[0].lower()

    # Build base query
    query = f"""
    MATCH ({from_id}:{from_node_label} {{uuid: ${from_id}_uuid}}), ({to_id}:{to_node_label} {{uuid: ${to_id}_uuid}})
    MERGE ({from_id})-[{rel_id}:{relationship_type}]->({to_id})
    ON CREATE SET {rel_id}.created_at = $created_at, {rel_id}.updated_at = $updated_at
    ON MATCH SET {rel_id}.updated_at = $updated_at
    """

    # Add any extra properties
    if edge_def.extra_props:
        extra_props = []
        for prop_name, prop_value in edge_def.extra_props.items():
            extra_props.append(f"{rel_id}.{prop_name} = {prop_value}")

        if extra_props:
            extra_props_str = ", ".join(extra_props)
            query = query.replace(
                "ON MATCH SET {rel_id}.updated_at = $updated_at",
                f"ON MATCH SET {rel_id}.updated_at = $updated_at, {extra_props_str}",
            )

    # Add return statement
    query += f"RETURN {from_id}, {rel_id}, {to_id}"

    return query


# --- Query generation functions for all edge types ---
def get_edge_query(
    from_node_label: str, to_node_label: str, relationship_type: EdgeType
) -> str:
    """
    Get the appropriate edge query for the given node labels and relationship type.

    This is a convenience wrapper around generate_edge_query that provides a simpler
    interface for getting edge queries. It's the main entry point for code that needs
    to generate edge queries.

    Args:
        from_node_label: The label of the source node (e.g., "User")
        to_node_label: The label of the target node (e.g., "Room")
        relationship_type: The type of relationship to create (e.g., "POSTED_IN")

    Returns:
        A parameterized Cypher query string ready to be executed with parameters

    Raises:
        ValueError: If the edge definition is not registered in EDGE_DEFINITIONS
    """
    return generate_edge_query(from_node_label, to_node_label, relationship_type)


# For backward compatibility, define the previously hardcoded queries
CREATE_MESSAGE_POSTED_IN_ROOM_QUERY = get_edge_query("Message", "Room", "POSTED_IN")
"""Cypher query for creating a POSTED_IN relationship from a Message to a Room."""

CREATE_MESSAGE_BELONGS_TO_CLUSTER_QUERY = get_edge_query(
    "Message", "Cluster", "BELONGS_TO"
)
"""Cypher query for creating a BELONGS_TO relationship from a Message to a Cluster."""

CREATE_USER_BELONGS_TO_ROOM_QUERY = get_edge_query("User", "Room", "BELONGS_TO")
"""Cypher query for creating a BELONGS_TO relationship from a User to a Room."""

CREATE_USER_POSTED_IN_ROOM_QUERY = get_edge_query("User", "Room", "POSTED_IN")
"""Cypher query for creating a POSTED_IN relationship from a User to a Room."""

CREATE_CLUSTER_RELATED_TO_ROOM_QUERY = get_edge_query("Cluster", "Room", "RELATED_TO")
"""Cypher query for creating a RELATED_TO relationship from a Cluster to a Room."""

CREATE_CLUSTER_RELATED_TO_TOPIC_QUERY = get_edge_query("Cluster", "Topic", "RELATED_TO")
"""Cypher query for creating a RELATED_TO relationship from a Cluster to a Topic."""

CREATE_USER_RELATED_TO_TOPIC_QUERY = get_edge_query("User", "Topic", "RELATED_TO")
"""Cypher query for creating a RELATED_TO relationship from a User to a Topic."""

CREATE_ROOM_RELATED_TO_TOPIC_QUERY = get_edge_query("Room", "Topic", "RELATED_TO")
"""Cypher query for creating a RELATED_TO relationship from a Room to a Topic."""
