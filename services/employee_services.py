from core.database import engine
from sqlalchemy import text
from typing import Any


async def list_employees() -> list[dict[str, Any]]:
    """Return all employees with their manager's name."""

    query = text("""SELECT
    e.EmployeeId,
    e.FirstName,
    e.LastName,
    e.Title,
    e.ReportsTo,
    m.FirstName || ' ' || m.LastName AS ManagerName,
    e.City,
    e.Country,
    e.Email
FROM Employee AS e
LEFT JOIN Employee AS m
    ON m.EmployeeId = e.ReportsTo
ORDER BY e.EmployeeId;
""")

    async with engine.connect() as conn:
        result = await conn.execute(query)
        return [dict(row) for row in result.mappings().all()]


async def get_employee_details(employee_id: int) -> dict[str, Any] | None:
    """Return an employee with manager, direct reports, and customer count."""

    employee_query = text("""SELECT
    e.EmployeeId,
    e.FirstName,
    e.LastName,
    e.Title,
    e.ReportsTo,
    m.FirstName || ' ' || m.LastName AS ManagerName,
    e.BirthDate,
    e.HireDate,
    e.Address,
    e.City,
    e.State,
    e.Country,
    e.PostalCode,
    e.Phone,
    e.Fax,
    e.Email,
    (SELECT COUNT(*) FROM Customer AS c
        WHERE c.SupportRepId = e.EmployeeId) AS CustomerCount
FROM Employee AS e
LEFT JOIN Employee AS m
    ON m.EmployeeId = e.ReportsTo
WHERE e.EmployeeId = :employee_id;
""")

    reports_query = text("""SELECT
    EmployeeId,
    FirstName,
    LastName,
    Title
FROM Employee
WHERE ReportsTo = :employee_id
ORDER BY EmployeeId;
""")

    async with engine.connect() as conn:
        employee_result = await conn.execute(
            employee_query,
            {"employee_id": employee_id}
        )
        employee = employee_result.mappings().first()

        if employee is None:
            return None

        reports_result = await conn.execute(
            reports_query,
            {"employee_id": employee_id}
        )
        direct_reports = [dict(row) for row in reports_result.mappings().all()]

    return {"employee": dict(employee), "direct_reports": direct_reports}


async def get_employee_sales_summary(employee_id: int) -> dict[str, Any] | None:
    """Return sales totals for customers supported by an employee.

    Chinook attributes sales to the employee assigned as the customer's
    support representative (Customer.SupportRepId).
    """

    employee_query = text("""SELECT
    EmployeeId,
    FirstName || ' ' || LastName AS EmployeeName,
    Title
FROM Employee
WHERE EmployeeId = :employee_id;
""")

    summary_query = text("""SELECT
    COUNT(DISTINCT c.CustomerId) AS CustomerCount,
    COUNT(i.InvoiceId) AS InvoiceCount,
    COALESCE(ROUND(SUM(i.Total), 2), 0) AS TotalSales,
    COALESCE(ROUND(AVG(i.Total), 2), 0) AS AverageInvoiceValue,
    MIN(i.InvoiceDate) AS FirstSaleDate,
    MAX(i.InvoiceDate) AS LastSaleDate
FROM Customer AS c
LEFT JOIN Invoice AS i
    ON i.CustomerId = c.CustomerId
WHERE c.SupportRepId = :employee_id;
""")

    async with engine.connect() as conn:
        employee_result = await conn.execute(
            employee_query,
            {"employee_id": employee_id}
        )
        employee = employee_result.mappings().first()

        if employee is None:
            return None

        summary_result = await conn.execute(
            summary_query,
            {"employee_id": employee_id}
        )
        summary = summary_result.mappings().one()

    return {**dict(employee), **dict(summary)}
