import json
import logging

from aiohttp.client import ClientSession
from aiohttp.web import Application, Request, Response, json_response

from utils.schemas.payment import CreateInvoiceResponse, GetInvoiceStatusResponse


class MonoPayAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.monobank.ua/api/merchant/invoice"

    async def create_invoice(self, amount: int, order_id: int, webhook_url: str) -> CreateInvoiceResponse | None:
        endpoint = f"{self.base_url}/create"
        headers = self._default_headers()

        payload = {
            "amount": amount,  # Сумма в копейках
            "ccy": 980,  # Код валюты как ISO 4217. 980 = UAH
            "merchantPaymInfo": {
                "reference": order_id,  # Номер чека, заказа и т.д.; определяется мерчантом
                "destination": f"Оплата заказа #{order_id}",  # Назначение платежа
            },
            "redirectUrl": "",  # URL для перенаправления
            "webHookUrl": webhook_url,  # URL для уведомлений
            "validity": 3600  # Время жизни инвойса в секундах
        }

        async with ClientSession() as session:
            async with session.post(endpoint, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return CreateInvoiceResponse(id=data["invoiceId"], url=data["pageUrl"])

                print(f"Error creating invoice: {response.status} - {await response.text()}")
                return None

    async def check_invoice_status(self, invoice_id: str):
        endpoint = f"{self.base_url}/status?invoiceId={invoice_id}"
        headers = self._default_headers()

        async with ClientSession() as session:
            async with session.get(endpoint, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return GetInvoiceStatusResponse(
                        id=data["invoiceId"],
                        status=data["status"],
                        failure_reason=data["failureReason"],
                        error_code=data["errCode"],
                        amount=data["amount"],
                        ccy=data["ccy"],
                        final_amount=data["finalAmount"],
                        created_date=data["createdDate"],
                        modified_date=data["modifiedDate"],
                        reference=data["reference"],
                        destination=data["destination"],
                    )

                print(f"Error checking invoice status: {response.status} - {await response.text()}")
                return None

    def _default_headers(self) -> dict[str, str]:
        return {"X-Token": self.api_key}


api = MonoPayAPI("")


# async def handle_webhook(request: Request) -> Response:
#     try:
#         data = await request.json()
#
#         logging.info(f"Received webhook data: {json.dumps(data, indent=2)}")
#
#         invoice_id = data.get("invoiceId")
#         status = data.get("status")
#         reference = data.get("reference")
#         amount = data.get("amount")
#
#         if not invoice_id:
#             logging.error("Invoice ID not found in webhook data")
#             return json_response({"error": "Invoice ID required"}, status=400)
#
#         match status:
#             case "success":
#                 logging.info(f"Payment successful for invoice {invoice_id}, order {reference}")
#             case "failure":
#                 logging.info(f"Payment failed for invoice {invoice_id}, order {reference}")
#             case "processing":
#                 logging.info(f"Payment processing for invoice {invoice_id}, order {reference}")
#             case _:
#                 logging.error(f"Unknown status {status} for invoice {invoice_id}, order {reference}")
#
#         return json_response({"status": "ok"})
#
#     except json.JSONDecodeError:
#         logging.error("Invalid JSON in webhook request")
#         return json_response({"error": "Invalid JSON"}, status=400)
#     except Exception as e:
#         logging.error(f"Error processing webhook: {str(e)}")
#         return json_response({"error": "Internal server error"}, status=500)
#
# def create_app() -> Application:
#     app = Application()
#     app.router.add_post("/webhook/monopay", handle_webhook)
#
#     return app