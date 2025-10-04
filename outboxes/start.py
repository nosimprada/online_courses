from datetime import datetime, timedelta

from aiogram.types import Message
from pytz import timezone

from config import ADMIN_CHAT_ID
from keyboards.start import start_menu_keyboard
from utils.enums.order import OrderStatus
from utils.enums.subscription import SubscriptionStatus
from utils.schemas.user import UserCreateSchemaDB
from utils.services.order import get_order_by_order_id, update_user_id_by_order_id
from utils.services.redeem_token import get_redeem_token_by_token_hash
from utils.services.subscription import (
    get_subscription_by_order_id,
    update_subscription_access_period,
    update_subscription_status
)
from utils.services.user import create_user, get_user_by_tg_id, get_user_full_info_by_tg_id


async def start_menu(message: Message):
    full_user_info = await get_user_full_info_by_tg_id(message.from_user.id)
    print(f"FULL USER INFO: {full_user_info}")

    if not full_user_info:
        await message.answer("Error retrieving user information.")
        return

    is_admin = False
    if message.from_user.id == ADMIN_CHAT_ID:
        is_admin = True

    msg_text = f"""
Привіт, {full_user_info.username}!
{'✅ Ви маєте активну підписку!' if full_user_info.is_subscribed else '❌ У вас немає активної підписки.'}

Прогрес навчання: {full_user_info.leaning_progress_procent:.2f}%
Дата закінчення підписки: {_format_date(full_user_info.subscription_access_to)}
"""

    await message.answer(msg_text, reply_markup=await start_menu_keyboard(is_admin))


async def registration_func(message: Message, ref_code: str | None = None):
    user_data = await get_user_by_tg_id(message.from_user.id)
    print(f"РЕФЕРАЛЬНЫЙ КОД: {ref_code}")

    if not user_data:
        user_create_data = UserCreateSchemaDB(
            user_id=message.from_user.id,
            username=message.from_user.username if message.from_user.username else "",
        )

        await create_user(user_create_data)
        print(f"=== НОВЫЙ ПОЛЬЗОВАТЕЛЬ СОЗДАН: {message.from_user.id} ===")
    else:
        print(f"=== ПОЛЬЗОВАТЕЛЬ УЖЕ СУЩЕСТВУЕТ: {message.from_user.id} ===")

    print(f"=== ПРОВЕРКА РЕФЕРАЛЬНОГО КОДА: {ref_code} ===")

    if ref_code:
        print(f"=== НАЧИНАЕМ ОБРАБОТКУ РЕФЕРАЛЬНОГО КОДА ===")

        try:
            token_hash = ref_code

            redeem_token = await get_redeem_token_by_token_hash(token_hash)
            print(f"=== REDEEM TOKEN НАЙДЕН: {redeem_token} ===")

            if redeem_token:
                print(f"=== ПОЛУЧАЕМ ЗАКАЗ ПО ID: {redeem_token.order_id} ===")

                order = await get_order_by_order_id(redeem_token.order_id)
                print(f"=== ЗАКАЗ ПОЛУЧЕН: {order}, СТАТУС: {order.status} ===")

                if order.status.value == OrderStatus.COMPLETED.value:
                    print(f"=== ЗАКАЗ ЗАВЕРШЕН, ПОЛУЧАЕМ ПОДПИСКУ ===")

                    subscription = await get_subscription_by_order_id(order.order_id)
                    print(f"=== ПОДПИСКА ПОЛУЧЕНА: {subscription} ===")

                    if subscription and subscription.status.value == SubscriptionStatus.CREATED.value:
                        print(f"=== АКТИВИРУЕМ ПОДПИСКУ ===")
                        await update_subscription_status(subscription.id, SubscriptionStatus.ACTIVE)

                        now = datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None)

                        await update_subscription_access_period(
                            subscription.id,
                            now,
                            now + timedelta(days=90)
                        )

                        await update_user_id_by_order_id(order.order_id, message.from_user.id)

                        access_to = _format_date(now + timedelta(days=90))

                        await message.answer(f"Оплату отримано ✅\nДоступ відкрито до {access_to}.")

                        print(f"=== ПОДПИСКА АКТИВИРОВАНА ДЛЯ: {message.from_user.id} ДО {access_to} ===")

                    elif subscription and subscription.status.value == SubscriptionStatus.ACTIVE.value:
                        print(f"=== ПОЛЬЗОВАТЕЛЬ УЖЕ ИМЕЕТ АКТИВНУЮ ПОДПИСКУ: {message.from_user.id} ===")
                        await message.answer("You already have an active subscription.")
                    else:
                        print(f"=== ПОДПИСКА НE НАЙДЕНА ИЛИ НЕВЕРНЫЙ СТАТУС ===")
                else:
                    print(f"=== ЗАКАЗ НЕ ЗАВЕРШЕН, СТАТУС: {order.status} ===")
            else:
                print(f"=== REDEEM TOKEN НЕ НАЙДЕН ===")

        except Exception as e:
            print(f"=== ОШИБКА ПРИ ОБРАБОТКЕ РЕФЕРАЛЬНОГО КОДА: {e} ===")
    else:
        print(f"=== РЕФЕРАЛЬНЫЙ КОД ОТСУТСТВУЕТ ===")

    print(f"=== КОНЕЦ ФУНКЦИИ REGISTRATION_FUNC ===")


def _format_date(date: datetime) -> str:
    return date.strftime("%d.%m.%Y") if date else "N/A"
