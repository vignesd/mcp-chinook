from pydantic import BaseModel, ConfigDict, Field


class Artist(BaseModel):
    """Artist base model."""

    model_config = ConfigDict(extra="forbid")


class ArtistSummary(Artist):
    """An artist with the number of albums they have."""

    ArtistId: int
    Name: str | None
    AlbumCount: int


class ArtistAlbum(Artist):
    """An album by an artist."""

    AlbumId: int
    Title: str
    TrackCount: int


class ArtistRecord(Artist):
    """Core artist record."""

    ArtistId: int
    Name: str | None


class ArtistListOutput(Artist):
    """One page of artists with pagination metadata."""

    artists: list[ArtistSummary] = Field(
        description="Artist records on the current page."
    )
    total: int = Field(
        ge=0,
        description="Total number of artists in the database."
    )
    limit: int = Field(
        ge=1,
        description="Maximum number of artists requested."
    )
    offset: int = Field(
        ge=0,
        description="Number of artists skipped."
    )
    has_next: bool = Field(
        description="Whether another page is available."
    )
    next_offset: int | None = Field(
        default=None,
        description="Offset to request the next page, or null if finished."
    )


class ArtistSearchOutput(Artist):
    """Artists matching a partial name search."""

    query: str
    count: int
    artists: list[ArtistSummary]


class ArtistDetailsOutput(Artist):
    """An artist and their albums."""

    found: bool
    artist: ArtistRecord
    album_count: int
    albums: list[ArtistAlbum]
