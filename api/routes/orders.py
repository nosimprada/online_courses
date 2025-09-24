from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import logging


router = APIRouter()

# # # POST эндпоинт для webhook платежей
# # @router.post("/webhook")
# # async def payment_webhook(data: PaymentWebhook):
#     ...

# POST эндпоинт для создания инвойса
@router.post("/create-subscription")
async def create_invoice(invoice_data: CreateInvoiceRequest):
    """Создание нового инвойса"""
    # Логика создания инвойса
    return {
        "invoice_id": 12345,
        "status": "created",
        "payment_url": "https://payment.link/12345"
    }

# GET эндпоинт для получения информации о заказе
@router.get("/order/{order_id}")
async def get_order(order_id: int):
    """Получить информацию о заказе"""
    return {
        "order_id": order_id,
        "status": "paid",
        "amount": 1000.0
    }