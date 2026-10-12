
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text


async def get_album(engine: AsyncEngine, album_id: int) -> dict | None:
    query = text('SELECT * FROM Album WHERE AlbumId = :album_id')

    async with engine.connect() as conn:
        result = await conn.execute(
            query,
            {"album_id": album_id},
        )
        row = result.mappings().first()

        return dict(row) if row else None


# async def list_albums(engine: AsyncEngine) -> list[dict]:
#     """Fetch all records from the Album table."""

#     query = text(""" SELECT * FROM Album """)

#     async with engine.connect() as conn:
#         result = await conn.execute(query)
#         return [dict(row) for row in result.mappings().all()]


async def list_albums(
    engine: AsyncEngine,
    limit: int = 10,
    offset: int = 0,
) -> dict:
    """Return one page of albums and pagination metadata."""

    albums_query = text("""
        SELECT *
        FROM Album
        ORDER BY AlbumId
        LIMIT :limit OFFSET :offset
    """)

    count_query = text("""
        SELECT COUNT(*)
        FROM Album
    """)

    async with engine.connect() as connection:
        albums_result = await connection.execute(
            albums_query,
            {"limit": limit, "offset": offset},
        )
        albums = [dict(row) for row in albums_result.mappings().all()]

        count_result = await connection.execute(count_query)
        total = count_result.scalar_one()

    return {
        "albums": albums,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_next": offset + len(albums) < total,
        "next_offset": offset + len(albums)
        if offset + len(albums) < total
        else None,
    }


async def search_albums(engine: AsyncEngine, title: str) -> list[dict]:
    """Search albums by title using LIKE."""

    query = text("""
        SELECT *
        FROM Album
        WHERE Title LIKE :title
    """)

    async with engine.connect() as conn:
        result = await conn.execute(
            query,
            {"title": f"%{title}%"},
        )
        return [dict(row) for row in result.mappings().all()]


async def get_total_albums(engine: AsyncEngine) -> int:
    query = text("""
        SELECT COUNT(*) AS total_rows
        FROM Album
    """)

    async with engine.connect() as conn:
        result = await conn.execute(
            query,
        )
        return result.scalar_one()
