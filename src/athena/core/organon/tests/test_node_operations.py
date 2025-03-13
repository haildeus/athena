import datetime
import uuid
from unittest.mock import patch

import pytest

from src.athena.core.organon.schemas.organon_nodes import (
    Cluster,
    Community,
    Entity,
    Message,
    OrganonNode,
    PlatformType,
    Preference,
    Room,
    Topic,
    User,
)


# Fixtures for common test data
@pytest.fixture
def uuid_str():
    """Generate a UUID string."""
    return str(uuid.uuid4())


@pytest.fixture
def current_time():
    """Get the current time with UTC timezone."""
    return datetime.datetime.now(datetime.timezone.utc)


@pytest.fixture
def user(uuid_str, current_time):
    """Create a test user."""
    return User(
        uuid=uuid_str,
        name="Test User",
        platform=PlatformType.TELEGRAM,
        user_id="user123",
        platform_handles={PlatformType.TELEGRAM: "@test_user"},
        summary="Active user",
        classification="regular",
        last_summary_update=current_time,
    )


@pytest.fixture
def room(uuid_str):
    """Create a test room."""
    return Room(
        uuid=uuid_str,
        name="Test Room",
        platform=PlatformType.DISCORD,
        room_id="room123",
        room_type="group",
        community_id="community123",
        summary="Active discussion group",
    )


@pytest.fixture
def message(uuid_str):
    """Create a test message."""
    return Message(
        uuid=uuid_str,
        name="Test Message",
        platform=PlatformType.TELEGRAM,
        message_id="msg123",
        room_id="room123",
        user_id="user123",
        content="Hello world",
        engagement_score=0.8,
        embedding=[0.1, 0.2, 0.3],
    )


@pytest.fixture
def cluster(uuid_str, current_time):
    """Create a test cluster."""
    return Cluster(
        uuid=uuid_str,
        name="Test Cluster",
        platform=PlatformType.GLOBAL,
        room_id="room123",
        start_time=current_time,
        end_time=current_time + datetime.timedelta(hours=1),
        keywords=["test", "cluster"],
        messages=[1, 2, 3],
        embeddings=[0.1, 0.2, 0.3],
    )


@pytest.fixture
def community(uuid_str):
    """Create a test community."""
    return Community(
        uuid=uuid_str,
        name="Test Community",
        platform=PlatformType.DISCORD,
        community_id="community123",
        description="A test community",
    )


@pytest.fixture
def entity(uuid_str):
    """Create a test entity."""
    return Entity(
        uuid=uuid_str,
        name="Test Entity",
        platform=PlatformType.GLOBAL,
        entity_type="product",
        embedding=[0.4, 0.5, 0.6],
    )


@pytest.fixture
def topic(uuid_str):
    """Create a test topic."""
    return Topic(
        uuid=uuid_str,
        name="Test Topic",
        platform=PlatformType.GLOBAL,
        embedding=[0.7, 0.8, 0.9],
    )


@pytest.fixture
def preference(uuid_str):
    """Create a test preference."""
    return Preference(
        uuid=uuid_str,
        name="Test Preference",
        platform=PlatformType.GLOBAL,
        preference_id="pref123",
        preference_type="like",
        description="A test preference",
        embedding=[0.1, 0.3, 0.5],
    )


# PlatformType tests
@pytest.mark.parametrize(
    "string_input,expected_enum",
    [
        ("global", PlatformType.GLOBAL),
        ("telegram", PlatformType.TELEGRAM),
        ("discord", PlatformType.DISCORD),
        ("twitter", PlatformType.TWITTER),
    ],
)
def test_platform_type_from_string(string_input, expected_enum):
    """Test conversion from string to PlatformType."""
    assert PlatformType.from_string(string_input) == expected_enum


@pytest.mark.parametrize(
    "int_input,expected_enum",
    [
        (1, PlatformType.GLOBAL),
        (2, PlatformType.TELEGRAM),
        (3, PlatformType.DISCORD),
        (4, PlatformType.TWITTER),
    ],
)
def test_platform_type_from_int(int_input, expected_enum):
    """Test conversion from int to PlatformType."""
    assert PlatformType.from_int(int_input) == expected_enum


