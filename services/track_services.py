from core.database import engine
from sqlalchemy import text
from typing import Any


# Shared column list and joins for track listings.
_TRACK_COLUMNS = """
    t.TrackId,
    t.Name,
    al.Title AS AlbumTitle,
    ar.Name AS ArtistName,
    g.Name AS GenreName,
    t.Composer,
    t.Milliseconds,
    printf('%d:%02d', t.Milliseconds / 60000, (t.Milliseconds / 1000) % 60) AS Duration,
    t.UnitPrice
"""

_TRACK_JOINS = """
FROM Track AS t
LEFT JOIN Album AS al
    ON al.AlbumId = t.AlbumId
LEFT JOIN Artist AS ar
    ON ar.ArtistId = al.ArtistId
LEFT JOIN Genre AS g
    ON g.GenreId = t.GenreId
"""


def _page(tracks: list[dict[str, Any]], total: int, limit: int, offset: int) -> dict[str, Any]:
    """Build pagination metadata for a page of tracks."""

    next_offset = offset + len(tracks)

    return {
        "tracks": tracks,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_next": next_offset < total,
        "next_offset": next_offset if next_offset < total else None,
    }


async def search_tracks(query: str, limit: int = 10, offset: int = 0) -> dict[str, Any]:
    """Search tracks by a partial match on track name or composer."""

    tracks_query = text(f"""SELECT {_TRACK_COLUMNS}
{_TRACK_JOINS}
WHERE t.Name LIKE :query OR t.Composer LIKE :query
ORDER BY t.Name, t.TrackId
LIMIT :limit OFFSET :offset;
""")

    count_query = text("""SELECT COUNT(*)
FROM Track AS t
WHERE t.Name LIKE :query OR t.Composer LIKE :query;
""")

    params = {"query": f"%{query}%", "limit": limit, "offset": offset}

    async with engine.connect() as conn:
        tracks_result = await conn.execute(tracks_query, params)
        tracks = [dict(row) for row in tracks_result.mappings().all()]

        count_result = await conn.execute(count_query, params)
        total = count_result.scalar_one()

    return _page(tracks, total, limit, offset)


async def get_track_details(track_id: int) -> dict[str, Any] | None:
    """Return a track with album, artist, genre, media type, and units sold."""

    query = text("""SELECT
    t.TrackId,
    t.Name,
    t.AlbumId,
    al.Title AS AlbumTitle,
    al.ArtistId,
    ar.Name AS ArtistName,
    t.GenreId,
    g.Name AS GenreName,
    t.MediaTypeId,
    mt.Name AS MediaType,
    t.Composer,
    t.Milliseconds,
    printf('%d:%02d', t.Milliseconds / 60000, (t.Milliseconds / 1000) % 60) AS Duration,
    t.Bytes,
    t.UnitPrice,
    (SELECT COALESCE(SUM(il.Quantity), 0) FROM InvoiceLine AS il
        WHERE il.TrackId = t.TrackId) AS UnitsSold
FROM Track AS t
LEFT JOIN Album AS al
    ON al.AlbumId = t.AlbumId
LEFT JOIN Artist AS ar
    ON ar.ArtistId = al.ArtistId
LEFT JOIN Genre AS g
    ON g.GenreId = t.GenreId
LEFT JOIN MediaType AS mt
    ON mt.MediaTypeId = t.MediaTypeId
WHERE t.TrackId = :track_id;
""")

    async with engine.connect() as conn:
        result = await conn.execute(query, {"track_id": track_id})
        row = result.mappings().first()

        return dict(row) if row else None


async def list_genres() -> list[dict[str, Any]]:
    """Return all genres with their track counts."""

    query = text("""SELECT
    g.GenreId,
    g.Name,
    COUNT(t.TrackId) AS TrackCount
FROM Genre AS g
LEFT JOIN Track AS t
    ON t.GenreId = g.GenreId
GROUP BY g.GenreId, g.Name
ORDER BY g.Name;
""")

    async with engine.connect() as conn:
        result = await conn.execute(query)
        return [dict(row) for row in result.mappings().all()]


async def get_tracks_by_genre(
    genre_id: int,
    limit: int = 10,
    offset: int = 0,
) -> dict[str, Any] | None:
    """Return one page of tracks in a genre, or None if the genre does not exist."""

    genre_query = text("SELECT GenreId, Name FROM Genre WHERE GenreId = :genre_id")

    tracks_query = text(f"""SELECT {_TRACK_COLUMNS}
{_TRACK_JOINS}
WHERE t.GenreId = :genre_id
ORDER BY t.Name, t.TrackId
LIMIT :limit OFFSET :offset;
""")

    count_query = text("SELECT COUNT(*) FROM Track WHERE GenreId = :genre_id")

    params = {"genre_id": genre_id, "limit": limit, "offset": offset}

    async with engine.connect() as conn:
        genre_result = await conn.execute(genre_query, params)
        genre = genre_result.mappings().first()

        if genre is None:
            return None

        tracks_result = await conn.execute(tracks_query, params)
        tracks = [dict(row) for row in tracks_result.mappings().all()]

        count_result = await conn.execute(count_query, params)
        total = count_result.scalar_one()

    return {"genre": dict(genre), **_page(tracks, total, limit, offset)}


async def get_longest_tracks(limit: int = 10) -> list[dict[str, Any]]:
    """Return the longest tracks by duration."""

    query = text(f"""SELECT {_TRACK_COLUMNS}
{_TRACK_JOINS}
ORDER BY t.Milliseconds DESC, t.TrackId
LIMIT :limit;
""")

    async with engine.connect() as conn:
        result = await conn.execute(query, {"limit": limit})
        return [dict(row) for row in result.mappings().all()]
