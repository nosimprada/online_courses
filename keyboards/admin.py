from datetime import datetime
from typing import List, Tuple

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup, ReplyKeyboardBuilder

from utils.auto_back import add_auto_back
from utils.enums.ticket import TicketStatus
from utils.schemas.lesson import LessonReadSchemaDB
from utils.schemas.ticket import TicketReadSchemaDB
from utils.schemas.user import UserReadSchemaDB


async def menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text="👥 Користувачі")
    builder.button(text="📖 Управління курсами")
    builder.button(text="❓ Тикетi")

    builder.button(text="🔁 На головну")

    builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)


async def show_users(users: List[UserReadSchemaDB]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for user in users:
        display_name = _format_user_display_name(user.user_id, user.username)
        builder.button(text=display_name, callback_data=f"admin:show_user_{user.user_id}")

    # await add_auto_back(builder, "admin:show_users")

    builder.adjust(1)

    return builder.as_markup()


async def show_user_data(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="🎟️ Доступи", callback_data=f"admin:show_user_subscriptions_{user_id}")

    await add_auto_back(builder, f"admin:show_user_{user_id}")

    builder.adjust(1)

    return builder.as_markup()


async def show_user_subscriptions(user_id: int, is_null: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="➕ Надати доступ", callback_data=f"admin:grant_access_{user_id}")

    if not is_null:
        builder.button(text="✅ Відкрити всі доступи", callback_data=f"admin:open_all_accesses_{user_id}")
        builder.button(text="❌ Закрити всі доступи", callback_data=f"admin:close_all_accesses_{user_id}")

    await add_auto_back(builder, f"admin:show_user_subscriptions_{user_id}")

    builder.adjust(1)

    return builder.as_markup()


async def manage_courses_menu(modules: List[Tuple[int, int]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    next_module_number = max((module_no for module_no, _ in modules), default=0) + 1
    builder.button(text="📑 Додати урок до нового модуля", callback_data=f"admin:add_module_lesson_{next_module_number}")

    for module_number, lesson_count in modules:
        builder.button(
            text=f"📚 Модуль №{module_number} ({lesson_count} ур.)",
            callback_data=f"admin:manage_course_{module_number}"
        )

    builder.adjust(1)

    return builder.as_markup()


async def manage_course_menu(module_number: int, lessons: List[LessonReadSchemaDB]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="📑 Додати урок", callback_data=f"admin:add_module_lesson_{module_number}")

    for lesson in lessons:
        builder.button(
            text=f"📖 {lesson.title} №{lesson.lesson_number}",
            callback_data=f"admin:manage_module_lesson_{module_number}_{lesson.lesson_number}"
        )

    builder.adjust(1)

    return builder.as_markup()


async def manage_module_lesson_menu(module_number: int, lesson_number: int, lesson: LessonReadSchemaDB
                                    ) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if lesson.video_file_id:
        builder.button(text="📽️ Показати відео", callback_data=f"admin:show_video_{module_number}_{lesson_number}")

    if lesson.pdf_file_id:
        builder.button(text="📄 Показати PDF", callback_data=f"admin:show_pdf_{module_number}_{lesson_number}")

    builder.button(text="✏️ Змінити назву", callback_data=f"admin:change_title_{module_number}_{lesson_number}")
    builder.button(text="✏️ Змінити відео", callback_data=f"admin:change_video_{module_number}_{lesson_number}")
    builder.button(text="✏️ Змінити PDF", callback_data=f"admin:change_pdf_{module_number}_{lesson_number}")

    builder.button(text="🗑️ Видалити урок", callback_data=f"admin:ask_delete_lesson_{module_number}_{lesson_number}")

    await add_auto_back(builder, f"admin:manage_module_lesson_{module_number}_{lesson_number}")

    builder.adjust(1)

    return builder.as_markup()


async def delete_module_lesson(module_number: int, lesson_number: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Видалити урок", callback_data=f"admin:delete_lesson_{module_number}_{lesson_number}")
    await add_auto_back(builder, f"admin:ask_delete_lesson_{module_number}_{lesson_number}")

    builder.adjust(1)

    return builder.as_markup()


async def tickets_menu(tickets: List[TicketReadSchemaDB]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for ticket in tickets:
        status_emoji: str = {
            TicketStatus.OPEN: "✅",
            TicketStatus.PENDING: "⏳",
            TicketStatus.CLOSED: "❌"
        }.get(ticket.status, "❓")

        builder.button(text=f"{status_emoji} | ID: {ticket.id}", callback_data=f"admin:ticket_{ticket.id}")

    await add_auto_back(builder, "help:R_admin_tickets_menu")

    builder.adjust(1)

    return builder.as_markup()


async def ticket_menu(ticket_id: int, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="💬 Відповісти", callback_data=f"help:admin_respond_{ticket_id}_{user_id}")
    builder.button(text="❌ Закрити тикет", callback_data=f"help:admin_close_{ticket_id}_{user_id}")

    builder.adjust(1)

    return builder.as_markup()


async def go_back(callback: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    await add_auto_back(builder, callback)

    return builder.as_markup()


async def back_to_start() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔁 На головну")

    return builder.as_markup(resize_keyboard=True)


def _find_next_available_module_number(modules: List[LessonReadSchemaDB]) -> int:
    if not modules:
        return 1

    module_numbers = sorted([module.module_number for module in modules])

    for i, module_number in enumerate(module_numbers, start=1):
        if module_number != i:
            return i

    return max(module_numbers) + 1


def _format_user_display_name(user_id: str, username: str | None = None) -> str:
    parts = []

    if username:
        parts.append(f"@{username}")

    if parts:
        return " | ".join(parts)
    else:
        return f"ID {user_id}"


def _format_date(date: datetime) -> str:
    if date is None:
        return "Не вказано"

    return date.strftime('%d.%m.%Y %H:%M:%S')
