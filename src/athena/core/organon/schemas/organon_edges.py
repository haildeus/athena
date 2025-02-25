import datetime

from pydantic import BaseModel, Field


class OrganonEdge(BaseModel):
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


# --- Relationship Models ---
class PostedIn(OrganonEdge):
    # TODO: Could add properties like 'frequency' here
    pass


class BelongsTo(OrganonEdge):
    pass


class RelatedTo(OrganonEdge):
    pass


class HasPreference(OrganonEdge):
    pass


class Expresses(OrganonEdge):
    pass
