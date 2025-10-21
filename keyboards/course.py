from typing import List, Tuple

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from utils.auto_back import add_auto_back
from utils.schemas.lesson import LessonReadSchemaDB
from utils.services.lesson import get_last_lesson_of_module


async def menu(modules: List[Tuple[int, int]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for module_number, lesson_count in modules:
        builder.button(
            text=f"📚 Модуль №{module_number} ({lesson_count} ур.)",
            callback_data=f"course:module_{module_number}"
        )

    builder.adjust(1)

    return builder.as_markup()


async def show_module(lessons: List[LessonReadSchemaDB]) -> None:
    builder = InlineKeyboardBuilder()

    for lesson in lessons:
        builder.button(
            text=f"📖 {lesson.title} №{lesson.lesson_number}",
            callback_data=f"course:module_lesson_{lesson.module_number}_{lesson.lesson_number}"
        )

    builder.adjust(1)

    return builder.as_markup()


async def show_module_lesson(lesson: LessonReadSchemaDB, total_lessons: int, total_modules: int) -> None:
    builder = InlineKeyboardBuilder()

    if lesson.pdf_file_id:
        builder.button(
            text="📄 Показати конспект",
            callback_data=f"course:show_pdf_{lesson.module_number}_{lesson.lesson_number}"
        )

    last_lesson = await get_last_lesson_of_module(lesson.module_number - 1)

    nav_buttons = []

    if lesson.lesson_number > 1:
        nav_buttons.append((
            "⬅️", f"course:module_lesson_{lesson.module_number}_{lesson.lesson_number - 1}"
        ))

    elif lesson.module_number > 1:
        nav_buttons.append((
            "⬅️ Модуль", f"course:module_lesson_{lesson.module_number - 1}_{last_lesson}"
        ))

    if lesson.lesson_number < total_lessons:
        nav_buttons.append((
            "➡️", f"course:module_lesson_{lesson.module_number}_{lesson.lesson_number + 1}"
        ))

    elif lesson.module_number < total_modules:
        nav_buttons.append((
            "Модуль ➡️", f"course:module_lesson_{lesson.module_number + 1}_1"
        ))

    for text, callback in nav_buttons:
        builder.button(text=text, callback_data=callback)

    await add_auto_back(builder, f"course:module_lesson_{lesson.module_number}_{lesson.lesson_number}")

    if len(list(builder.buttons)) > 0:
        builder.adjust(1)
    else:
        builder.adjust(1, len(nav_buttons), 1)

    return builder.as_markup()


async def notes_menu(lessons: List[LessonReadSchemaDB]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    sorted_lessons = sorted(lessons, key=lambda x: x.module_number)
    added_modules = set()

    for lesson in sorted_lessons:
        if lesson.pdf_file_id and lesson.module_number not in added_modules:
            added_modules.add(lesson.module_number)

            builder.button(
                text=f"📝 Модуль №{lesson.module_number}",
                callback_data=f"course:show_notes_{lesson.module_number}"
            )

    builder.adjust(1)

    return builder.as_markup()


async def show_module_notes(module: List[LessonReadSchemaDB]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    sorted_module = sorted(module, key=lambda x: x.lesson_number)

    for lesson in sorted_module:
        if lesson.pdf_file_id:
            builder.button(
                text=f"📖 №{lesson.lesson_number} | {lesson.title}",
                callback_data=f"course:show_note_{lesson.module_number}_{lesson.lesson_number}"
            )

    builder.adjust(1)

    return builder.as_markup()
