from datetime import datetime, timedelta
from typing import List, Tuple

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup

import keyboards.admin as admin_kb
from utils.enums.order import OrderStatus
from utils.enums.subscription import SubscriptionStatus
from utils.schemas.order import OrderCreateSchemaDB
from utils.schemas.subscription import SubscriptionReadSchemaDB, SubscriptionCreateSchemaDB
from utils.services.order import get_orders_by_tg_id, create_order
from utils.services.subscription import get_subscriptions_by_tg_id, get_active_subscriptions, \
    close_subscriptions_access, open_subscriptions_access, create_subscription
from utils.services.user import get_all_users, get_user_by_tg_id, set_user_email

router = Router()


class SetUserEmailState(StatesGroup):
    email = State()


class GrantSubscriptionState(StatesGroup):
    access_to = State()


@router.callback_query(F.data.startswith("admin:show_user_orders_"))
async def show_user_orders(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])

    orders = await get_orders_by_tg_id(user_id)
    if not orders:
        await callback.message.edit_text("Користувач не має замовлень.", reply_markup=admin_kb.back_to_admin_or_menu())
        await callback.answer()
        return

    msg = f"\n<i>Замовлення користувача (ID {user_id}):</i>\n\n"

    for order in orders:
        msg += f"📦 <b>ID:</b> <code>{order.id}</code>\n"
        msg += f"💰 <b>Сума:</b> <code>{order.amount}</code>\n"
        msg += f"🔔 <b>Статус:</b> <code>{order.status}</code>\n"
        msg += f"⌚ <b>Створено:</b> <code>{_normalize_date(order.created_at)}</code>\n"
        msg += f"💸 <b>Сплачено:</b> <code>{_normalize_date(order.paid_at)}</code>\n\n"

    await callback.message.edit_text(msg, reply_markup=admin_kb.back_to_admin_menu_user(user_id))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:show_user_subscriptions_"))
async def show_user_subscriptions(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])

    subscriptions = await get_subscriptions_by_tg_id(user_id)
    if not subscriptions:
        await callback.message.edit_text(
            "Користувач не має доступів.",
            reply_markup=admin_kb.show_user_subscriptions(user_id, True)
        )
        await callback.answer()
        return

    msg = f"\n<i>Доступи користувача (ID {user_id}):</i>\n\n"

    for subscription in subscriptions:
        msg += f"🎟️ <b>ID:</b> <code>{subscription.id}</code>\n"
        msg += f"📦 <b>ID замовлення:</b> <code>{subscription.order_id}</code>\n"
        msg += f"📅 <b>Початок доступу:</b> <code>{subscription.access_from}</code>\n"
        msg += f"📅 <b>Кінець доступу:</b> <code>{subscription.access_to}</code>\n"
        msg += f"🔔 <b>Статус:</b> <code>{subscription.status}</code>\n"
        msg += f"⌚ <b>Створено:</b> <code>{_normalize_date(subscription.created_at)}</code>\n\n"

    await callback.message.edit_text(msg, reply_markup=admin_kb.show_user_subscriptions(user_id, False))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:show_user_"))
async def show_user_data(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])

    user = await get_user_by_tg_id(user_id)
    if not user:
        await callback.message.edit_text("Користувач не знайдено.", reply_markup=admin_kb.back_to_admin_or_menu())
        await callback.answer()
        return

    msg = (
        f"👤 <b>Інформація про користувача</b>\n\n"
        f"🆔 <b>User ID:</b> <code>{user.user_id}</code>\n"
    )

    if user.username:
        msg += f"👤 <b>Username:</b> @{user.username}\n"
    if user.email:
        msg += f"📧 <b>Email:</b> <code>{user.email}</code>\n"

    msg += f"📅 <b>Створено:</b> <code>{_normalize_date(user.created_at)}</code>\n"

    msg += f"\n📋 Оберіть категорію для перегляду:"

    await callback.message.edit_text(msg, reply_markup=admin_kb.show_user_data(user_id))
    await callback.answer()


