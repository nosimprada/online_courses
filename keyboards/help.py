from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def choose_support_topic() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="💬 Тема повідомлення №1")],
        [KeyboardButton(text="💬 Тема повідомлення №2")],
        [KeyboardButton(text="💬 Тема повідомлення №3")]
    ], resize_keyboard=True)


def admin_choose_ticket_action(user_id: int, ticket_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="💬 Відповісти", callback_data=f"help:admin_respond_{ticket_id}_{user_id}")
    builder.button(text="✅ Закрити тикет", callback_data=f"help:admin_close_{ticket_id}_{user_id}")

    builder.adjust(1)

    return builder.as_markup()


def admin_back_to_tickets() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📋 До списку тикетів")]
    ], resize_keyboard=True)
