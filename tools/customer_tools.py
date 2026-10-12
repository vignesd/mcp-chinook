
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from mcp.server.mcpserver.exceptions import ToolError
from models.customer_models import (
    CustomerData,
    GetCustomerInput,
    CustomerOutput
)
from services.customer_services import (
    get_customer_by_email
)
from core.logging import logger


async def get_customer(customer_email: str) -> CustomerOutput:
    """Get an album by its ID. If the ID is invalid, correct the input before retrying. 
    If the album does not exist, do not retry the same ID. Retry database failures only when they are transient. """
    try:
        validated_input = GetCustomerInput(cusotmer_emailId=customer_email)
        customer = await get_customer_by_email(validated_input.cusotmer_emailId)

    except ValidationError:
        raise ToolError(
            "INVALID_ARGUMENT: Customer email id should be valid."
        ) from None

    except SQLAlchemyError:
        logger.exception(
            "Database failure fetching email_id=%s", customer_email)
        raise ToolError("DATABASE_ERROR: Unable to retrieve the album because "
                        "a database operation failed. Retry at most twice with "
                        "a short delay. If the error persists, stop and report "
                        "the issue to the user.") from None
    if customer is None:
        raise ToolError(f"NOT_FOUND: No customer exists with email_id={customer_email}. "
                        "Do not retry the same Email ID.")

    return CustomerOutput(
        found=True,
        customer=customer
    )
