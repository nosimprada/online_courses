from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def choose_support_topic() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Тема повідомлення №1", callback_data="help:support_topic_1")
    builder.button(text="Тема повідомлення №2", callback_data="help:support_topic_2")
    builder.button(text="Тема повідомлення №3", callback_data="help:support_topic_3")
    builder.button(text="❌ Скасувати запит", callback_data="help:cancel")

    builder.adjust(2)

    return builder.as_markup()


def choose_message_action_for_helpers(username: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if username:
        builder.button(text="Відповісти", url=f"https://t.me/{username}")

    builder.button(text="Закрити", callback_data="helper:close")

    builder.adjust(2)

    return builder.as_markup()
