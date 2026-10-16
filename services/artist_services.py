from core.database import engine
from sqlalchemy import text
from typing import Any


async def list_artists(limit: int = 10, offset: int = 0) -> dict[str, Any]:
    """Return one page of artists and pagination metadata."""

    artists_query = text("""SELECT
    ar.ArtistId,
    ar.Name,
    COUNT(al.AlbumId) AS AlbumCount
FROM Artist AS ar
LEFT JOIN Album AS al
    ON al.ArtistId = ar.ArtistId
GROUP BY ar.ArtistId, ar.Name
ORDER BY ar.ArtistId
LIMIT :limit OFFSET :offset;
""")

    count_query = text("SELECT COUNT(*) FROM Artist")

    async with engine.connect() as conn:
        artists_result = await conn.execute(
            artists_query,
            {"limit": limit, "offset": offset}
        )
        artists = [dict(row) for row in artists_result.mappings().all()]

        count_result = await conn.execute(count_query)
        total = count_result.scalar_one()

    next_offset = offset + len(artists)

    return {
        "artists": artists,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_next": next_offset < total,
        "next_offset": next_offset if next_offset < total else None,
    }


async def search_artists(name: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search artists by a partial name match."""

    query = text("""SELECT
    ar.ArtistId,
    ar.Name,
    COUNT(al.AlbumId) AS AlbumCount
FROM Artist AS ar
LEFT JOIN Album AS al
    ON al.ArtistId = ar.ArtistId
WHERE ar.Name LIKE :name
GROUP BY ar.ArtistId, ar.Name
ORDER BY ar.Name
LIMIT :limit;
""")

    async with engine.connect() as conn:
        result = await conn.execute(
            query,
            {"name": f"%{name}%", "limit": limit}
        )
        return [dict(row) for row in result.mappings().all()]


async def get_artist_details(artist_id: int) -> dict[str, Any] | None:
    """Return an artist with their albums, or None if not found."""

    artist_query = text("""SELECT
    ArtistId,
    Name
FROM Artist
WHERE ArtistId = :artist_id;
""")

    albums_query = text("""SELECT
    al.AlbumId,
    al.Title,
    COUNT(t.TrackId) AS TrackCount
FROM Album AS al
LEFT JOIN Track AS t
    ON t.AlbumId = al.AlbumId
WHERE al.ArtistId = :artist_id
GROUP BY al.AlbumId, al.Title
ORDER BY al.Title;
""")

    async with engine.connect() as conn:
        artist_result = await conn.execute(
            artist_query,
            {"artist_id": artist_id}
        )
        artist = artist_result.mappings().first()

        if artist is None:
            return None

        albums_result = await conn.execute(
            albums_query,
            {"artist_id": artist_id}
        )
        albums = [dict(row) for row in albums_result.mappings().all()]

    return {"artist": dict(artist), "albums": albums}
