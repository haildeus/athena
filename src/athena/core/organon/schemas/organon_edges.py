import datetime
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from ..operations.organon_edge_op import (
    CREATE_CLUSTER_RELATED_TO_ROOM_QUERY,
    CREATE_CLUSTER_RELATED_TO_TOPIC_QUERY,
    CREATE_MESSAGE_BELONGS_TO_CLUSTER_QUERY,
    CREATE_MESSAGE_POSTED_IN_ROOM_QUERY,
    CREATE_ROOM_RELATED_TO_TOPIC_QUERY,
    CREATE_USER_BELONGS_TO_ROOM_QUERY,
    CREATE_USER_RELATED_TO_TOPIC_QUERY,
)
from .organon_nodes import (
    Cluster,
    Message,
    OrganonNode,
    Room,
    Topic,
    User,
)


class OrganonEdge(BaseModel, ABC):
    """Base class for all Organon edges."""

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

    @abstractmethod
    def connect(
        self, node1: OrganonNode, node2: OrganonNode
    ) -> tuple[str, dict[str, Any]]:
        """Connect two nodes."""
        pass

    def check_supported_pair(self, node1: OrganonNode, node2: OrganonNode) -> bool:
        """Check if the pair of nodes is supported."""
        try:
            assert (node1, node2) in self.supported_pairs
        except AssertionError:
            raise ValueError("Invalid nodes for edge") from None
        except Exception as e:
            raise ValueError("Unexpected error") from e


# --- Relationship Models ---
class Posts(OrganonEdge):
    def connect(
        self, node1: OrganonNode, node2: OrganonNode
    ) -> tuple[str, dict[str, Any]]:
        """Connect two nodes."""
        raise NotImplementedError("Not implemented")


class PostedIn(OrganonEdge):
    supported_pairs = [
        (Message, Room),
        (User, Room),
    ]

    def connect(
        self, node1: OrganonNode, node2: OrganonNode
    ) -> tuple[str, dict[str, Any]]:
        """Connect two nodes."""
        self.check_supported_pair(node1, node2)

        if isinstance(node1, User) and isinstance(node2, Room):
            return CREATE_USER_BELONGS_TO_ROOM_QUERY
        elif isinstance(node1, Message) and isinstance(node2, Room):
            return CREATE_MESSAGE_POSTED_IN_ROOM_QUERY

        raise ValueError("Unexpected error")


class Mentions(OrganonEdge):
    def connect(
        self, node1: OrganonNode, node2: OrganonNode
    ) -> tuple[str, dict[str, Any]]:
        """Connect two nodes."""
        raise NotImplementedError("Not implemented")


class Includes(OrganonEdge):
    def connect(
        self, node1: OrganonNode, node2: OrganonNode
    ) -> tuple[str, dict[str, Any]]:
        """Connect two nodes."""
        raise NotImplementedError("Not implemented")


class BelongsTo(OrganonEdge):
    """
    - Belongs to a room
    - Belongs to a community
    - Belongs to a cluster
    """

    supported_pairs = [
        (Message, Cluster),
        (User, Room),
    ]

    def connect(
        self, node1: OrganonNode, node2: OrganonNode
    ) -> tuple[str, dict[str, Any]]:
        """Connect two nodes."""
        self.check_supported_pair(node1, node2)

        if isinstance(node1, Message) and isinstance(node2, Cluster):
            return CREATE_MESSAGE_BELONGS_TO_CLUSTER_QUERY
        elif isinstance(node1, User) and isinstance(node2, Room):
            return CREATE_USER_BELONGS_TO_ROOM_QUERY

        raise ValueError("Unexpected error")


class ParticipatesIn(OrganonEdge):
    def connect(
        self, node1: OrganonNode, node2: OrganonNode
    ) -> tuple[str, dict[str, Any]]:
        """Connect two nodes."""
        raise NotImplementedError("Not implemented")


class HasPreference(OrganonEdge):
    def connect(
        self, node1: OrganonNode, node2: OrganonNode
    ) -> tuple[str, dict[str, Any]]:
        """Connect two nodes."""
        raise NotImplementedError("Not implemented")


class For(OrganonEdge):
    def connect(
        self, node1: OrganonNode, node2: OrganonNode
    ) -> tuple[str, dict[str, Any]]:
        """Connect two nodes."""
        raise NotImplementedError("Not implemented")


class RelatedTo(OrganonEdge):
    supported_pairs = [
        (Cluster, Room),
        (Cluster, Topic),
        (User, Topic),
        (Room, Topic),
    ]

    def connect(
        self, node1: OrganonNode, node2: OrganonNode
    ) -> tuple[str, dict[str, Any]]:
        """Connect two nodes."""
        self.check_supported_pair(node1, node2)

        if isinstance(node1, Cluster) and isinstance(node2, Room):
            return CREATE_CLUSTER_RELATED_TO_ROOM_QUERY
        elif isinstance(node1, Cluster) and isinstance(node2, Topic):
            return CREATE_CLUSTER_RELATED_TO_TOPIC_QUERY
        elif isinstance(node1, User) and isinstance(node2, Topic):
            return CREATE_USER_RELATED_TO_TOPIC_QUERY
        elif isinstance(node1, Room) and isinstance(node2, Topic):
            return CREATE_ROOM_RELATED_TO_TOPIC_QUERY

        raise ValueError("Unexpected error")


class Expresses(OrganonEdge):
    def connect(
        self, node1: OrganonNode, node2: OrganonNode
    ) -> tuple[str, dict[str, Any]]:
        """Connect two nodes."""
        raise NotImplementedError("Not implemented")
