from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def menu(is_admin: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if is_admin:
        builder.button(text="Адмiн-панель", callback_data="admin:menu")

    builder.button(text="Техпідтримка", callback_data="help:start")

    builder.adjust(1)

    return builder.as_markup()
