import math
from datetime import datetime
from typing import List, Dict, Any

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup, ReplyKeyboardBuilder

from utils.schemas.lesson import LessonReadSchemaDB
from utils.schemas.user import UserReadSchemaDB


def menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Користувачі", callback_data="admin:show_users")
    builder.button(text="Активні доступи", callback_data="admin:show_active_accesses")
    builder.button(text="Управління курсами", callback_data="admin:courses")

    builder.adjust(1)

    return builder.as_markup()


def show_users(users: List[UserReadSchemaDB]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for user in users:
        display_name = _format_user_display_name(user.user_id, user.username)
        builder.button(text=display_name, callback_data=f"admin:show_user_{user.user_id}")

    builder.button(text="↩️ Назад", callback_data="back_")

    builder.adjust(1)

    return builder.as_markup()


def show_user_data(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Замовлення", callback_data=f"admin:show_user_orders_{user_id}")
    builder.button(text="Доступи", callback_data=f"admin:show_user_subscriptions_{user_id}")

    builder.adjust(1)

    return builder.as_markup()


def show_user_subscriptions(user_id: int, is_null: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Надати доступ", callback_data=f"admin:grant_access_{user_id}")

    if not is_null:
        builder.button(text="Відкрити всі доступи", callback_data=f"admin:open_all_accesses_{user_id}")
        builder.button(text="Закрити всі доступи", callback_data=f"admin:close_all_accesses_{user_id}")

    builder.button(text="До користувача", callback_data=f"admin:show_user_{user_id}")

    builder.button(text="В адмін-панель", callback_data="admin:back_to_menu")

    builder.adjust(1)

    return builder.as_markup()


def manage_courses_menu(modules: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Додати урок", callback_data=f"admin:add_module_lesson_{len(modules) + 1}")

    for module in modules_page:
        builder.button(
            text=f"Модуль №{module["module_number"]} ({module["lesson_count"]} ур.)",
            callback_data=f"admin:manage_course_page_{module["module_number"]}_1"
        )

    if total_pages > 1:
        add_pagination_buttons(builder, page, total_pages, "admin:courses_page")

    builder.button(text="В адмін-панель", callback_data="admin:back_to_menu")

    builder.adjust(1)

    return builder.as_markup()


def manage_course_menu(module_number: int, lessons: List[LessonReadSchemaDB],
                       page: int = 1, per_page: int = 8) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Додати урок", callback_data=f"admin:add_module_lesson_{module_number}")

    total_lessons = len(lessons)
    total_pages = math.ceil(total_lessons / per_page) if total_lessons > 0 else 1

    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    lessons_page = lessons[start_index:end_index]

    for lesson in lessons_page:
        builder.button(
            text=f"📖 {lesson.title} №{lesson.lesson_number}",
            callback_data=f"admin:manage_module_lesson_{module_number}_{lesson.lesson_number}"
        )

    if total_pages > 1:
        add_pagination_buttons(builder, page, total_pages, f"admin:manage_course_page_{module_number}")

    builder.button(text="До управління курсами", callback_data="admin:courses_page_1")
    builder.button(text="В адмін-панель", callback_data="admin:back_to_menu")

    builder.adjust(1)

    return builder.as_markup()


def manage_module_lesson_menu(module_number: int, lesson_number: int, lesson: LessonReadSchemaDB
                              ) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if lesson.video_file_id:
        builder.button(text="Показати відео", callback_data=f"admin:show_video_{module_number}_{lesson_number}")

    if lesson.pdf_file_id:
        builder.button(text="Показати PDF", callback_data=f"admin:show_pdf_{module_number}_{lesson_number}")

    builder.button(text="Змінити назву", callback_data=f"admin:change_title_{module_number}_{lesson_number}")
    builder.button(text="Змінити відео", callback_data=f"admin:change_video_{module_number}_{lesson_number}")
    builder.button(text="Змінити PDF", callback_data=f"admin:change_pdf_{module_number}_{lesson_number}")

    builder.button(text="Видалити урок", callback_data=f"admin:ask_delete_lesson_{module_number}_{lesson_number}")

    builder.button(text="До уроків", callback_data=f"admin:manage_course_page_{module_number}_1")
    builder.button(text="В адмін-панель", callback_data=f"admin:back_to_menu")

    builder.adjust(1)

    return builder.as_markup()


def delete_module_lesson(module_number: int, lesson_number: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Видалити урок", callback_data=f"admin:delete_lesson_{module_number}_{lesson_number}")
    builder.button(text="❌ До уроку", callback_data=f"admin:manage_module_lesson_{module_number}_{lesson_number}")

    builder.adjust(1)

    return builder.as_markup()


def back_to_start() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="На головну", callback_data="back_to_start")

    return builder.as_markup(resize_keyboard=True)


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
