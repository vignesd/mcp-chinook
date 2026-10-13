from pydantic import AliasChoices, Field, BaseModel, ConfigDict, EmailStr
from datetime import datetime
from decimal import Decimal
from typing import List


class Invoice(BaseModel):
    """Invoice base model."""

    model_config = ConfigDict(extra="forbid")


class CustomerInvoice(Invoice):
    """Customer invoice details response model."""

    model_config = ConfigDict(extra="forbid")

    InvoiceId: int
    CustomerId: int
    FirstName: str
    LastName: str
    Email: EmailStr
    InvoiceDate: str
    BillingAddress: str
    BillingCity: str
    BillingState: str | None
    BillingCountry: str
    BillingPostalCode: str | None
    Total: Decimal


class CustomerInvoiceOutput(BaseModel):
    """Structured response containing a customer's invoices."""

    model_config = ConfigDict(extra="forbid")

    found: bool
    customer_id: int
    total_invoices: int
    invoices: list[CustomerInvoice]


class CustomerPurchase(Invoice):
    """Customer invoice line and purchase history response."""

    model_config = ConfigDict(extra="forbid")

    InvoiceId: int
    InvoiceDate: str
    CustomerId: int
    CustomerName: str
    BillingCountry: str
    TrackName: str
    UnitPrice: Decimal
    Quantity: int
    LineTotal: Decimal
    InvoiceTotal: Decimal


class CustomerPurchaseOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    found: bool
    customer_id: int
    total_purchases: int
    purchases: List[CustomerPurchase]
