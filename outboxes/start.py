from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from pytz import timezone

from config import ADMIN_CHAT_ID
from keyboards.start import start_menu_keyboard
from utils.enums.order import OrderStatus
from utils.enums.subscription import SubscriptionStatus
from utils.schemas.user import UserCreateSchemaDB, UserReadFullInfoSchemaDB
from utils.services.order import get_order_by_order_id, update_order_status, update_user_id_by_order_id
from utils.services.redeem_token import get_redeem_token_by_token_hash
from utils.services.short_code import get_short_code_by_code_hash
from utils.services.subscription import (
    get_subscription_by_order_id,
    get_subscriptions_by_tg_id,
    update_subscription_access_period,
    update_subscription_status,
    update_subscription_user_id_by_subscription_id
)
from utils.services.user import create_user, get_user_by_tg_id, get_user_full_info_by_tg_id
from utils.states import RefCode


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

    msg_text = _start_text(full_user_info)

    if isinstance(message, Message):
        await message.answer(msg_text, reply_markup=await start_menu_keyboard(is_admin))

    elif isinstance(message, CallbackQuery):
        await message.message.answer(msg_text, reply_markup=await start_menu_keyboard(is_admin))


async def send_start_menu_to_user(bot: Bot, user_id: int) -> None:
    full_user_info: UserReadFullInfoSchemaDB = await get_user_full_info_by_tg_id(user_id)

    if not full_user_info:
        await bot.send_message(user_id, "❌ Не вдалося отримати інформацію про користувача.")
        return

    await bot.send_message(
        user_id,
        _start_text(full_user_info),
        reply_markup=await start_menu_keyboard(user_id == ADMIN_CHAT_ID)
    )


async def registration_func(message: Message, ref_code: str | None = None, state: FSMContext | None = None):
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
                        new_order_status = await update_order_status(order.order_id, OrderStatus.CANCELED)
                        print(f"=== ОБНОВЛЕН СТАТУС ЗАКАЗА НА CANCELED: {new_order_status} ===")

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
                await message.answer(
                    "Активних підписок немає. Введіть будь ласка код, який був надісланий вам на електронну пошту.")
                print(f"=== ПЕРЕХОДИМ В СОСТОЯНИЕ GET_REF_CODE ===")
                await state.set_state(RefCode.get_ref_code)

        except Exception as e:
            print(f"=== ОШИБКА ПРИ ОБРАБОТКЕ РЕФЕРАЛЬНОГО КОДА: {e} ===")
    else:
        print(f"=== РЕФЕРАЛЬНЫЙ КОД ОТСУТСТВУЕТ ===")

    print(f"=== КОНЕЦ ФУНКЦИИ REGISTRATION_FUNC ===")


def _format_date(date: datetime) -> str:
    return date.strftime("%d.%m.%Y") if date else "N/A"


def _start_text(user: UserReadFullInfoSchemaDB) -> str:
    # Прогрес навчання: {user.leaning_progress_procent:.2f}%
    msg_text = f"""
Привіт, {user.username}!
{"✅ Ви маєте активну підписку!" if user.is_subscribed else "❌ У вас немає активної підписки."}
Дата закінчення підписки: {_format_date(user.subscription_access_to)}
    """

    return msg_text


# ...existing code...
async def register_ref_code_handler(code: str, message: Message):
    user_data = await get_user_by_tg_id(message.from_user.id)
    if not user_data:
        user_create_data = UserCreateSchemaDB(
            tg_id=message.from_user.id,
            username=message.from_user.username if message.from_user.username else "",
        )
        await create_user(user_create_data)
        print(f"=== НОВЫЙ ПОЛЬЗОВАТЕЛЬ СОЗДАН: {message.from_user.id} ===")
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
            await update_order_status(order.order_id, OrderStatus.CANCELED)
            await start_menu(message)
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


# ...existing code...

# ...existing code...

