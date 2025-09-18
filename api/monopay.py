from aiohttp import ClientSession

from utils.schemas.payment import CreateInvoiceResponse, GetInvoiceStatusResponse


class MonoPay:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.monobank.ua/api/merchant/invoice"


    async def create_invoice(self, amount: int, order_id: int, webhook_url: str) -> CreateInvoiceResponse | None:
        endpoint = f"{self.base_url}/create"
        headers = self._default_headers()

        payload = {
            "amount": amount, # Сумма в копейках
            "ccy": 980, # Код валюты как ISO 4217. 980 = UAH
            "merchantPaymInfo": {
                "reference": order_id, # Номер чека, заказа и т.д.; определяется мерчантом
                "destination": f"Оплата заказа #{order_id}", # Назначение платежа
            },
            "redirectUrl": "", # URL для перенаправления
            "webHookUrl": webhook_url, # URL для уведомлений
            "validity": 3600 # Время жизни инвойса в секундах
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

