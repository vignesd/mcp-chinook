from models.invoice_models import (
    CustomerInvoiceOutput,
    CustomerInvoice,
    CustomerPurchaseOutput,
    CustomerPurchase,
    InvoiceDetailsOutput,
)
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from mcp.server.mcpserver.exceptions import ToolError

from services.Invoice_services import (
    get_invoices,
    get_invoice_tracks,
    get_invoice_details as fetch_invoice_details,
)

from core.logging import logger
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError


async def get_customer_invoices(customer_id: int) -> CustomerInvoiceOutput:
    """Retrieve all invoices for a customer by CustomerId.

    If the customer ID is invalid, correct the input before retrying.
    If the customer does not exist, do not retry the same customer ID.
    Retry database failures only when they are transient.
    """
    try:

        invoices = await get_invoices(customer_id)
        if invoices is None:
            raise ToolError(
                f"NOT_FOUND: No customer exists with customer_id={customer_id}. "
                "Do not retry the same customer ID."
            )
        validated_invoices = [invoice if isinstance(
            invoice, CustomerInvoice) else CustomerInvoice.model_validate(invoice) for invoice in invoices]

        return CustomerInvoiceOutput(
            found=True,
            customer_id=customer_id,
            invoices=invoices,  # type:ignore
            total_invoices=len(validated_invoices),
        )

    except ToolError:
        raise

    except ValidationError:
        raise ToolError(
            "INVALID_ARGUMENT: Customer ID must be a valid positive integer."
        ) from None

    except SQLAlchemyError:
        logger.exception(
            "Database failure fetching invoices for customer_id=%s",
            customer_id,
        )
        raise ToolError(
            "DATABASE_ERROR: Unable to retrieve customer invoices because "
            "a database operation failed. Retry at most twice with a short "
            "delay only if the error is transient. If the error persists, "
            "stop and report the issue to the user."
        ) from None

    except Exception:
        logger.exception(
            "Unexpected error fetching invoices for customer_id=%s",
            customer_id,
        )
        raise ToolError(
            "INTERNAL_ERROR: An unexpected error occurred while retrieving "
            "customer invoices. Do not retry repeatedly. Report the issue "
            "to the user if it persists."
        ) from None


async def get_customer_purchase_tracks(
    customer_id: int,
) -> CustomerPurchaseOutput:
    """Retrieve purchased tracks for a customer by CustomerId."""

    try:

        purchases = await get_invoice_tracks(customer_id)

        if purchases is None:
            raise ToolError(
                f"NOT_FOUND: No customer exists with "
                f"customer_id={customer_id}."
            )

        return CustomerPurchaseOutput(
            found=True,
            customer_id=customer_id,
            purchases=purchases,  # type:ignore
            total_purchases=len(purchases),  # type:ignore
        )

    except ToolError:
        raise

    except SQLAlchemyError:
        logger.exception(
            "Database failure fetching purchase tracks for customer_id=%s",
            customer_id,
        )
        raise ToolError(
            "DATABASE_ERROR: Unable to retrieve customer purchase tracks."
        ) from None

    except Exception:
        logger.exception(
            "Unexpected error retrieving purchase tracks for customer_id=%s",
            customer_id,
        )
        raise ToolError(
            "INTERNAL_ERROR: Unable to retrieve customer purchase tracks."
        ) from None


async def get_invoice_details(invoice_id: int) -> InvoiceDetailsOutput:
    """Retrieve an invoice and its line items by InvoiceId.

    If the invoice ID is invalid, correct the input before retrying.
    If the invoice does not exist, do not retry the same invoice ID.
    Retry database failures only when they are transient.
    """
    if invoice_id < 1:
        raise ToolError("INVALID_ARGUMENT: invoice_id must be a positive integer. "
                        "Provide an invoice_id greater than or equal to 1. "
                        "Do not retry with the same invalid value.")
    try:
        details = await fetch_invoice_details(invoice_id)

        if details is None:
            raise ToolError(
                f"NOT_FOUND: No invoice exists with invoice_id={invoice_id}. "
                "Do not retry the same ID. Use get_customer_invoices to find "
                "valid invoice IDs for a customer."
            )

        return InvoiceDetailsOutput(
            found=True,
            invoice=details["invoice"],
            line_count=len(details["lines"]),
            lines=details["lines"],
        )

    except ToolError:
        raise

    except SQLAlchemyError:
        logger.exception(
            "Database failure fetching invoice_id=%s",
            invoice_id,
        )
        raise ToolError(
            "DATABASE_ERROR: Unable to retrieve the invoice because a "
            "database operation failed. Retry at most twice with a short "
            "delay. If the error persists, stop and report the issue to "
            "the user."
        ) from None

    except Exception:
        logger.exception(
            "Unexpected error fetching invoice_id=%s",
            invoice_id,
        )
        raise ToolError(
            "INTERNAL_ERROR: An unexpected error occurred while retrieving "
            "the invoice. Do not retry repeatedly. Report the issue to the "
            "user if it persists."
        ) from None
