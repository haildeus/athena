import datetime
from uuid import uuid4

import pytest

from src.athena.core.organon.operations.organon_edge_op import (
    EDGE_DEFINITIONS,
    generate_edge_query,
)
from src.athena.core.organon.schemas.organon_edges import (
    BelongsTo,
    PostedIn,
    RelatedTo,
)
from src.athena.core.organon.schemas.organon_nodes import (
    Cluster,
    Message,
    PlatformType,
    Room,
    Topic,
    User,
)


# Fixtures for node instances
@pytest.fixture
def user():
    """Create a test user."""
    return User(
        uuid=str(uuid4()),
        name="Test User",
        platform=PlatformType.TELEGRAM,
        user_id="test123",
    )


@pytest.fixture
def room():
    """Create a test room."""
    return Room(
        uuid=str(uuid4()),
        name="Test Room",
        platform=PlatformType.TELEGRAM,
        room_id="room123",
        room_type="group",
    )


@pytest.fixture
def message():
    """Create a test message."""
    return Message(
        uuid=str(uuid4()),
        name="Test Message",
        platform=PlatformType.TELEGRAM,
        message_id="msg123",
        room_id="room123",
        user_id="user123",
        content="Hello world",
    )


@pytest.fixture
def cluster():
    """Create a test cluster."""
    return Cluster(
        uuid=str(uuid4()),
        name="Test Cluster",
        platform=PlatformType.TELEGRAM,
        room_id="room123",
        start_time=datetime.datetime.now(datetime.timezone.utc),
        end_time=datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=1),
        keywords=["test", "cluster"],
        messages=[1, 2, 3],
        embeddings=[0.1, 0.2, 0.3],
    )


@pytest.fixture
def topic():
    """Create a test topic."""
    return Topic(
        uuid=str(uuid4()),
        name="Test Topic",
        platform=PlatformType.TELEGRAM,
        entity_type="topic",
    )


def test_edge_definitions():
    """Test the edge definitions registry."""
    # Check that all expected edges are defined
    assert ("Message", "Room", "POSTED_IN") in EDGE_DEFINITIONS
    assert ("Message", "Cluster", "BELONGS_TO") in EDGE_DEFINITIONS
    assert ("User", "Room", "BELONGS_TO") in EDGE_DEFINITIONS
    assert ("Cluster", "Room", "RELATED_TO") in EDGE_DEFINITIONS

    # Check that an invalid combination is not defined
    assert ("User", "User", "POSTED_IN") not in EDGE_DEFINITIONS


def test_query_generation():
    """Test dynamic query generation."""
    # Test generating a valid query
    query = generate_edge_query("Message", "Room", "POSTED_IN")

    # Query should contain expected patterns
    assert "MATCH (m:Message {uuid: $m_uuid}), (r:Room {uuid: $r_uuid})" in query
    assert "MERGE (m)-[p:POSTED_IN]->(r)" in query
    assert "ON CREATE SET p.created_at = $created_at" in query
    assert "RETURN m, p, r" in query

    # Test with invalid combination
    with pytest.raises(ValueError):
        generate_edge_query("Invalid", "Room", "POSTED_IN")


def test_connect_posted_in(message, room, user):
    """Test connecting nodes with a POSTED_IN edge."""
    edge = PostedIn()

    # Test valid connection: message posted in room
    query, params = edge.connect(message, room)

    # Check query
    assert "MATCH (m:Message {uuid: $m_uuid}), (r:Room {uuid: $r_uuid})" in query
    assert "MERGE (m)-[p:POSTED_IN]->(r)" in query

    # Check params
    assert params["m_uuid"] == message.uuid
    assert params["r_uuid"] == room.uuid
    assert "created_at" in params
    assert "updated_at" in params

    # Test invalid connection
    with pytest.raises(ValueError):
        edge.connect(user, message)  # Invalid combination


def test_connect_belongs_to(message, cluster):
    """Test connecting nodes with a BELONGS_TO edge."""
    edge = BelongsTo()

    # Test valid connection: message belongs to cluster
    query, params = edge.connect(message, cluster)

    # Check query
    assert "MATCH (m:Message {uuid: $m_uuid}), (c:Cluster {uuid: $c_uuid})" in query
    assert "MERGE (m)-[b:BELONGS_TO]->(c)" in query

    # Check params
    assert params["m_uuid"] == message.uuid
    assert params["c_uuid"] == cluster.uuid


def test_connect_related_to(cluster, topic):
    """Test connecting nodes with a RELATED_TO edge."""
    edge = RelatedTo()

    # Test valid connection: cluster related to topic
    query, params = edge.connect(cluster, topic)

    # Check query
    assert "MATCH (c:Cluster {uuid: $c_uuid}), (t:Entity {uuid: $t_uuid})" in query
    assert "MERGE (c)-[r:RELATED_TO]->(t)" in query

    # Check params
    assert params["c_uuid"] == cluster.uuid
    assert params["t_uuid"] == topic.uuid


def test_connect_with_validity_period(user, topic):
    """Test connecting nodes with validity period."""
    # Create edge with validity period
    now = datetime.datetime.now(datetime.timezone.utc)
    future = now + datetime.timedelta(days=30)

    edge = RelatedTo(
        valid_from=now,
        valid_to=future,
    )

    # Connect with validity period
    query, params = edge.connect(user, topic)

    # Check that validity params are included
    assert "valid_from" in params
    assert "valid_to" in params
    assert params["valid_from"] == now.isoformat()
    assert params["valid_to"] == future.isoformat()


# Parametrized test for different edge types and node combinations
@pytest.mark.parametrize(
    "edge_class,source_node_fixture,target_node_fixture,expected_rel_type",
    [
        (PostedIn, "message", "room", "POSTED_IN"),
        (BelongsTo, "message", "cluster", "BELONGS_TO"),
        (RelatedTo, "cluster", "topic", "RELATED_TO"),
        (RelatedTo, "user", "topic", "RELATED_TO"),
    ],
)
def test_edge_types(
    edge_class, source_node_fixture, target_node_fixture, expected_rel_type, request
):
    """Test various edge types with different node combinations."""
    # Get the node instances from fixtures using request.getfixturevalue
    source_node = request.getfixturevalue(source_node_fixture)
    target_node = request.getfixturevalue(target_node_fixture)

    # Create edge instance
    edge = edge_class()

    # Connect nodes
    query, params = edge.connect(source_node, target_node)

    # Verify relationship type in query
    assert (
        f"MERGE ({source_node_fixture[0]})-[{expected_rel_type[0].lower()}:{expected_rel_type}]->({target_node_fixture[0]})"
        in query
    )
    assert f"{source_node_fixture[0]}_uuid" in params
    assert f"{target_node_fixture[0]}_uuid" in params