def test_platform_type_error_cases():
    """Test error cases for PlatformType conversions."""
    with pytest.raises(ValueError):
        PlatformType.from_string("invalid")

    with pytest.raises(ValueError):
        PlatformType.from_string(123)  # type: ignore

    with pytest.raises(ValueError):
        PlatformType.from_int("invalid")  # type: ignore

    with pytest.raises(ValueError):
        PlatformType.from_int(99)


# Node metadata tests
@pytest.mark.parametrize(
    "node_class,expected_label",
    [
        (User, "User"),
        (Room, "Room"),
        (Message, "Message"),
        (Cluster, "Cluster"),
        (Community, "Community"),
        (Entity, "Entity"),
        (Preference, "Preference"),
    ],
)
def test_node_labels(node_class, expected_label):
    """Test that node classes have correct labels."""
    assert node_class.NODE_LABEL == expected_label


@pytest.mark.parametrize(
    "node_class",
    [User, Room, Message, Cluster, Community, Entity, Topic, Preference],
)
def test_required_metadata(node_class):
    """Test that all node classes have required metadata."""
    assert hasattr(node_class, "NODE_LABEL")
    assert hasattr(node_class, "FETCH_QUERY")
    assert hasattr(node_class, "FETCH_MULTI_QUERY")
    assert hasattr(node_class, "CREATE_QUERY")
    assert hasattr(node_class, "HAS_EMBEDDING")


@pytest.mark.parametrize(
    "node_class,has_embedding",
    [
        (User, False),
        (Room, False),
        (Message, True),
        (Entity, True),
        (Preference, True),
    ],
)
def test_embedding_flags(node_class, has_embedding):
    """Test that node classes have correct embedding flags."""
    assert node_class.HAS_EMBEDDING == has_embedding

    if has_embedding:
        assert hasattr(node_class, "EMBEDDING_RETURN_IDENTIFIER")
        assert node_class.EMBEDDING_RETURN_IDENTIFIER != ""


# Node equality tests
def test_node_equality(uuid_str):
    """Test node equality comparison."""
    # Create two nodes with the same UUID
    user1 = User(
        uuid=uuid_str, name="User 1", platform=PlatformType.TELEGRAM, user_id="uid1"
    )
    user2 = User(
        uuid=uuid_str, name="User 2", platform=PlatformType.DISCORD, user_id="uid2"
    )

    # Create a node with a different UUID
    user3 = User(
        uuid=str(uuid.uuid4()),
        name="User 1",
        platform=PlatformType.TELEGRAM,
        user_id="uid1",
    )

    # Test equality
    assert user1 == user2  # Same UUID should be equal
    assert user1 != user3  # Different UUID should not be equal

    # Test with different node types
    room = Room(
        uuid=uuid_str,
        name="Room",
        platform=PlatformType.TELEGRAM,
        room_id="rid",
        room_type="group",
    )
    assert user1 != room  # Different types should not be equal

    # Test hash
    node_set = {user1, user2, user3, room}
    assert len(node_set) == 3  # user1 and user2 should hash to the same value


# Embedding tests
@pytest.mark.asyncio
@patch("src.athena.core.ai_models.shared.LLMBase.embed_content")
async def test_embed_content_string(mock_embed, user):
    """Test embedding string content."""
    mock_embed.return_value = [0.1, 0.2, 0.3]

    result = await user.embed_content("Test content")
    mock_embed.assert_called_once_with("Test content")
    assert result == [0.1, 0.2, 0.3]


@pytest.mark.asyncio
@patch("src.athena.core.ai_models.shared.LLMBase.embed_content")
async def test_embed_content_list(mock_embed, user):
    """Test embedding list content."""
    mock_embed.return_value = [0.1, 0.2, 0.3]

    result = await user.embed_content(["Test 1", "Test 2"])
    mock_embed.assert_called_once_with(["Test 1", "Test 2"])
    assert result == [0.1, 0.2, 0.3]


# Database operation tests
@pytest.mark.asyncio
async def test_user_save(user, uuid_str):
    """Test saving user node."""
    query, params = await user.save()

    assert query == User.CREATE_QUERY
    assert params["uuid"] == uuid_str
    assert params["user_id"] == "user123"
    assert params["platform"] == PlatformType.TELEGRAM.value
    assert params["name"] == "Test User"
    assert "created_at" in params
    assert "updated_at" in params


