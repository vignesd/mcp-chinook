from core.database import engine
from sqlalchemy import text
from typing import Any


async def get_total_revenue(
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Return revenue totals, optionally limited to an inclusive date range.

    Dates are ISO strings (YYYY-MM-DD). InvoiceDate is stored as
    'YYYY-MM-DD HH:MM:SS' text, so string comparison is chronological.
    """

    query = text("""SELECT
    COUNT(*) AS InvoiceCount,
    COUNT(DISTINCT CustomerId) AS CustomerCount,
    COALESCE(ROUND(SUM(Total), 2), 0) AS TotalRevenue,
    COALESCE(ROUND(AVG(Total), 2), 0) AS AverageInvoiceValue,
    MIN(InvoiceDate) AS FirstInvoiceDate,
    MAX(InvoiceDate) AS LastInvoiceDate
FROM Invoice
WHERE (:start_date IS NULL OR InvoiceDate >= :start_date)
  AND (:end_date IS NULL OR InvoiceDate < date(:end_date, '+1 day'));
""")

    async with engine.connect() as conn:
        result = await conn.execute(
            query,
            {"start_date": start_date, "end_date": end_date}
        )
        return dict(result.mappings().one())


async def get_sales_by_month(year: int) -> list[dict[str, Any]]:
    """Return invoice counts and revenue for each month of a year with sales."""

    query = text("""SELECT
    strftime('%Y-%m', InvoiceDate) AS Month,
    COUNT(*) AS InvoiceCount,
    ROUND(SUM(Total), 2) AS Revenue
FROM Invoice
WHERE strftime('%Y', InvoiceDate) = :year
GROUP BY Month
ORDER BY Month;
""")

    async with engine.connect() as conn:
        result = await conn.execute(query, {"year": f"{year:04d}"})
        return [dict(row) for row in result.mappings().all()]


async def get_revenue_by_country(limit: int = 10) -> list[dict[str, Any]]:
    """Return revenue per billing country, highest first."""

    query = text("""SELECT
    BillingCountry AS Country,
    COUNT(DISTINCT CustomerId) AS CustomerCount,
    COUNT(*) AS InvoiceCount,
    ROUND(SUM(Total), 2) AS Revenue
FROM Invoice
GROUP BY BillingCountry
ORDER BY Revenue DESC, Country
LIMIT :limit;
""")

    async with engine.connect() as conn:
        result = await conn.execute(query, {"limit": limit})
        return [dict(row) for row in result.mappings().all()]


async def get_best_selling_tracks(limit: int = 10) -> list[dict[str, Any]]:
    """Return the tracks with the most units sold."""

    query = text("""SELECT
    t.TrackId,
    t.Name AS TrackName,
    ar.Name AS ArtistName,
    SUM(il.Quantity) AS UnitsSold,
    ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS Revenue
FROM InvoiceLine AS il
JOIN Track AS t
    ON t.TrackId = il.TrackId
LEFT JOIN Album AS al
    ON al.AlbumId = t.AlbumId
LEFT JOIN Artist AS ar
    ON ar.ArtistId = al.ArtistId
GROUP BY t.TrackId, t.Name, ar.Name
ORDER BY UnitsSold DESC, Revenue DESC, t.TrackId
LIMIT :limit;
""")

    async with engine.connect() as conn:
        result = await conn.execute(query, {"limit": limit})
        return [dict(row) for row in result.mappings().all()]


async def get_top_artists_by_revenue(limit: int = 10) -> list[dict[str, Any]]:
    """Return the artists whose tracks generated the most revenue."""

    query = text("""SELECT
    ar.ArtistId,
    ar.Name AS ArtistName,
    SUM(il.Quantity) AS UnitsSold,
    ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS Revenue
FROM InvoiceLine AS il
JOIN Track AS t
    ON t.TrackId = il.TrackId
JOIN Album AS al
    ON al.AlbumId = t.AlbumId
JOIN Artist AS ar
    ON ar.ArtistId = al.ArtistId
GROUP BY ar.ArtistId, ar.Name
ORDER BY Revenue DESC, ar.ArtistId
LIMIT :limit;
""")

    async with engine.connect() as conn:
        result = await conn.execute(query, {"limit": limit})
        return [dict(row) for row in result.mappings().all()]


async def get_top_customers(limit: int = 10) -> list[dict[str, Any]]:
    """Return the customers with the highest total spend."""

    query = text("""SELECT
    c.CustomerId,
    c.FirstName || ' ' || c.LastName AS CustomerName,
    c.Country,
    COUNT(i.InvoiceId) AS InvoiceCount,
    ROUND(SUM(i.Total), 2) AS TotalSpent
FROM Customer AS c
JOIN Invoice AS i
    ON i.CustomerId = c.CustomerId
GROUP BY c.CustomerId, CustomerName, c.Country
ORDER BY TotalSpent DESC, c.CustomerId
LIMIT :limit;
""")

    async with engine.connect() as conn:
        result = await conn.execute(query, {"limit": limit})
        return [dict(row) for row in result.mappings().all()]


async def get_customer_lifetime_value(customer_id: int) -> dict[str, Any] | None:
    """Return a customer's lifetime spend, or None if the customer does not exist."""

    # Subqueries keep invoice totals and line quantities from double counting.
    query = text("""SELECT
    c.CustomerId,
    c.FirstName || ' ' || c.LastName AS CustomerName,
    c.Email,
    c.Country,
    (SELECT COUNT(*) FROM Invoice AS i
        WHERE i.CustomerId = c.CustomerId) AS InvoiceCount,
    (SELECT COALESCE(ROUND(SUM(i.Total), 2), 0) FROM Invoice AS i
        WHERE i.CustomerId = c.CustomerId) AS TotalSpent,
    (SELECT COALESCE(ROUND(AVG(i.Total), 2), 0) FROM Invoice AS i
        WHERE i.CustomerId = c.CustomerId) AS AverageInvoiceValue,
    (SELECT COALESCE(SUM(il.Quantity), 0) FROM InvoiceLine AS il
        JOIN Invoice AS i ON i.InvoiceId = il.InvoiceId
        WHERE i.CustomerId = c.CustomerId) AS TracksPurchased,
    (SELECT MIN(i.InvoiceDate) FROM Invoice AS i
        WHERE i.CustomerId = c.CustomerId) AS FirstPurchaseDate,
    (SELECT MAX(i.InvoiceDate) FROM Invoice AS i
        WHERE i.CustomerId = c.CustomerId) AS LastPurchaseDate
FROM Customer AS c
WHERE c.CustomerId = :customer_id;
""")

    async with engine.connect() as conn:
        result = await conn.execute(query, {"customer_id": customer_id})
        row = result.mappings().first()

        return dict(row) if row else None
