from aiogram.utils.keyboard import InlineKeyboardBuilder


def add_pagination_buttons(
        builder: InlineKeyboardBuilder,
        current_page: int, total_pages: int, callback_prefix: str
) -> None:
    pagination_buttons = []

    if current_page > 1:
        pagination_buttons.append({
            "text": "⬅️ Назад",
            "callback_data": f"{callback_prefix}_{current_page - 1}"
        })

    if current_page < total_pages:
        pagination_buttons.append({
            "text": "➡️ Вперед",
            "callback_data": f"{callback_prefix}_{current_page + 1}"
        })

    for btn in pagination_buttons:
        builder.button(text=btn["text"], callback_data=btn["callback_data"])

    if len(pagination_buttons) > 0:
        current_buttons = len(list(builder.buttons))

        adjust_pattern = [1] * (current_buttons - len(pagination_buttons)) + [len(pagination_buttons)]
        builder.adjust(*adjust_pattern)
