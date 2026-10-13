from core.database import engine
from sqlalchemy import text
from typing import Any
from core.logging import logger


async def get_invoices(customer_id: int) -> list[dict[str, Any]] | None:
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
        result = await conn.execute(
            query,
            {"customer_id": customer_id}
        )
        invoices = [dict(row) for row in result.mappings().all()]

        # Log the InvoiceDate value and Python type for debugging
    for invoice in invoices:
        logger.info(
            "InvoiceId=%s | InvoiceDate=%r | type=%s",
            invoice.get("InvoiceId"),
            invoice.get("InvoiceDate"),
            type(invoice.get("InvoiceDate")).__name__,
        )

        return invoices


async def get_invoice_tracks(customer_id: int) -> list[dict[str, Any]] | None:
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
        result = await conn.execute(
            query,
            {"customer_id": customer_id}
        )
        invoices = [dict(row) for row in result.mappings().all()]

        return invoices
