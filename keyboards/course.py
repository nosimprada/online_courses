import math
from typing import List, Dict, Any

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from utils.pagination import add_pagination_buttons
from utils.schemas.lesson import LessonReadSchemaDB


def courses_menu(modules: List[Dict[str, Any]], page: int = 1, per_page: int = 5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    total_modules = len(modules)
    total_pages = math.ceil(total_modules / per_page) if total_modules > 0 else 1

    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    modules_page = modules[start_index:end_index]

    for module in modules_page:
        builder.button(
            text=f"📕 Модуль №{module["module_number"]} ({module["lesson_count"]} ур.)",
            callback_data=f"course:module_{module["module_number"]}_1"
        )

    if total_pages > 1:
        add_pagination_buttons(builder, page, total_pages, "course:menu_page")

    builder.adjust(1)

    return builder.as_markup()


def course_menu(lessons: List[LessonReadSchemaDB], module_number: int,
                page: int = 1, per_page: int = 5) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    total_lessons = len(lessons)
    total_pages = math.ceil(total_lessons / per_page) if total_lessons > 0 else 1

    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    lessons_page = lessons[start_index:end_index]

    for lesson in lessons_page:
        builder.button(
            text=f"📖 {lesson.title} №{lesson.lesson_number}",
            callback_data=f"course:lesson_{lesson.module_number}_{lesson.lesson_number}"
        )

    if total_pages > 1:
        add_pagination_buttons(builder, page, total_pages, f"course:module_{module_number}")

    builder.button(text="До модуля", callback_data=f"course:module_{module_number}_1")

    builder.adjust(1)

    return builder.as_markup()
