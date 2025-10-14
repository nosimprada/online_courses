from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from pytz import timezone

from config import ADMIN_CHAT_ID
from keyboards.start import start_menu_keyboard
from utils.enums.order import OrderStatus
from utils.enums.subscription import SubscriptionStatus
from utils.schemas.user import UserCreateSchemaDB, UserReadFullInfoSchemaDB
from utils.services.order import get_order_by_order_id, update_user_id_by_order_id
from utils.services.redeem_token import get_redeem_token_by_token_hash
from utils.services.short_code import get_short_code_by_code_hash
from utils.services.subscription import (
    get_subscription_by_order_id,
    update_subscription_access_period,
    update_subscription_status,
    update_subscription_user_id_by_subscription_id
)
from utils.services.user import create_user, get_user_by_tg_id, get_user_full_info_by_tg_id


async def start_menu(message: Message | CallbackQuery):
    full_user_info: UserReadFullInfoSchemaDB = None

    if isinstance(message, Message):
        full_user_info = await get_user_full_info_by_tg_id(message.from_user.id)
        print(f"FULL USER INFO: {full_user_info}")

    elif isinstance(message, CallbackQuery):
        full_user_info = await get_user_full_info_by_tg_id(message.from_user.id)
        print(f"FULL USER INFO: {full_user_info}")

    if not full_user_info:
        if isinstance(message, Message):
            await message.answer("❌ Не вдалося отримати інформацію про користувача.")
            return

        elif isinstance(message, CallbackQuery):
            await message.message.answer("❌ Не вдалося отримати інформацію про користувача.")
            return

    is_admin = message.from_user.id == ADMIN_CHAT_ID

    msg_text = f"""
Привіт, {full_user_info.username}!
{'✅ Ви маєте активну підписку!' if full_user_info.is_subscribed else '❌ У вас немає активної підписки.'}

Прогрес навчання: {full_user_info.leaning_progress_procent:.2f}%
Дата закінчення підписки: {_format_date(full_user_info.subscription_access_to)}
"""

    if isinstance(message, Message):
        await message.answer(msg_text, reply_markup=await start_menu_keyboard(is_admin))

    elif isinstance(message, CallbackQuery):
        await message.message.answer(msg_text, reply_markup=await start_menu_keyboard(is_admin))


async def send_start_menu_to_user(bot: Bot, user_id: int) -> None:
    full_user_info: UserReadFullInfoSchemaDB = await get_user_full_info_by_tg_id(user_id)

    if not full_user_info:
        await bot.send_message(user_id, "❌ Не вдалося отримати інформацію про користувача.")
        return

    is_admin = user_id == ADMIN_CHAT_ID

    msg_text = f"""
Привіт, {full_user_info.username}!
{'✅ Ви маєте активну підписку!' if full_user_info.is_subscribed else '❌ У вас немає активної підписки.'}
    
Прогрес навчання: {full_user_info.leaning_progress_procent:.2f}%
Дата закінчення підписки: {_format_date(full_user_info.subscription_access_to)}
    """

    await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=await start_menu_keyboard(is_admin))


async def registration_func(message: Message, ref_code: str | None = None):
    user_data = await get_user_by_tg_id(message.from_user.id)
    print(f"РЕФЕРАЛЬНЫЙ КОД: {ref_code}")

    if not user_data:
        user_create_data = UserCreateSchemaDB(
            tg_id=message.from_user.id,
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
                        await update_subscription_user_id_by_subscription_id(subscription.id, message.from_user.id)

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


# ...existing code...
async def register_ref_code_handler(code: str, message: Message):
    try:
        short_code = await get_short_code_by_code_hash(code)
        if not short_code:
            await message.answer("Даний код недійсний. Спробуйте ще раз.")
            return

        order = await get_order_by_order_id(short_code.order_id)
        if not order:
            await message.answer("Замовлення не знайдено.")
            return

        if order.status.value != OrderStatus.COMPLETED.value:
            print(f"=== ЗАКАЗ НЕ ЗАВЕРШЕН, СТАТУС: {order.status} ===")
            await message.answer("Оплата ще не підтверджена. Спробуйте пізніше.")
            return

        print("=== ЗАКАЗ ЗАВЕРШЕН, ПОЛУЧАЕМ ПОДПИСКУ ===")
        subscription = await get_subscription_by_order_id(order.order_id)
        print(f"=== ПОДПИСКА ПОЛУЧЕНА: {subscription} ===")

        if subscription and subscription.status.value == SubscriptionStatus.CREATED.value:
            print("=== АКТИВИРУЕМ ПОДПИСКУ ===")
            await update_subscription_status(subscription.id, SubscriptionStatus.ACTIVE)
            await update_subscription_user_id_by_subscription_id(subscription.id, message.from_user.id)

            now = datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None)
            await update_subscription_access_period(
                subscription.id,
                now,
                now + timedelta(days=90),
            )
            await update_user_id_by_order_id(order.order_id, message.from_user.id)

            access_to = _format_date(now + timedelta(days=90))
            await message.answer(f"Оплату отримано ✅\nДоступ відкрито до {access_to}.")
            print(f"=== ПОДПИСКА АКТИВИРОВАНА ДЛЯ: {message.from_user.id} ДО {access_to} ===")

        elif subscription and subscription.status.value == SubscriptionStatus.ACTIVE.value:
            print(f"=== ПОЛЬЗОВАТЕЛЬ УЖЕ ИМЕЕТ АКТИВНУЮ ПОДПИСКУ: {message.from_user.id} ===")
            await message.answer("You already have an active subscription.")
        else:
            print("=== ПОДПИСКА НE НАЙДЕНА ИЛИ НЕВЕРНЫЙ СТАТУС ===")
            await message.answer("Підписку не знайдено. Зверніться до підтримки.")

    except Exception as e:
        print(f"=== ОШИБКА ПРИ ОБРАБОТКЕ РЕФЕРАЛЬНОГО КОДА: {e} ===")
        await message.answer("Сталася помилка. Спробуйте пізніше.")
# ...existing code...
