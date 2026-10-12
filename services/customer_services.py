from core.database import engine
from sqlalchemy import text


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
