from fastapi import APIRouter, HTTPException, Request, Header, Depends
from pydantic import BaseModel
from typing import Optional
import logging

from config import API_TOKEN

router = APIRouter()

async def verify_api_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization[7:] 
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")
    
    return token

# Схема для данных инвойса от сайта
class InvoiceNotificationData(BaseModel):
    timestamp: int
    order_id: int
    order_total: float
    order_currency: str
    customer_email: str
    customer_phone: Optional[str] = None
    invoice_data: dict  # Весь объект инвойса от MonoPay
    site_url: str

# # # POST эндпоинт для webhook платежей
# # @router.post("/webhook")
# # async def payment_webhook(data: PaymentWebhook):
#     ...

# POST эндпоинт для приема данных об инвойсе от сайта (БЕЗ ТОКЕНА)
@router.post("/invoice-created")
async def receive_invoice_notification(request: Request):
    """Принимаем уведомление о создании инвойса от WordPress сайта"""
    
    try:
        # Получаем весь объект как есть
        data = await request.json()
        
        # Принтим в консоль тоже
        print("="*50)
        print("ПОЛУЧЕНЫ ДАННЫЕ ОБ ИНВОЙСЕ:")
        print(f"Полный объект: {data}")
        
        # Разбираем основные поля из запроса
        if 'invoice' in data:
            print(f"Invoice данные: {data['invoice']}")
        if 'order_id' in data:
            print(f"Order ID: {data['order_id']}")
        if 'order_total' in data:
            print(f"Order Total: {data['order_total']}")
        if 'timestamp' in data:
            print(f"Timestamp: {data['timestamp']}")
        
        print("="*50)
        
        return {
            "status": "success", 
            "message": "Invoice notification received and logged",
            "received_data": data
        }
        
    except Exception as e:
        logging.error(f"Ошибка обработки инвойса: {e}")
        print(f"ОШИБКА: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# Универсальный эндпоинт для отладки (без токена)
@router.post("/debug-webhook")
async def debug_webhook(request: Request):
    """Отладочный эндпоинт для анализа любых данных"""
    
    try:
        json_data = await request.json()
        logging.info(f"DEBUG - JSON данные: {json_data}")
    except:
        json_data = None
    
    headers = dict(request.headers)
    logging.info(f"DEBUG - Headers: {headers}")
    
    return {
        "message": "DEBUG: Данные получены",
        "received_json": json_data,
        "received_headers": headers
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