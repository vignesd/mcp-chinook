
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from mcp.server.mcpserver.exceptions import ToolError
from models.customer_models import (
    CustomerData,
    GetCustomerInput,
    CustomerOutput,
    CustomerListOutput
)
from services.customer_services import (
    get_customer_by_email as get_by_email,
    get_customer_by_id as get_by_id,
    search_customers_by_keyword,
    get_customer_count as get_count
)
from core.logging import logger


async def get_customer_by_email(customer_email: str) -> CustomerOutput:
    """Get an customer by its EmailID. If the EmailID is invalid, correct the input before retrying. 
    If the customer does not exist, do not retry the same EmailID. Retry database failures only when they are transient. """
    try:
        validated_input = GetCustomerInput(cusotmer_emailId=customer_email)
        customer = await get_by_email(validated_input.cusotmer_emailId)

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


async def get_customer_by_id(customer_id: int) -> CustomerOutput:
    """Get an customer by its EmailID. If the EmailID is invalid, correct the input before retrying. 
    If the customer does not exist, do not retry the same EmailID. Retry database failures only when they are transient. """
    try:
        customer = await get_by_id(customer_id)

    except ValidationError:
        raise ToolError(
            "INVALID_ARGUMENT: Customer email id should be valid."
        ) from None

    except SQLAlchemyError:
        logger.exception(
            "Database failure fetching customer_id=%s", customer_id)
        raise ToolError("DATABASE_ERROR: Unable to retrieve the album because "
                        "a database operation failed. Retry at most twice with "
                        "a short delay. If the error persists, stop and report "
                        "the issue to the user.") from None
    if customer is None:
        raise ToolError(f"NOT_FOUND: No customer exists with customer_id={customer_id}. "
                        "Do not retry the same Email ID.")

    return CustomerOutput(
        found=True,
        customer=customer
    )


async def search_customer(keyword: str) -> CustomerListOutput:
    """Search customers by keyword (FirstName or LastName or Company).
    Retry database failures only when they are transient. """
    try:
        customer = await search_customers_by_keyword(keyword)

    except ValidationError:
        raise ToolError(
            "INVALID_ARGUMENT: Keyword should be valid."
        ) from None

    except SQLAlchemyError:
        logger.exception(
            "Database failure fetching customers by keyword =%s", keyword)
        raise ToolError("DATABASE_ERROR: Unable to retrieve the album because "
                        "a database operation failed. Retry at most twice with "
                        "a short delay. If the error persists, stop and report "
                        "the issue to the user.") from None
    if customer is None:
        raise ToolError(f"NOT_FOUND: No customers exists with keyword ={keyword}. "
                        "Do not retry the same Email ID.")

    return CustomerListOutput(
        found=True,
        customer=customer
    )


async def get_customers_count() -> int:
    """Get coustomers count"""

    try:
        customer_count = 0
        customer_count = await get_count()
    except SQLAlchemyError:
        logger.exception(
            "Database failure fetching customers count")
        raise ToolError("DATABASE_ERROR: Unable to retrieve the customer count "
                        "a database operation failed. Retry at most twice with "
                        "a short delay. If the error persists, stop and report "
                        "the issue to the user.") from None

    return customer_count  # type:ignore
