# import json
# from json import JSONDecodeError
#
# from aiohttp.client import ClientSession
# from fastapi import Request, HTTPException, FastAPI
# from fastapi.responses import JSONResponse
#
# from config import MONOPAY_TOKEN
# from utils.schemas.payment import CreateInvoiceResponse, GetInvoiceStatusResponse, CreateInvoiceRequest
#
#
# class MonoPayAPI:
#     def __init__(self, api_key: str):
#         self.api_key = api_key
#         self.base_url = "https://api.monobank.ua/api/merchant/invoice"
#
#     async def create_invoice(self, amount: int, order_id: int, webhook_url: str) -> CreateInvoiceResponse | None:
#         endpoint = f"{self.base_url}/create"
#         headers = self._default_headers()
#
#         payload = {
#             "amount": amount,  # Сумма в копейках
#             "ccy": 980,  # Код валюты как ISO 4217. 980 = UAH
#             "merchantPaymInfo": {
#                 "reference": order_id,  # Номер чека, заказа и т.д.; определяется мерчантом
#                 "destination": f"Оплата заказа #{order_id}",  # Назначение платежа
#             },
#             "redirectUrl": "",  # URL для перенаправления
#             "webHookUrl": webhook_url,  # URL для уведомлений
#             "validity": 3600  # Время жизни инвойса в секундах
#         }
#
#         async with ClientSession() as session:
#             async with session.post(endpoint, json=payload, headers=headers) as response:
#                 if response.status == 200:
#                     data = await response.json()
#                     return CreateInvoiceResponse(id=data["invoiceId"], url=data["pageUrl"])
#
#                 print(f"[ERROR] Error creating invoice: {response.status} - {await response.text()}")
#                 return None
#
#     async def check_invoice_status(self, invoice_id: str) -> GetInvoiceStatusResponse | None:
#         endpoint = f"{self.base_url}/status?invoiceId={invoice_id}"
#         headers = self._default_headers()
#
#         async with ClientSession() as session:
#             async with session.get(endpoint, headers=headers) as response:
#                 if response.status == 200:
#                     data = await response.json()
#                     return GetInvoiceStatusResponse(
#                         id=data["invoiceId"],
#                         status=data["status"],
#                         failure_reason=data["failureReason"],
#                         error_code=data["errCode"],
#                         amount=data["amount"],
#                         ccy=data["ccy"],
#                         final_amount=data["finalAmount"],
#                         created_date=data["createdDate"],
#                         modified_date=data["modifiedDate"],
#                         reference=data["reference"],
#                         destination=data["destination"],
#                     )
#
#                 print(f"[ERROR] Error checking invoice status: {response.status} - {await response.text()}")
#                 return None
#
#     def _default_headers(self) -> dict[str, str]:
#         return {"X-Token": self.api_key}
#
#
# api = MonoPayAPI(MONOPAY_TOKEN)
#
# app = FastAPI(title="Monopay API")
#
#
# @app.post("/webhook")
# async def handle_webhook(request: Request) -> JSONResponse:
#     try:
#         data = await request.json()
#         print(f"[INFO] Received webhook data: {json.dumps(data, indent=2)}")
#
#         invoice_id = data.get("invoiceId")
#         status = data.get("status")
#         reference = data.get("reference")
#
#         if not invoice_id:
#             print("[ERROR] Invoice ID not found in webhook data.")
#             raise HTTPException(status_code=400, detail="Invalid Invoice ID")
#
#         match status:
#             case "success":
#                 print(f"[MONO_SUCCESS] Payment successful for invoice {invoice_id}, order {reference}")
#                 pass
#             case "failure":
#                 print(f"[MONO_WARN] Payment failed for invoice {invoice_id}, order {reference}")
#                 pass
#             case "processing":
#                 print(f"[MONO_INFO] Payment processing for invoice {invoice_id}, order {reference}")
#             case _:
#                 print(f"[MONO_ERROR] Unknown status {status} for invoice {invoice_id}, order {reference}")
#
#         return JSONResponse(content={"status": "ok"})
#
#     except JSONDecodeError:
#         print("[ERROR] Invalid JSON in webhook request")
#         raise HTTPException(status_code=400, detail="Invalid JSON")
#     except Exception as e:
#         print(f"[ERROR] Error processing webhook: {str(e)}")
#         return HTTPException(status_code=500, detail="Internal Server Error")
#
#
# @app.post("/invoice")
# async def create_invoice(request: CreateInvoiceRequest) -> JSONResponse:
#     result = await api.create_invoice(request.amount, request.order_id, request.webhook_url)
#     if result:
#         return JSONResponse(content=result.model_dump_json(), status_code=201)
#
#     raise HTTPException(status_code=500, detail="failed to create invoice")
#
#
# @app.get("/invoice/{invoice_id}")
# async def get_invoice_status(invoice_id: int) -> JSONResponse:
#     result = await api.check_invoice_status(invoice_id)
#     if result:
#         return JSONResponse(content=result.model_dump_json(), status_code=200)
#
#     raise HTTPException(status_code=500, detail="failed to get invoice status")
#
#
# @app.get("/health")
# async def health_check() -> JSONResponse:
#     return JSONResponse(content={"status": "healthy"}, status_code=200)