async def subscription_renewal(message: Message, ref_code: str | None = None, short_code: str | None = None):
    if ref_code:
        print(f"=== НАЧИНАЕМ ОБРАБОТКУ РЕФЕРАЛЬНОГО КОДА ===")
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
                    print(f"=== ПРОДЛЕВАЕМ ПОДПИСКУ ===")

                    # Получаем все подписки пользователя
                    subscriptions = await get_subscriptions_by_tg_id(message.from_user.id)

                    # Находим активную подписку с самой поздней датой access_to
                    latest_subscription = None
                    if subscriptions:
                        active_subs = [sub for sub in subscriptions if sub.status == SubscriptionStatus.ACTIVE]
                        if active_subs:
                            latest_subscription = max(active_subs,
                                                      key=lambda sub: sub.access_to if sub.access_to else datetime.min)
                            print(f"=== НАЙДЕНА АКТИВНАЯ ПОДПИСКА С access_to: {latest_subscription.access_to} ===")

                    now = datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None)

                    # Определяем новые даты
                    if latest_subscription and latest_subscription.access_to:
                        new_access_from = latest_subscription.access_to
                        new_access_to = latest_subscription.access_to + timedelta(days=90)
                        print(f"=== ПРОДЛЕНИЕ ОТ СУЩЕСТВУЮЩЕЙ ПОДПИСКИ: {new_access_from} -> {new_access_to} ===")
                    else:
                        new_access_from = now
                        new_access_to = now + timedelta(days=90)
                        print(f"=== НОВАЯ ПОДПИСКА: {new_access_from} -> {new_access_to} ===")

                    # Активируем новую подписку
                    await update_subscription_status(subscription.id, SubscriptionStatus.ACTIVE)
                    await update_subscription_user_id_by_subscription_id(subscription.id, message.from_user.id)

                    await update_subscription_access_period(
                        subscription.id,
                        new_access_from,
                        new_access_to
                    )

                    await update_user_id_by_order_id(order.order_id, message.from_user.id)

                    access_to = _format_date(new_access_to)
                    await message.answer(f"Підписку продовжено ✅\nНовий термін дії до {access_to}.")

                    print(
                        f"=== ПОДПИСКА ПРОДЛЕНА ДЛЯ: {message.from_user.id} с {new_access_from} ДО {new_access_to} ===")

                    await update_order_status(order.order_id, OrderStatus.CANCELED)
                    print(f"=== ОБНОВЛЕН СТАТУС ЗАКАЗА НА CANCELED ===")

                    await start_menu(message)

                elif subscription and subscription.status.value == SubscriptionStatus.ACTIVE.value:
                    print(f"=== ПОДПИСКА УЖЕ АКТИВНА ===")
                    await message.answer("Ця підписка вже активована.")
                else:
                    print(f"=== ПОДПИСКА НЕ НАЙДЕНА ИЛИ НЕВЕРНЫЙ СТАТУС ===")
                    await message.answer("Підписку не знайдено. Зверніться до підтримки.")
            else:
                print(f"=== ЗАКАЗ НЕ ЗАВЕРШЕН, СТАТУС: {order.status} ===")
                await message.answer("Оплата ще не підтверджена. Спробуйте пізніше.")
        else:
            print(f"=== REDEEM TOKEN НЕ НАЙДЕН ===")
            await message.answer("Недійсний код доступу.")

    elif short_code:
        print(f"=== НАЧИНАЕМ ОБРАБОТКУ КОРОТКОГО КОДА ===")
        try:
            short_code_obj = await get_short_code_by_code_hash(short_code)

            if not short_code_obj:
                await message.answer("Даний код недійсний. Спробуйте ще раз.")
                return

            print(f"=== SHORT CODE НАЙДЕН: {short_code_obj} ===")
            print(f"=== ПОЛУЧАЕМ ЗАКАЗ ПО ID: {short_code_obj.order_id} ===")

            order = await get_order_by_order_id(short_code_obj.order_id)

            if not order:
                await message.answer("Замовлення не знайдено.")
                return

            print(f"=== ЗАКАЗ ПОЛУЧЕН: {order}, СТАТУС: {order.status} ===")

            if order.status.value != OrderStatus.COMPLETED.value:
                print(f"=== ЗАКАЗ НЕ ЗАВЕРШЕН, СТАТУС: {order.status} ===")
                await message.answer("Оплата ще не підтверджена. Спробуйте пізніше.")
                return

            print("=== ЗАКАЗ ЗАВЕРШЕН, ПОЛУЧАЕМ ПОДПИСКУ ===")
            subscription = await get_subscription_by_order_id(order.order_id)
            print(f"=== ПОДПИСКА ПОЛУЧЕНА: {subscription} ===")

            if subscription and subscription.status.value == SubscriptionStatus.CREATED.value:
                print("=== ПРОДЛЕВАЕМ ПОДПИСКУ ===")

                # Получаем все подписки пользователя
                subscriptions = await get_subscriptions_by_tg_id(message.from_user.id)

                # Находим активную подписку с самой поздней датой access_to
                latest_subscription = None
                if subscriptions:
                    active_subs = [sub for sub in subscriptions if sub.status == SubscriptionStatus.ACTIVE]
                    if active_subs:
                        latest_subscription = max(active_subs,
                                                  key=lambda sub: sub.access_to if sub.access_to else datetime.min)
                        print(f"=== НАЙДЕНА АКТИВНАЯ ПОДПИСКА С access_to: {latest_subscription.access_to} ===")

                now = datetime.now(timezone("Europe/Kyiv")).replace(tzinfo=None)

                # Определяем новые даты
                if latest_subscription and latest_subscription.access_to:
                    new_access_from = latest_subscription.access_to
                    new_access_to = latest_subscription.access_to + timedelta(days=90)
                    print(f"=== ПРОДЛЕНИЕ ОТ СУЩЕСТВУЮЩЕЙ ПОДПИСКИ: {new_access_from} -> {new_access_to} ===")
                else:
                    new_access_from = now
                    new_access_to = now + timedelta(days=90)
                    print(f"=== НОВАЯ ПОДПИСКА: {new_access_from} -> {new_access_to} ===")

                # Активируем новую подписку
                await update_subscription_status(subscription.id, SubscriptionStatus.ACTIVE)
                await update_subscription_user_id_by_subscription_id(subscription.id, message.from_user.id)

                await update_subscription_access_period(
                    subscription.id,
                    new_access_from,
                    new_access_to
                )

                await update_user_id_by_order_id(order.order_id, message.from_user.id)

                access_to = _format_date(new_access_to)
                await message.answer(f"Підписку продовжено ✅\nНовий термін дії до {access_to}.")

                print(f"=== ПОДПИСКА ПРОДЛЕНА ДЛЯ: {message.from_user.id} с {new_access_from} ДО {new_access_to} ===")

                await update_order_status(order.order_id, OrderStatus.CANCELED)
                print(f"=== ОБНОВЛЕН СТАТУС ЗАКАЗА НА CANCELED ===")

                await start_menu(message)

            elif subscription and subscription.status.value == SubscriptionStatus.ACTIVE.value:
                print(f"=== ПОДПИСКА УЖЕ АКТИВНА ===")
                await message.answer("Ця підписка вже активована.")
            else:
                print("=== ПОДПИСКА НE НАЙДЕНА ИЛИ НЕВЕРНЫЙ СТАТУС ===")
                await message.answer("Підписку не знайдено. Зверніться до підтримки.")

        except Exception as e:
            print(f"=== ОШИБКА ПРИ ОБРАБОТКЕ КОРОТКОГО КОДА: {e} ===")
            import traceback
            traceback.print_exc()
            await message.answer("Сталася помилка. Спробуйте пізніше.")
    else:
        print(f"=== НЕ ПЕРЕДАН НИ ОДИН КОД ===")
        await message.answer("Будь ласка, введіть код доступу.")

# ...existing code...