@pytest.mark.asyncio
async def test_message_save_with_embedding(message):
    """Test saving message node with embedding."""
    query, params = await message.save()

    assert "WITH m CALL db.create.setNodeVectorProperty" in query
    assert params["embedding"] == [0.1, 0.2, 0.3]


@pytest.mark.asyncio
async def test_room_save(room):
    """Test saving room node."""
    query, params = await room.save()

    assert query == Room.CREATE_QUERY
    assert params["room_id"] == "room123"
    assert params["room_type"] == "group"
    assert params["community_id"] == "community123"


@pytest.mark.asyncio
async def test_topic_save(topic):
    """Test saving topic node (inherits from Entity)."""
    query, params = await topic.save()

    assert params["entity_type"] == "topic"
    assert params["embedding"] == [0.7, 0.8, 0.9]


@pytest.mark.asyncio
async def test_delete_operations(user, message):
    """Test delete operations for nodes."""
    # Test User delete
    query, params = await user.delete()
    assert "MATCH (u:User {uuid: $uuid})" in query
    assert "DETACH DELETE u" in query
    assert params["uuid"] == user.uuid

    # Test Message delete
    query, params = await message.delete()
    assert "MATCH (m:Message {uuid: $uuid})" in query
    assert "DETACH DELETE m" in query
    assert params["uuid"] == message.uuid


@pytest.mark.asyncio
async def test_fetch_operations(user):
    """Test fetch operations for nodes."""
    # Test get_by_uuid
    query, params = await user.get_by_uuid("test-uuid")
    assert query == User.FETCH_QUERY
    assert params["uuid"] == "test-uuid"

    # Test get_by_uuids
    query, params = await user.get_by_uuids(["uuid1", "uuid2"])
    assert query == User.FETCH_MULTI_QUERY
    assert params["uuids"] == ["uuid1", "uuid2"]


@pytest.mark.asyncio
async def test_update_operations(user):
    """Test update operations for nodes."""
    # Test update (should be same as save)
    with patch.object(user, "save") as mock_save:
        mock_save.return_value = ("QUERY", {"param": "value"})
        result = await user.update()
        mock_save.assert_called_once()
        assert result == ("QUERY", {"param": "value"})


@pytest.mark.asyncio
async def test_missing_metadata():
    """Test behavior when metadata is missing."""

    # Create a node class without required metadata
    class InvalidNode(OrganonNode):
        name: str
        platform: PlatformType

    # Create an instance
    invalid_node = InvalidNode(name="Invalid", platform=PlatformType.GLOBAL)

    # Test operations that require metadata
    with pytest.raises(NotImplementedError):
        await invalid_node.save()

    with pytest.raises(NotImplementedError):
        await invalid_node.get_by_uuid("uuid")

    with pytest.raises(NotImplementedError):
        await invalid_node.get_by_uuids(["uuid1", "uuid2"])


def test_topic_entity_type():
    """Test that Topic has fixed entity_type."""
    # Create Topic with default entity_type
    topic = Topic(name="Test Topic", platform=PlatformType.GLOBAL)
    assert topic.entity_type == "topic"

    # Try to create with different entity_type (should be ignored)
    topic2 = Topic(name="Test Topic", platform=PlatformType.GLOBAL, entity_type="other")
    assert topic2.entity_type == "topic"


# Parametrized test for get_save_params
@pytest.mark.parametrize(
    "node_fixture,expected_fields",
    [
        ("user", ["uuid", "name", "platform", "user_id", "summary"]),
        (
            "message",
            ["message_id", "room_id", "content", "engagement_score", "embedding"],
        ),
        (
            "cluster",
            ["room_id", "keywords", "messages", "embeddings", "start_time", "end_time"],
        ),
    ],
)
def test_get_save_params(node_fixture, expected_fields, request):
    """Test get_save_params method for different node types."""
    # Get the node instance
    node = request.getfixturevalue(node_fixture)

    # Get the parameters
    params = node.get_save_params()

    # Check that all expected fields are present and have correct values
    for field in expected_fields:
        assert field in params
        if hasattr(node, field):
            field_value = getattr(node, field)
            if isinstance(field_value, datetime.datetime):
                assert params[field] == field_value.isoformat()
            elif isinstance(field_value, PlatformType):
                assert params[field] == field_value.value
            else:
                assert params[field] == field_value
