
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Album(BaseModel):
    pass


class GetAlbumInput(Album):
    model_config = ConfigDict(extra="forbid")

    album_id: int = Field(
        ge=1,
        description="Positive AlbumId from the Chinook database.",
    )


class AlbumOutput(Album):
    model_config = ConfigDict(extra="forbid")

    found: bool
    album: dict[str, Any] | None


# class AlbumListOutput(Album):
#     model_config = ConfigDict(extra="forbid")

#     count: int
#     albums: list[dict[str, Any]]


class AlbumListOutput(Album):
    model_config = ConfigDict(extra="forbid")

    albums: list[dict[str, Any]] = Field(
        description="Album records on the current page."
    )
    total: int = Field(
        ge=0,
        description="Total number of albums in the database."
    )
    limit: int = Field(
        ge=1,
        description="Maximum number of albums requested."
    )
    offset: int = Field(
        ge=0,
        description="Number of albums skipped."
    )
    has_next: bool = Field(
        description="Whether another page is available."
    )
    next_offset: int | None = Field(
        default=None,
        description="Offset to request the next page, or null if finished."
    )


class AlbumSearchOutput(Album):
    model_config = ConfigDict(extra="forbid")

    query: str
    count: int
    albums: list[dict[str, Any]]


class AlbumCountOutput(Album):
    model_config = ConfigDict(extra="forbid")

    count: int
