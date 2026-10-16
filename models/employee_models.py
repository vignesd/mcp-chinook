from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class Employee(BaseModel):
    """Employee base model."""

    model_config = ConfigDict(extra="forbid")


class EmployeeSummary(Employee):
    """Short employee record used in listings."""

    EmployeeId: int
    FirstName: str
    LastName: str
    Title: str | None
    ReportsTo: int | None
    ManagerName: str | None
    City: str | None
    Country: str | None
    Email: str | None


class DirectReport(Employee):
    """An employee who reports to another employee."""

    EmployeeId: int
    FirstName: str
    LastName: str
    Title: str | None


class EmployeeRecord(Employee):
    """Full employee record."""

    EmployeeId: int
    FirstName: str
    LastName: str
    Title: str | None
    ReportsTo: int | None
    ManagerName: str | None
    BirthDate: str | None
    HireDate: str | None
    Address: str | None
    City: str | None
    State: str | None
    Country: str | None
    PostalCode: str | None
    Phone: str | None
    Fax: str | None
    Email: str | None
    CustomerCount: int


class EmployeeListOutput(Employee):
    """All employees in the company."""

    count: int
    employees: list[EmployeeSummary]


class EmployeeDetailsOutput(Employee):
    """An employee with their direct reports."""

    found: bool
    employee: EmployeeRecord
    direct_report_count: int
    direct_reports: list[DirectReport]


class EmployeeSalesSummaryOutput(Employee):
    """Sales totals for customers supported by an employee."""

    found: bool
    EmployeeId: int
    EmployeeName: str
    Title: str | None
    CustomerCount: int
    InvoiceCount: int
    TotalSales: Decimal
    AverageInvoiceValue: Decimal
    FirstSaleDate: str | None
    LastSaleDate: str | None
