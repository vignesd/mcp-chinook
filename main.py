# import asyncio

# # from services.customer_services import get_customer_by_email
# # from services.Invoice_services import get_invoices, get_invoice_tracks

# from core.database import close_database
# from tools.album_tools import health_check, get_album
# from tools.customer_tools import get_customer_by_email
# from tools.invoice_tools import get_customer_purchase_tracks, get_customer_invoices

from models.invoice_models import CustomerInvoiceOutput, CustomerPurchaseOutput, CustomerInvoice
# import json

from datetime import datetime
from pydantic import BaseModel


# class DateTest(BaseModel):
#     InvoiceDate: datetime


# result = DateTest.model_validate({
#     "InvoiceDate": "2025-11-13T00:00:00"
# })

# print(result.model_dump(mode="json"))

result = CustomerInvoiceOutput.model_validate({
    "found": True,
    "customer_id": 6,
    "total_invoices": 1,
    "invoices": [
        {
            "InvoiceId": 404,
            "CustomerId": 6,
            "FirstName": "Helena",
            "LastName": "Holý",
            "Email": "hholy@gmail.com",
            "InvoiceDate": "2025-11-13T00:00:00",
            "BillingAddress": "Rilská 3174/6",
            "BillingCity": "Prague",
            "BillingState": None,
            "BillingCountry": "Czech Republic",
            "BillingPostalCode": "14300",
            "Total": "25.86",
        }
    ],
})

print(result.model_dump(mode="json"))

# async def main():
#     try:
#         # print((await health_check()).model_dump())
#         # print((await get_album(1)).model_dump())
#         # print((await get_customer_by_email('luisg@embraer.com.br')).model_dump())
#         # print((await get_customer_purchase_tracks(12)).model_dump_json(indent=2))
#         # print((await get_customer_invoices(6)).model_dump_json(indent=2))
#         # schema = CustomerInvoiceOutput.model_json_schema(by_alias=False)
#         # print(schema["$defs"]["CustomerInvoice"]["properties"].keys())
#         print(json.dumps(CustomerInvoice.model_json_schema(), indent=2))
#     finally:
#         await close_database()


# if __name__ == "__main__":
#     asyncio.run(main())
