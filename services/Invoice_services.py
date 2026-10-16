from core.database import engine
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import Any


async def _customer_exists(conn: AsyncConnection, customer_id: int) -> bool:
    """Return True if a customer with the given ID exists."""

    query = text("SELECT 1 FROM Customer WHERE CustomerId = :customer_id")
    result = await conn.execute(query, {"customer_id": customer_id})
    return result.first() is not None


async def get_invoices(customer_id: int) -> list[dict[str, Any]] | None:
    """Return a customer's invoices, or None if the customer does not exist."""

    query = text("""SELECT
    i.InvoiceId,
    i.CustomerId,
    c.FirstName,
    c.LastName,
    c.Email,
    i.InvoiceDate,
    i.BillingAddress,
    i.BillingCity,
    i.BillingState,
    i.BillingCountry,
    i.BillingPostalCode,
    i.Total
FROM Invoice AS i
JOIN Customer AS c
    ON c.CustomerId = i.CustomerId
WHERE i.CustomerId = :customer_id
ORDER BY i.InvoiceDate DESC, i.InvoiceId DESC;
""")

    async with engine.connect() as conn:
        if not await _customer_exists(conn, customer_id):
            return None

        result = await conn.execute(
            query,
            {"customer_id": customer_id}
        )
        return [dict(row) for row in result.mappings().all()]


async def get_invoice_tracks(customer_id: int) -> list[dict[str, Any]] | None:
    """Return a customer's purchased tracks, or None if the customer does not exist."""

    query = text("""SELECT
    i.InvoiceId,
    i.InvoiceDate,
    i.CustomerId,
    c.FirstName || ' ' || c.LastName AS CustomerName,
    i.BillingCountry,
    t.Name AS TrackName,
    il.UnitPrice,
    il.Quantity,
    il.UnitPrice * il.Quantity AS LineTotal,
    i.Total AS InvoiceTotal
FROM Invoice AS i
JOIN Customer AS c
    ON c.CustomerId = i.CustomerId
JOIN InvoiceLine AS il
    ON il.InvoiceId = i.InvoiceId
JOIN Track AS t
    ON t.TrackId = il.TrackId
WHERE i.CustomerId = :customer_id
ORDER BY i.InvoiceDate DESC, i.InvoiceId DESC, il.InvoiceLineId;
""")

    async with engine.connect() as conn:
        if not await _customer_exists(conn, customer_id):
            return None

        result = await conn.execute(
            query,
            {"customer_id": customer_id}
        )
        return [dict(row) for row in result.mappings().all()]


async def get_invoice_details(invoice_id: int) -> dict[str, Any] | None:
    """Return an invoice header and its line items, or None if not found."""

    header_query = text("""SELECT
    i.InvoiceId,
    i.CustomerId,
    c.FirstName,
    c.LastName,
    c.Email,
    i.InvoiceDate,
    i.BillingAddress,
    i.BillingCity,
    i.BillingState,
    i.BillingCountry,
    i.BillingPostalCode,
    i.Total
FROM Invoice AS i
JOIN Customer AS c
    ON c.CustomerId = i.CustomerId
WHERE i.InvoiceId = :invoice_id;
""")

    lines_query = text("""SELECT
    il.InvoiceLineId,
    t.TrackId,
    t.Name AS TrackName,
    al.Title AS AlbumTitle,
    ar.Name AS ArtistName,
    il.UnitPrice,
    il.Quantity,
    il.UnitPrice * il.Quantity AS LineTotal
FROM InvoiceLine AS il
JOIN Track AS t
    ON t.TrackId = il.TrackId
JOIN Album AS al
    ON al.AlbumId = t.AlbumId
JOIN Artist AS ar
    ON ar.ArtistId = al.ArtistId
WHERE il.InvoiceId = :invoice_id
ORDER BY il.InvoiceLineId;
""")

    async with engine.connect() as conn:
        header_result = await conn.execute(
            header_query,
            {"invoice_id": invoice_id}
        )
        header = header_result.mappings().first()

        if header is None:
            return None

        lines_result = await conn.execute(
            lines_query,
            {"invoice_id": invoice_id}
        )
        lines = [dict(row) for row in lines_result.mappings().all()]

    return {"invoice": dict(header), "lines": lines}
