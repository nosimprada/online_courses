from aiogram import Router, F
from aiogram.types import CallbackQuery

import keyboards.admin as admin_kb
from utils.services.order import get_orders_by_tg_id
from utils.services.subscription import get_subscriptions_by_tg_id, get_active_subscriptions
from utils.services.user import get_all_users, get_user_by_tg_id

router = Router()


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


@router.callback_query(F.data.startswith("admin:show_user_"))
async def show_user_data(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])

    try:
        user = await get_user_by_tg_id(user_id)

        msg = (
            "Інформація про користувача:\n\n"
            f"🆔 <b>User ID:</b> <code>{user.user_id}</code>\n"
        )

        if user.username:
            msg += f"👤 <b>Username:</b> <code>{user.username}</code>\n"
        if user.email:
            msg += f"📧 <b>Email:</b> <code>{user.email}</code>\n"

        await callback.message.edit_text(msg, reply_markup=admin_kb.show_user_data(user_id))
        await callback.answer()

    except Exception as e:
        print(f"[ERROR] Show user data for admin: {e}")


@router.callback_query(F.data.startswith("admin:show_user_orders_"))
async def show_user_orders(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])

    try:
        orders = await get_orders_by_tg_id(user_id)

        msg = f"\n<i>Замовлення користувача (ID {user_id}):</i>\n\n"

        for order in orders:
            msg += f"📦 <b>ID:</b> <code>{order.id}</code>\n"
            msg += f"💰 <b>Сума:</b> <code>{order.amount}</code>\n"
            msg += f"🔔 <b>Статус:</b> <code>{order.status}</code>\n"
            msg += f"⌚ <b>Створено:</b> <code>{order.created_at}</code>\n"
            msg += f"💸 <b>Сплачено:</b> <code>{order.paid_at}</code>\n\n"

        await callback.message.edit_text(msg, reply_markup=admin_kb.back_to_admin_or_menu())
        await callback.answer()

    except Exception as e:
        print(f"[ERROR] Show user orders for admin: {e}")
        await callback.answer()


@router.callback_query(F.data == "admin:show_user_subscriptions_")
async def show_user_subscriptions(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])

    try:
        subscriptions = await get_subscriptions_by_tg_id(user_id)

        msg = f"\n<i>Доступи користувача (ID {user_id}):</i>\n\n"

        for subscription in subscriptions:
            msg += f"🎟️ <b>ID:</b> <code>{subscription.id}</code>\n"
            msg += f"📦 <b>ID замовлення:</b> <code>{subscription.order_id}</code>\n"
            msg += f"📅 <b>Початок доступу:</b> <code>{subscription.access_from}</code>\n"
            msg += f"📅 <b>Кінець доступу:</b> <code>{subscription.access_to}</code>\n"
            msg += f"🔔 <b>Статус:</b> <code>{subscription.status}</code>\n"
            msg += f"⌚ <b>Створено:</b> <code>{subscription.created_at}</code>\n"

        await callback.message.edit_text(msg, reply_markup=admin_kb.back_to_admin_or_menu())
        await callback.answer()

    except Exception as e:
        print(f"[ERROR] Show user subscriptions for admin: {e}")
        await callback.answer()


@router.callback_query(F.data == "admin:show_active_accesses")
async def show_active_accesses(callback: CallbackQuery) -> None:
    try:
        active_subscriptions = await get_active_subscriptions()

        msg = "\n<i>Активні доступи користувачів:</i>\n\n"

        for subscription in active_subscriptions:
            if subscription.user_id:
                msg += f"🆔 <b>ID користувача:</b> <code>{subscription.user_id}</code>\n"
            msg += f"🔔 <b>Статус:</b> <code>{subscription.status}</code>\n\n"

        await callback.message.edit_text(msg, reply_markup=admin_kb.back_to_admin_or_menu())
        await callback.answer()

    except Exception as e:
        print(f"[ERROR] Show active subscriptions for admin: {e}")


@router.callback_query(F.data == "admin:back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Виберіть дію:", reply_markup=admin_kb.menu())
    await callback.answer()
