from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.schemas.user import UserReadSchemaDB


def menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Користувачі", callback_data="admin:show_users")
    builder.button(text="Активні доступи", callback_data="admin:show_active_accesses")
    builder.button(text="На головну", callback_data="back_to_menu")

    builder.adjust(1)

    return builder.as_markup()


def show_users(users: list[UserReadSchemaDB]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for user in users:
        display_name = _format_user_display_name(user.user_id, user.username, user.email)
        builder.button(text=display_name, callback_data=f"admin:show_user_{user.user_id}")

    builder.button(text="В адмін-панель", callback_data="admin:back_to_menu")
    builder.button(text="На головну", callback_data="back_to_menu")

    builder.adjust(1)

    return builder.as_markup()


def show_user_data(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Замовлення", callback_data=f"admin:show_user_orders_{user_id}")
    builder.button(text="Доступи", callback_data=f"admin:show_user_subscriptions_{user_id}")

    builder.button(text="Прив'язати електронну пошту", callback_data=f"admin:set_user_email_{user_id}")

    builder.button(text="В адмін-панель", callback_data="admin:back_to_menu")
    builder.button(text="На головну", callback_data="back_to_menu")

    builder.adjust(1)

    return builder.as_markup()


def show_user_orders(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="До користувача", callback_data=f"admin:show_user_{user_id}")

    builder.button(text="В адмін-панель", callback_data="admin:back_to_menu")
    builder.button(text="На головну", callback_data="back_to_menu")

    builder.adjust(1)

    return builder.as_markup()


def back_to_admin_or_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="В адмін-панель", callback_data="admin:back_to_menu")
    builder.button(text="На головну", callback_data="back_to_menu")

    builder.adjust(1)

    return builder.as_markup()


def _format_user_display_name(user_id: str, username: str | None = None, email: str | None = None) -> str:
    parts = []

    if email:
        parts.append(email)

    if username:
        parts.append(f"@{username}")

    if parts:
        return " | ".join(parts)
    else:
        return f"ID {user_id}"
