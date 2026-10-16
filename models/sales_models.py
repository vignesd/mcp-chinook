from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Sales(BaseModel):
    """Sales analytics base model."""

    model_config = ConfigDict(extra="forbid")


class TotalRevenueOutput(Sales):
    """Revenue totals for all invoices or a date range."""

    start_date: str | None = Field(description="Inclusive start date, or null for no lower bound.")
    end_date: str | None = Field(description="Inclusive end date, or null for no upper bound.")
    InvoiceCount: int
    CustomerCount: int
    TotalRevenue: Decimal
    AverageInvoiceValue: Decimal
    FirstInvoiceDate: str | None
    LastInvoiceDate: str | None


class MonthlySales(Sales):
    """Sales for one month."""

    Month: str = Field(description="Month formatted as YYYY-MM.")
    InvoiceCount: int
    Revenue: Decimal


class SalesByMonthOutput(Sales):
    """Monthly sales for a year."""

    year: int
    total_revenue: Decimal
    total_invoices: int
    months: list[MonthlySales] = Field(
        description="Months with at least one invoice, in calendar order."
    )


class CountryRevenue(Sales):
    """Revenue for one billing country."""

    Country: str
    CustomerCount: int
    InvoiceCount: int
    Revenue: Decimal


class RevenueByCountryOutput(Sales):
    """Countries ranked by revenue."""

    count: int
    countries: list[CountryRevenue]


class TrackSales(Sales):
    """Units sold and revenue for one track."""

    TrackId: int
    TrackName: str
    ArtistName: str | None
    UnitsSold: int
    Revenue: Decimal


class BestSellingTracksOutput(Sales):
    """Tracks ranked by units sold."""

    count: int
    tracks: list[TrackSales]


class ArtistRevenue(Sales):
    """Units sold and revenue for one artist."""

    ArtistId: int
    ArtistName: str | None
    UnitsSold: int
    Revenue: Decimal


class TopArtistsOutput(Sales):
    """Artists ranked by revenue."""

    count: int
    artists: list[ArtistRevenue]


class CustomerSpend(Sales):
    """Total spend for one customer."""

    CustomerId: int
    CustomerName: str
    Country: str | None
    InvoiceCount: int
    TotalSpent: Decimal


class TopCustomersOutput(Sales):
    """Customers ranked by total spend."""

    count: int
    customers: list[CustomerSpend]


class CustomerLifetimeValueOutput(Sales):
    """A customer's lifetime purchasing summary."""

    found: bool
    CustomerId: int
    CustomerName: str
    Email: str
    Country: str | None
    InvoiceCount: int
    TotalSpent: Decimal
    AverageInvoiceValue: Decimal
    TracksPurchased: int
    FirstPurchaseDate: str | None
    LastPurchaseDate: str | None