@router.callback_query(F.data == "admin:menu")
async def menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Виберіть дію:", reply_markup=admin_kb.menu())
    await callback.answer()


@router.callback_query(F.data == "admin:show_users")
async def show_users(callback: CallbackQuery) -> None:
    users = await get_all_users()

    await callback.message.edit_text(
        f"Кількість користувачів: <code>{len(users)}</code>",
        reply_markup=admin_kb.show_users(users)
    )

    await callback.answer()


@router.callback_query(F.data == "admin:show_active_accesses")
async def show_active_accesses(callback: CallbackQuery) -> None:
    active_subscriptions = await get_active_subscriptions()
    if not active_subscriptions:
        await callback.message.edit_text("Немає активних доступів.", reply_markup=admin_kb.back_to_admin_or_menu())
        await callback.answer()
        return

    msg = "\n<i>Активні доступи користувачів:</i>\n\n"

    for subscription in active_subscriptions:
        if subscription.user_id:
            msg += f"🆔 <b>ID користувача:</b> <code>{subscription.user_id}</code>\n"

        msg += f"📅 <b>Кінець доступу:</b> <code>{_normalize_date(subscription.access_to)}</code>\n"
        msg += f"⏰ <b>Створено:</b> <code>{_normalize_date(subscription.created_at)}</code>\n\n"

    await callback.message.edit_text(msg, reply_markup=admin_kb.back_to_admin_or_menu())
    await callback.answer()


