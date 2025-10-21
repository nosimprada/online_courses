from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def renewal_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Перейти до оплати 💠", url="https://annarodina.pro/case/")
    builder.button(text="Ввести код ➕", callback_data="renewal:enter_code")
    builder.adjust(1)
    return builder.as_markup()
