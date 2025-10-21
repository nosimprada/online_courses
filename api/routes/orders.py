import logging

from fastapi import APIRouter, HTTPException, Request, Header

from config import API_TOKEN
from utils.email import send_course_access_email, send_email
from utils.enums.order import OrderStatus
from utils.schemas.order import OrderCreateSchemaDB
from utils.schemas.subscription import SubscriptionCreateSchemaDB
from utils.services.order import create_invoice_order_token_code, get_order_by_order_id, update_order_status
from utils.services.redeem_token import get_redeem_token_by_order_id
from utils.services.short_code import get_short_code_by_order_id
from utils.services.subscription import create_subscription, get_subscription_by_order_id

router = APIRouter()


async def verify_api_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    token = authorization[7:]
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")

    return token


# POST эндпоинт для приема данных об инвойсе от сайта (БЕЗ ТОКЕНА)
@router.post("/invoice-created")
async def receive_invoice_notification(request: Request):
    """Принимаем уведомление о создании инвойса от WordPress сайта"""

    try:
        data = await request.json()

        print("=" * 50)
        print("ПОЛУЧЕНЫ ДАННЫЕ ОБ ИНВОЙСЕ:")
        print(f"Полный объект: {data}")

        if 'invoice' in data:
            print(f"Invoice данные: {data['invoice']}")
        if 'order_id' in data:
            print(f"Order ID: {data['order_id']}")
        if 'order_total' in data:
            print(f"Order Total: {data['order_total']}")
        if 'timestamp' in data:
            print(f"Timestamp: {data['timestamp']}")

        print("=" * 50)
        invoice_id = data.get('invoice', {}).get('invoiceId', '') if isinstance(data.get('invoice'), dict) else str(
            data.get('invoice', ''))
        customer_email = data.get('customer_email', '')

        order_data = OrderCreateSchemaDB(
            amount=float(data.get('order_total', 0)),
            order_id=int(data.get('order_id', 0)),
            invoice_id=invoice_id,
            email=customer_email
        )

        print(await create_invoice_order_token_code(order_data))

        return {
            "status": "success",
            "message": "Invoice notification received and logged",
            "received_data": data
        }

    except Exception as e:
        logging.error(f"Ошибка обработки инвойса: {e}")
        print(f"ОШИБКА: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# POST эндпоинт для получения уведомления об успешной оплате
@router.post("/payment-completed")
async def payment_completed(request: Request):
    """Принимаем уведомление об успешной оплате от WordPress сайта"""

    try:
        data = await request.json()

        print("=" * 50)
        print("ПОЛУЧЕНО УВЕДОМЛЕНИЕ ОБ УСПЕШНОЙ ОПЛАТЕ:")
        print(f"Полный объект: {data}")

        # Извлекаем данные
        event = data.get('event', '')
        order_id = data.get('order_id', 0)

        print(f"Event: {event}")
        print(f"Order ID: {order_id}")
        print("=" * 50)

        if event == 'payment_completed' and order_id:
            # Здесь будет логика:
            # 1. Найти заказ по order_id
            # 2. Обновить статус на COMPLETED
            # 3. Создать активную подписку для пользователя
            # 4. Отправить email с токеном и кодом доступа

            token: str = ""

            order = await get_order_by_order_id(order_id)

            if order:
                await update_order_status(order_id, OrderStatus.COMPLETED)
                subscription = await get_subscription_by_order_id(order.order_id)
                if not subscription:
                    await create_subscription(SubscriptionCreateSchemaDB(
                        order_id=order.order_id,
                    ))

                redeem_token = await get_redeem_token_by_order_id(order_id)
                token = redeem_token.token_hash

                short_code = await get_short_code_by_order_id(order_id)
                code = short_code.code_hash

                # Отправка письма с доступом к курсу
                success, error = await send_course_access_email(
                    to=order.email,
                    access_code=code,
                    bot_link="https://t.me/lagidna_disciplinabot?start=" + token
                )

                if success:
                    print("Email sent successfully")
                else:
                    print(f"Failed to send email: {error}")

            print(f"Обрабатываем успешную оплату для заказа {order_id}")

            return {
                "status": "success",
                "message": f"Payment completed notification processed for order {order_id}",
                "order_id": order_id,
                "button_url": f"https://t.me/lagidna_disciplinabot?start={token}"  # Пример ссылки с токеном
            }
        else:
            return {
                "status": "error",
                "message": "Invalid event or missing order_id"
            }

    except Exception as e:
        logging.error(f"Ошибка обработки успешной оплаты: {e}")
        print(f"ОШИБКА: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
