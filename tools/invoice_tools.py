from models.invoice_models import (
    CustomerInvoiceOutput,
    CustomerInvoice,
    CustomerPurchaseOutput,
    CustomerPurchase
)
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from mcp.server.mcpserver.exceptions import ToolError

from services.Invoice_services import get_invoices, get_invoice_tracks

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
