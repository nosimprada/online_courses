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
        if user.username and user.email:
            builder.button(text=f"{user.email} | @{user.username}", callback_data=f"admin:show_user_{user.user_id}")
        elif user.username and not user.email:
            builder.button(text=f"{user.username}", callback_data=f"admin:show_user_{user.user_id}")
        elif not user.username and user.email:
            builder.button(text=f"{user.email}", callback_data=f"admin:show_user_{user.user_id}")
        elif not user.username and not user.email:
            builder.button(text=f"ID {user.user_id}", callback_data=f"admin:show_user_{user.user_id}")

    builder.button(text="В адмін-панель", callback_data="admin:back_to_menu")
    builder.button(text="На головну", callback_data="back_to_menu")

    builder.adjust(1)

    return builder.as_markup()


def show_user_data(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Замовлення", callback_data=f"admin:show_user_orders_{user_id}")
    builder.button(text="Доступи", callback_data=f"admin:show_user_subscriptions_{user_id}")

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
