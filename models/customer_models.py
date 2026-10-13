
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Any, Literal, List


class Customer(BaseModel):
    pass


class GetCustomerInput(Customer):
    model_config = ConfigDict(extra="forbid")

    cusotmer_emailId: EmailStr = Field(...,
                                       description="Customer email id.",
                                       )


class CustomerData(Customer):
    """Customer information and contact details."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )

    customer_id: int = Field(
        ...,
        alias="CustomerId",
        gt=0,
        description="Unique identifier assigned to the customer.",
    )

    first_name: str = Field(
        ...,
        alias="FirstName",
        min_length=1,
        max_length=100,
        description="Customer's first or given name.",
    )

    last_name: str = Field(
        ...,
        alias="LastName",
        min_length=1,
        max_length=100,
        description="Customer's last or family name.",
    )

    company: str | None = Field(
        default=None,
        alias="Company",
        max_length=200,
        description="Company or organization associated with the customer.",
    )

    address: str | None = Field(
        default=None,
        alias="Address",
        max_length=255,
        description="Customer's street address.",
    )

    city: str | None = Field(
        default=None,
        alias="City",
        max_length=100,
        description="City where the customer resides or the company is located.",
    )

    state: str | None = Field(
        default=None,
        alias="State",
        max_length=100,
        description="State, province, or regional subdivision.",
    )

    country: str | None = Field(
        default=None,
        alias="Country",
        max_length=100,
        description="Country where the customer resides or the company is located.",
    )

    postal_code: str | None = Field(
        default=None,
        alias="PostalCode",
        max_length=20,
        description="Postal or ZIP code. Stored as text to preserve leading zeros.",
    )

    phone: str | None = Field(
        default=None,
        alias="Phone",
        max_length=30,
        description="Customer's contact telephone number, including country code.",
    )

    email: EmailStr = Field(...,
                            alias="Email",
                            description="Customer's email address, validated using EmailStr.",
                            )


class CustomerOutput(Customer):
    model_config = ConfigDict(extra="forbid")

    found: bool
    customer: dict[str, Any] | None


class CustomerListOutput(Customer):
    model_config = ConfigDict(extra="forbid")

    found: bool
    customer: List[dict[str, Any]] | None
