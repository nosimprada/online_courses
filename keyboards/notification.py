from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def go_to_the_first_lesson() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 До першого уроку", callback_data="course:module_lesson_1_1")

    return builder.as_markup()


async def extend_subscription() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Продовжити доступ", url="https://annarodina.pro/case/")

    return builder.as_markup()
