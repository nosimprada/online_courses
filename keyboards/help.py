from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


async def cancel() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Скасувати звернення")

    return builder.as_markup(resize_keyboard=True)


async def back_to_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔁 На головну")

    return builder.as_markup(resize_keyboard=True)


async def admin_choose_ticket_action(user_id: int, ticket_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="💬 Відповісти", callback_data=f"help:admin_respond_{ticket_id}_{user_id}")
    builder.button(text="✅ Закрити тикет", callback_data=f"help:admin_close_{ticket_id}_{user_id}")

    builder.adjust(1)

    return builder.as_markup()


async def admin_back_to_tickets() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❓ Тикетi")

    return builder.as_markup(resize_keyboard=True)
