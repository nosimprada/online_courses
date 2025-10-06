from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def start_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text="Навчання 📚")
    builder.button(text="Конспекти 📝")
    builder.button(text="Продовити доступ 🔄")
    builder.button(text="Help ❓")

    if is_admin:
        builder.button(text="Адмін панель 🔧")

    builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)
