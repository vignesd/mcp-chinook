from sqlalchemy.exc import SQLAlchemyError
from mcp.server.mcpserver.exceptions import ToolError

from core.logging import logger
from models.employee_models import (
    EmployeeDetailsOutput,
    EmployeeListOutput,
    EmployeeSalesSummaryOutput,
)
from services.employee_services import (
    get_employee_details as fetch_employee_details,
    get_employee_sales_summary as fetch_employee_sales_summary,
    list_employees as fetch_employees,
)


async def list_employees() -> EmployeeListOutput:
    """List all Chinook employees with their titles and managers."""

    try:
        employees = await fetch_employees()

    except SQLAlchemyError:
        logger.exception("Database failure listing employees")
        raise ToolError("DATABASE_ERROR: Unable to list employees because a "
                        "database operation failed. Retry at most twice with "
                        "a short delay. If the error persists, stop and report "
                        "the issue to the user.") from None

    return EmployeeListOutput(
        count=len(employees),
        employees=employees,  # type:ignore
    )


async def get_employee_details(employee_id: int) -> EmployeeDetailsOutput:
    """Get an employee by EmployeeId. If the ID is invalid, correct the input
    before retrying. If the employee does not exist, do not retry the same ID.
    Retry database failures only when they are transient."""
    if employee_id < 1:
        raise ToolError("INVALID_ARGUMENT: employee_id must be a positive integer. "
                        "Provide an employee_id greater than or equal to 1. "
                        "Do not retry with the same invalid value.")

    try:
        details = await fetch_employee_details(employee_id)

    except SQLAlchemyError:
        logger.exception(
            "Database failure fetching employee_id=%s", employee_id)
        raise ToolError("DATABASE_ERROR: Unable to retrieve the employee because "
                        "a database operation failed. Retry at most twice with "
                        "a short delay. If the error persists, stop and report "
                        "the issue to the user.") from None

    if details is None:
        raise ToolError(f"NOT_FOUND: No employee exists with employee_id={employee_id}. "
                        "Do not retry the same ID. Use list_employees to find "
                        "valid employee IDs.")

    return EmployeeDetailsOutput(
        found=True,
        employee=details["employee"],
        direct_report_count=len(details["direct_reports"]),
        direct_reports=details["direct_reports"],
    )


async def get_employee_sales_summary(
    employee_id: int,
) -> EmployeeSalesSummaryOutput:
    """Get sales totals for the customers an employee supports. If the ID is
    invalid, correct the input before retrying. If the employee does not exist,
    do not retry the same ID. Retry database failures only when they are
    transient."""
    if employee_id < 1:
        raise ToolError("INVALID_ARGUMENT: employee_id must be a positive integer. "
                        "Provide an employee_id greater than or equal to 1. "
                        "Do not retry with the same invalid value.")

    try:
        summary = await fetch_employee_sales_summary(employee_id)

    except SQLAlchemyError:
        logger.exception(
            "Database failure fetching sales summary for employee_id=%s",
            employee_id,
        )
        raise ToolError("DATABASE_ERROR: Unable to retrieve the sales summary "
                        "because a database operation failed. Retry at most "
                        "twice with a short delay. If the error persists, stop "
                        "and report the issue to the user.") from None

    if summary is None:
        raise ToolError(f"NOT_FOUND: No employee exists with employee_id={employee_id}. "
                        "Do not retry the same ID. Use list_employees to find "
                        "valid employee IDs.")

    return EmployeeSalesSummaryOutput(found=True, **summary)