@router.callback_query(F.data.startswith("admin:set_user_email_"))
async def handle_set_user_email(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = int(callback.data.split("_")[-1])

    await state.set_state(SetUserEmailState.email)
    await state.update_data(user_id=user_id)

    await callback.message.edit_text(
        "Введіть нову електронну пошту користувача.\n"
        "Для скасування дії введіть «-»."
    )

    await callback.answer()


@router.message(F.text, StateFilter(SetUserEmailState.email))
async def input_set_user_email(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get("user_id")

    if message.text == "-":
        await state.clear()
        await message.answer("❌ Дія скасована.", reply_markup=admin_kb.back_to_admin_menu_user(user_id))
        return

    try:
        set_email = await set_user_email(user_id, message.text)
        if set_email and set_email.email == message.text:
            await message.answer(
                "✅ Електронна пошта успішно змінена.",
                reply_markup=admin_kb.back_to_admin_menu_user(user_id)
            )
            await state.clear()
            return

    except Exception as e:
        print(f"Error setting email for user {user_id}: {str(e)}")

    await message.answer(
        "❌ Сталася помилка під час зміни електронної пошти. Спробуйте пізніше.",
        reply_markup=admin_kb.back_to_admin_menu_user(user_id)
    )
    await state.clear()


@router.callback_query(F.data.startswith("admin:grant_access_"))
async def handle_grant_access(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = int(callback.data.split("_")[-1])

    await state.set_state(GrantSubscriptionState.access_to)
    await state.update_data(user_id=user_id)

    await callback.message.edit_text(
        "Введіть термін для надання доступу (у місяцях).\n"
        "Для скасування дії введіть «-»."
    )

    await callback.answer()


@router.message(F.text, StateFilter(GrantSubscriptionState.access_to))
async def input_grant_access(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get("user_id")

    if message.text == "-":
        await state.clear()
        await message.answer("❌ Дія скасована.", reply_markup=admin_kb.back_to_admin_menu_user(user_id))
        return

    try:
        months = int(message.text)
        if months <= 0:
            await message.answer(
                "❌ Введіть позитивне число місяців.\n"
                "Спробуйте ще раз або введіть «-» для скасування."
            )
            return
    except ValueError:
        await message.answer(
            "❌ Введіть коректне число місяців.\n"
            "Спробуйте ще раз або введіть «-» для скасування."
        )
        return

    try:
        order = await create_order(OrderCreateSchemaDB(
            user_id=user_id,
            amount=0.0,
            status=OrderStatus.COMPLETED.value
        ))

        access_from = datetime.now()
        access_to = access_from + timedelta(days=months * 30)

        subscription = await create_subscription(SubscriptionCreateSchemaDB(
            user_id=user_id,
            order_id=order.id,
            access_from=access_from,
            access_to=access_to,
            status=SubscriptionStatus.CREATED.value
        ))

        if subscription.user_id == user_id:
            await message.answer(
                f"✅ Доступ успішно надано користувачу (ID {user_id}) на {months} місяць(ів).\n"
                f"📅 Доступ до: {_normalize_date(access_to)}",
                reply_markup=admin_kb.back_to_admin_menu_user(user_id)
            )
            await state.clear()
            return

    except Exception as e:
        print(f"Error granting access to user {user_id}: {str(e)}")
        await message.answer(
            "❌ Сталася помилка під час надання доступу. Спробуйте пізніше.",
            reply_markup=admin_kb.back_to_admin_menu_user(user_id)
        )
        await state.clear()


@router.callback_query(F.data.startswith("admin:open_all_accesses_"))
async def open_all_accesses(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])

    try:
        opened = await open_subscriptions_access(user_id)
        message_text, reply_markup = _are_subscriptions_updated(opened, "open", user_id)
        await callback.message.edit_text(message_text, reply_markup=reply_markup)

    except Exception as e:
        print(f"Error opening access for user {user_id}: {str(e)}")
        await callback.message.edit_text(
            f"❌ Сталася помилка при відкритті доступів користувача (ID {user_id}).",
            reply_markup=admin_kb.back_to_admin_or_menu()
        )

    await callback.answer()


@router.callback_query(F.data.startswith("admin:close_all_accesses_"))
async def close_all_accesses(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])

    try:
        closed = await close_subscriptions_access(user_id)
        message_text, reply_markup = _are_subscriptions_updated(closed, "close", user_id)
        await callback.message.edit_text(message_text, reply_markup=reply_markup)

    except Exception as e:
        print(f"Error closing access for user {user_id}: {str(e)}")
        await callback.message.edit_text(
            f"❌ Сталася помилка при закритті доступів користувача (ID {user_id}).",
            reply_markup=admin_kb.back_to_admin_or_menu()
        )

    await callback.answer()


@router.callback_query(F.data == "admin:back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Виберіть дію:", reply_markup=admin_kb.menu())
    await callback.answer()


def _are_subscriptions_updated(subscriptions: List[SubscriptionReadSchemaDB], action: str, user_id: int
                               ) -> Tuple[str, InlineKeyboardMarkup]:
    messages = {
        "open": {
            "success": f"✅ Всі доступи користувача (ID {user_id}) успішно відкрито.",
            "warn": f"⚠️ Частково відкрито доступи користувача (ID {user_id}). Деякі доступи не вдалося відкрити.",
            "error": f"❌ Не вдалося відкрити доступи користувача (ID {user_id})."
        },
        "close": {
            "success": f"✅ Всі доступи користувача (ID {user_id}) успішно закрито.",
            "warn": f"⚠️ Частково закрито доступи користувача (ID {user_id}). Деякі доступи не вдалося закрити.",
            "error": f"❌ Не вдалося закрити доступи користувача (ID {user_id})."
        }
    }

    if not subscriptions:
        return messages[action]["error"], admin_kb.back_to_admin_or_menu()

    expected_status = SubscriptionStatus.ACTIVE.value if action == "open" else SubscriptionStatus.CANCELED.value
    success_count = sum(1 for sub in subscriptions if sub.status == expected_status)
    total_count = len(subscriptions)

    if success_count == total_count:
        return messages[action]["success"], admin_kb.back_to_admin_menu_user(user_id)
    elif success_count > 0:
        return messages[action]["warn"], admin_kb.back_to_admin_menu_user(user_id)
    else:
        return messages[action]["error"], admin_kb.back_to_admin_menu_user(user_id)


def _normalize_date(date: datetime) -> str:
    if date is None:
        return "Не вказано"
    
    return date.strftime('%d.%m.%Y %H:%M:%S')
