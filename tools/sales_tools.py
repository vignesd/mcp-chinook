from datetime import date
from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError
from mcp.server.mcpserver.exceptions import ToolError

from core.logging import logger
from models.sales_models import (
    BestSellingTracksOutput,
    CustomerLifetimeValueOutput,
    RevenueByCountryOutput,
    SalesByMonthOutput,
    TopArtistsOutput,
    TopCustomersOutput,
    TotalRevenueOutput,
)
from services.sales_services import (
    get_best_selling_tracks as fetch_best_selling_tracks,
    get_customer_lifetime_value as fetch_customer_lifetime_value,
    get_revenue_by_country as fetch_revenue_by_country,
    get_sales_by_month as fetch_sales_by_month,
    get_top_artists_by_revenue as fetch_top_artists,
    get_top_customers as fetch_top_customers,
    get_total_revenue as fetch_total_revenue,
)


def _validate_limit(limit: int) -> None:
    """Reject limits outside the supported range."""

    if not 1 <= limit <= 100:
        raise ToolError("INVALID_ARGUMENT: limit must be between 1 and 100. "
                        "Do not retry with the same invalid value.")


def _parse_date(value: str | None, name: str) -> date | None:
    """Parse an optional ISO date argument."""

    if value is None or not value.strip():
        return None

    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        raise ToolError(f"INVALID_ARGUMENT: {name} must be a date in YYYY-MM-DD "
                        "format, for example 2024-01-31.") from None


async def get_total_revenue(
    start_date: str | None = None,
    end_date: str | None = None,
) -> TotalRevenueOutput:
    """Get total revenue, optionally limited to an inclusive date range.

    Args:
        start_date: Optional inclusive start date in YYYY-MM-DD format.
        end_date: Optional inclusive end date in YYYY-MM-DD format.
    """
    start = _parse_date(start_date, "start_date")
    end = _parse_date(end_date, "end_date")

    if start and end and start > end:
        raise ToolError("INVALID_ARGUMENT: start_date must be on or before "
                        "end_date.")

    start_text = start.isoformat() if start else None
    end_text = end.isoformat() if end else None

    try:
        totals = await fetch_total_revenue(start_text, end_text)

    except SQLAlchemyError:
        logger.exception(
            "Database failure fetching total revenue start=%s end=%s",
            start_text,
            end_text,
        )
        raise ToolError("DATABASE_ERROR: Unable to calculate total revenue "
                        "because a database operation failed. Retry at most "
                        "twice with a short delay. If the error persists, stop "
                        "and report the issue to the user.") from None

    return TotalRevenueOutput(start_date=start_text, end_date=end_text, **totals)


async def get_sales_by_month(year: int) -> SalesByMonthOutput:
    """Get invoice counts and revenue for each month of a year.

    Args:
        year: Four-digit calendar year, for example 2024.
    """
    if not 1900 <= year <= 2100:
        raise ToolError("INVALID_ARGUMENT: year must be a four-digit year "
                        "between 1900 and 2100.")

    try:
        months = await fetch_sales_by_month(year)

    except SQLAlchemyError:
        logger.exception("Database failure fetching sales for year=%s", year)
        raise ToolError("DATABASE_ERROR: Unable to retrieve monthly sales "
                        "because a database operation failed. Retry at most "
                        "twice with a short delay. If the error persists, stop "
                        "and report the issue to the user.") from None

    return SalesByMonthOutput(
        year=year,
        total_revenue=sum(
            (Decimal(str(month["Revenue"])) for month in months), Decimal("0")
        ),
        total_invoices=sum(month["InvoiceCount"] for month in months),
        months=months,  # type:ignore
    )


async def get_revenue_by_country(limit: int = 10) -> RevenueByCountryOutput:
    """Rank billing countries by revenue.

    Args:
        limit: Number of countries to return, from 1 to 100.
    """
    _validate_limit(limit)

    try:
        countries = await fetch_revenue_by_country(limit)

    except SQLAlchemyError:
        logger.exception("Database failure fetching revenue by country")
        raise ToolError("DATABASE_ERROR: Unable to retrieve revenue by country "
                        "because a database operation failed. Retry at most "
                        "twice with a short delay. If the error persists, stop "
                        "and report the issue to the user.") from None

    return RevenueByCountryOutput(
        count=len(countries),
        countries=countries,  # type:ignore
    )


async def get_best_selling_tracks(limit: int = 10) -> BestSellingTracksOutput:
    """Rank tracks by units sold.

    Args:
        limit: Number of tracks to return, from 1 to 100.
    """
    _validate_limit(limit)

    try:
        tracks = await fetch_best_selling_tracks(limit)

    except SQLAlchemyError:
        logger.exception("Database failure fetching best-selling tracks")
        raise ToolError("DATABASE_ERROR: Unable to retrieve best-selling tracks "
                        "because a database operation failed. Retry at most "
                        "twice with a short delay. If the error persists, stop "
                        "and report the issue to the user.") from None

    return BestSellingTracksOutput(
        count=len(tracks),
        tracks=tracks,  # type:ignore
    )


async def get_top_artists_by_revenue(limit: int = 10) -> TopArtistsOutput:
    """Rank artists by the revenue their tracks generated.

    Args:
        limit: Number of artists to return, from 1 to 100.
    """
    _validate_limit(limit)

    try:
        artists = await fetch_top_artists(limit)

    except SQLAlchemyError:
        logger.exception("Database failure fetching top artists by revenue")
        raise ToolError("DATABASE_ERROR: Unable to retrieve top artists "
                        "because a database operation failed. Retry at most "
                        "twice with a short delay. If the error persists, stop "
                        "and report the issue to the user.") from None

    return TopArtistsOutput(
        count=len(artists),
        artists=artists,  # type:ignore
    )


async def get_top_customers(limit: int = 10) -> TopCustomersOutput:
    """Rank customers by total spend.

    Args:
        limit: Number of customers to return, from 1 to 100.
    """
    _validate_limit(limit)

    try:
        customers = await fetch_top_customers(limit)

    except SQLAlchemyError:
        logger.exception("Database failure fetching top customers")
        raise ToolError("DATABASE_ERROR: Unable to retrieve top customers "
                        "because a database operation failed. Retry at most "
                        "twice with a short delay. If the error persists, stop "
                        "and report the issue to the user.") from None

    return TopCustomersOutput(
        count=len(customers),
        customers=customers,  # type:ignore
    )


async def get_customer_lifetime_value(
    customer_id: int,
) -> CustomerLifetimeValueOutput:
    """Get a customer's lifetime spend by CustomerId. If the ID is invalid,
    correct the input before retrying. If the customer does not exist, do not
    retry the same ID. Retry database failures only when they are transient."""
    if customer_id < 1:
        raise ToolError("INVALID_ARGUMENT: customer_id must be a positive integer. "
                        "Provide a customer_id greater than or equal to 1. "
                        "Do not retry with the same invalid value.")

    try:
        value = await fetch_customer_lifetime_value(customer_id)

    except SQLAlchemyError:
        logger.exception(
            "Database failure fetching lifetime value for customer_id=%s",
            customer_id,
        )
        raise ToolError("DATABASE_ERROR: Unable to calculate customer lifetime "
                        "value because a database operation failed. Retry at "
                        "most twice with a short delay. If the error persists, "
                        "stop and report the issue to the user.") from None

    if value is None:
        raise ToolError(f"NOT_FOUND: No customer exists with customer_id={customer_id}. "
                        "Do not retry the same ID. Use search_customers_by_keyword "
                        "or get_top_customers to find valid customer IDs.")

    return CustomerLifetimeValueOutput(found=True, **value)
