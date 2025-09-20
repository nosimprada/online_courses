from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.schemas.user import UserReadSchemaDB


def menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Користувачі", callback_data="admin:show_users")
    builder.button(text="Активні доступи", callback_data="admin:show_active_accesses")

    builder.adjust(1)

    return builder.as_markup()


def show_users(users: list[UserReadSchemaDB]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for user in users:
        if user.username:
            builder.button(text=f"{user.email} | @{user.username}", callback_data=f"admin:show_user_{user.user_id}")
        else:
            builder.button(text=f"{user.email}", callback_data=f"admin:show_user_{user.user_id}")

    builder.adjust(1)

    return builder.as_markup()
