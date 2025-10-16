import re
from typing import Callable, Tuple, List

from aiogram.utils.keyboard import InlineKeyboardBuilder

_BACK_RULES: List[Tuple[str, Callable[[re.Match[str]], str]]] = [
    # Admin: Users
    (r"^admin:show_user_subscriptions_page_(\d+)_(\d+)$", lambda m: f"admin:show_user_{m.group(1)}"),
    (r"^admin:grant_access_(\d+)$", lambda m: f"admin:show_user_subscriptions_page_{m.group(1)}_{m.group(2)}"),
    (r"^admin:show_subscription_(\d+)$", lambda m: f"admin:show_user_subscriptions_page_{m.group(1)}_{m.group(2)}"),
    (r"^admin:open_subscription_(\d+)$", lambda m: f"admin:show_subscription_{m.group(1)}"),
    (r"^admin:close_subscription_(\d+)$", lambda m: f"admin:show_subscription_{m.group(1)}"),

    # Admin: Courses
    (r"^admin:manage_course_(\d+)$", lambda m: f"admin:back_to_menu"),
    (r"^admin:manage_module_lesson_(\d+)_(\d+)$", lambda m: f"admin:manage_course_{m.group(1)}"),
    (r"^admin:ask_delete_lesson_(\d+)_(\d+)$", lambda m: f"admin:manage_module_lesson_{m.group(1)}_{m.group(2)}"),
    (r"^admin:show_video_(\d+)_(\d+)$", lambda m: f"admin:manage_module_lesson_{m.group(1)}_{m.group(2)}"),
    (r"^admin:show_pdf_(\d+)_(\d+)$", lambda m: f"admin:manage_module_lesson_{m.group(1)}_{m.group(2)}"),

    # Admin: Tickets
    (r"^help:admin:ticket_(\d+)$", lambda m: f"admin:tickets_menu_page_{m.group(1)}"),
    (r"^help:admin_respond_(\d+)_(\d+)$", lambda m: f"admin:ticket_{m.group(1)}"),
    (r"^help:admin_close_(\d+)_(\d+)$", lambda m: f"admin:ticket_{m.group(1)}"),

    # Admin: Other
    (r"^admin:show_active_accesses$", lambda m: "admin:back_to_menu"),

    # User: Courses
    (r"^course:module_lesson_(\d+)_(\d+)$", lambda m: f"course:module_{m.group(1)}"),
    (r"^course:show_pdf_(\d+)_(\d+)$", lambda m: f"course:module_lesson_{m.group(1)}_{m.group(2)}"),
    (r"^course:show_note_(\d+)_(\d+)$", lambda m: f"course:show_notes_{m.group(1)}"),
]


async def add_auto_back(builder: InlineKeyboardBuilder, callback: str) -> None:
    resolved = await _resolve_back_target(callback)

    if resolved:
        builder.button(text="↩️ Назад", callback_data=resolved)
    else:
        builder.button(text="🔁 На головну", callback_data="back_to_menu")


async def _resolve_back_target(callback: str) -> str | None:
    for pattern, factory in _BACK_RULES:
        m = re.match(pattern, callback)
        if m:
            return factory(m)

    return None
