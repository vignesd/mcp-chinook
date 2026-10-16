from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Track(BaseModel):
    """Track base model."""

    model_config = ConfigDict(extra="forbid")


class TrackSummary(Track):
    """Track record used in listings."""

    TrackId: int
    Name: str
    AlbumTitle: str | None
    ArtistName: str | None
    GenreName: str | None
    Composer: str | None
    Milliseconds: int
    Duration: str = Field(description="Track length formatted as m:ss.")
    UnitPrice: Decimal


class TrackRecord(Track):
    """Full track record with related catalogue data and sales."""

    TrackId: int
    Name: str
    AlbumId: int | None
    AlbumTitle: str | None
    ArtistId: int | None
    ArtistName: str | None
    GenreId: int | None
    GenreName: str | None
    MediaTypeId: int
    MediaType: str | None
    Composer: str | None
    Milliseconds: int
    Duration: str = Field(description="Track length formatted as m:ss.")
    Bytes: int | None
    UnitPrice: Decimal
    UnitsSold: int = Field(description="Total units sold across all invoices.")


class Genre(Track):
    """Genre record."""

    GenreId: int
    Name: str | None


class GenreSummary(Genre):
    """Genre with the number of tracks in it."""

    TrackCount: int


class TrackPage(Track):
    """Pagination fields shared by paged track listings."""

    tracks: list[TrackSummary] = Field(
        description="Track records on the current page."
    )
    total: int = Field(
        ge=0,
        description="Total number of matching tracks."
    )
    limit: int = Field(
        ge=1,
        description="Maximum number of tracks requested."
    )
    offset: int = Field(
        ge=0,
        description="Number of tracks skipped."
    )
    has_next: bool = Field(
        description="Whether another page is available."
    )
    next_offset: int | None = Field(
        default=None,
        description="Offset to request the next page, or null if finished."
    )


class TrackSearchOutput(TrackPage):
    """Tracks matching a partial name or composer search."""

    query: str


class TrackDetailsOutput(Track):
    """A single track."""

    found: bool
    track: TrackRecord


class GenreListOutput(Track):
    """All genres with track counts."""

    count: int
    genres: list[GenreSummary]


class GenreTracksOutput(TrackPage):
    """One page of tracks in a genre."""

    genre: Genre


class LongestTracksOutput(Track):
    """The longest tracks by duration."""

    count: int
    tracks: list[TrackSummary]
