import re
from typing import Callable, Tuple, List

from aiogram.utils.keyboard import InlineKeyboardBuilder

_BACK_RULES: List[Tuple[str, Callable[[re.Match[str]], str]]] = [
    # Пользователи
    (r"^admin:show_users$", lambda m: "admin:back_to_menu"),
    (r"^admin:show_user_(\d+)$", lambda m: "admin:show_users"),
    (r"^admin:show_user_orders_(\d+)$", lambda m: f"admin:show_user_{m.group(1)}"),
    (r"^admin:show_user_subscriptions_(\d+)$", lambda m: f"admin:show_user_{m.group(1)}"),
    (r"^admin:grant_access_(\d+)$", lambda m: f"admin:show_user_subscriptions_{m.group(1)}"),
    (r"^admin:open_all_accesses_(\d+)$", lambda m: f"admin:show_user_subscriptions_{m.group(1)}"),
    (r"^admin:close_all_accesses_(\d+)$", lambda m: f"admin:show_user_subscriptions_{m.group(1)}"),

    # Курсы
    (r"^admin:courses$", lambda m: "admin:back_to_menu"),
    (r"^admin:courses_page_(\d+)$", lambda m: "admin:back_to_menu"),
    (r"^admin:manage_course_page_(\d+)_(\d+)$", lambda m: "admin:courses"),
    (r"^admin:manage_module_lesson_(\d+)_(\d+)$", lambda m: f"admin:manage_course_page_{m.group(1)}_1"),
    (r"^admin:ask_delete_lesson_(\d+)_(\d+)$", lambda m: f"admin:manage_module_lesson_{m.group(1)}_{m.group(2)}"),
    (r"^admin:show_video_(\d+)_(\d+)$", lambda m: f"admin:manage_module_lesson_{m.group(1)}_{m.group(2)}"),
    (r"^admin:show_pdf_(\d+)_(\d+)$", lambda m: f"admin:manage_module_lesson_{m.group(1)}_{m.group(2)}"),

    # Прочее
    (r"^admin:show_active_accesses$", lambda m: "admin:back_to_menu"),
]


async def add_auto_back_button(builder: InlineKeyboardBuilder, callback: str) -> None:
    """
    Использование:
        builder = InlineKeyboardBuilder()
        # ... кнопки ...

        add_auto_back_button(builder, callback="callback_of_this_page")
        return builder.as_markup()
    """

    resolved = _resolve_back_target(callback)

    if resolved:
        builder.button(text="↩️ Назад", callback_data=resolved)
    else:
        builder.button(text="В адмiн-панель", callback_data="admin:back_to_menu")


def _resolve_back_target(callback: str) -> str | None:
    for pattern, factory in _BACK_RULES:
        m = re.match(pattern, callback)
        if m:
            return factory(m)
    
    return None
