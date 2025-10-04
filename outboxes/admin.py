from datetime import datetime

from aiogram.types import CallbackQuery

from utils.services.order import get_orders_by_tg_id


async def show_user_orders(callback: CallbackQuery) -> None:
    try:
        user_id = int(callback.data.split("_")[-1])

        orders = await get_orders_by_tg_id(user_id)

        if not orders:
            await callback.message.answer(
                "Користувач не має замовлень.",
            )
            await callback.answer()
            return

        msg = f"\n<i>Замовлення користувача (ID {user_id}):</i>\n\n"

        for order in orders:
            msg += f"📦 <b>ID:</b> <code>{order.id}</code>\n"
            msg += f"💰 <b>Сума:</b> <code>{order.amount}</code>\n"
            msg += f"🔔 <b>Статус:</b> <code>{order.status}</code>\n"
            msg += f"⌚ <b>Створено:</b> <code>{_format_date(order.created_at)}</code>\n"
            msg += f"💸 <b>Сплачено:</b> <code>{_format_date(order.paid_at)}</code>\n\n"

        await callback.message.answer(msg, reply_markup=admin_kb.back_to_admin_or_user(user_id))
        await callback.answer()


def _format_date(date: datetime) -> str:
    return date.strftime("%d.%m.%Y") if date else "N/A"
