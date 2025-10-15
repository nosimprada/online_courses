from typing import List, T

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def keyboard_with_pagination(
        builder: InlineKeyboardBuilder,
        page: int, page_size: int, total_items: int,
        callback_data: str
) -> InlineKeyboardMarkup:
    prefix = f"{callback_data}_page_"

    total_pages = (total_items - 1) // page_size + 1
    pagination_buttons: List[InlineKeyboardButton] = []

    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️", callback_data=f"{prefix}{page - 1}"
        ))

    if page < total_pages - 1:
        pagination_buttons.append(InlineKeyboardButton(
            text="➡️", callback_data=f"{prefix}{page + 1}"
        ))

    if pagination_buttons:
        builder.row(*pagination_buttons, width=2)

    return builder.as_markup()


def paginate_items(items: List[T], page: int, page_size: int) -> List[T]:
    if page_size <= 0:
        raise ValueError("page_size must be > 0")

    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size

    page = max(0, min(page, total_pages - 1)) if total_pages > 0 else 0

    start = page * page_size
    end = start + page_size

    return items[start:end]
