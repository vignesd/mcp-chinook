from core.database import engine
from sqlalchemy import text
from typing import Any


async def get_customer_by_email(email_id: str) -> dict | None:
    query = text(
        'SELECT CustomerId,FirstName,LastName,Company,Address,City,State,Country,PostalCode,Phone '
        'FROM Customer '
        'WHERE Email=:email_id')

    async with engine.connect() as conn:
        result = await conn.execute(
            query,
            {"email_id": email_id}
        )
        row = result.mappings().first()

        return dict(row) if row else None


async def get_customer_by_id(customer_id: int) -> dict | None:
    query = text(
        'SELECT CustomerId,FirstName,LastName,Company,Address,City,State,Country,PostalCode,Phone '
        'FROM Customer '
        'WHERE CustomerId=:customer_id')

    async with engine.connect() as conn:
        result = await conn.execute(
            query,
            {"customer_id": customer_id}
        )
        row = result.mappings().first()

        return dict(row) if row else None


async def search_customers_by_keyword(keyword: str, limit: int = 10, offset: int = 0) -> list[dict[str, Any]] | None:
    query = text("""SELECT * FROM Customer 
    WHERE FirstName LIKE :keyword 
    OR LastName LIKE :keyword 
    OR Company LIKE :keyword 
    OR Country LIKE :keyword
    ORDER BY CustomerId 
    LIMIT :limit 
    OFFSET :offset;
""")

    async with engine.connect() as conn:
        result = await conn.execute(
            query,
            {
                "keyword": keyword,
                "limit": limit,
                "offset": offset
            }
        )
        customers = [dict(row) for row in result.mappings().all()]

        return customers


async def get_customer_count() -> int | None:
    query = text("""
        SELECT COUNT(*) AS total_rows
        FROM Customer
    """)

    async with engine.connect() as conn:
        result = await conn.execute(
            query,
        )
        return result.scalar_one()
