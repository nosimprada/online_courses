from typing import List, Tuple

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from utils.auto_back import add_auto_back
from utils.schemas.lesson import LessonReadSchemaDB


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


async def show_module_lesson(lesson: LessonReadSchemaDB) -> None:
    builder = InlineKeyboardBuilder()

    if lesson.video_file_id:
        builder.button(
            text="📄 Показати PDF",
            callback_data=f"course:show_pdf_{lesson.module_number}_{lesson.lesson_number}"
        )

    await add_auto_back(builder, f"course:module_lesson_{lesson.module_number}_{lesson.lesson_number}")

    builder.adjust(1)

    return builder.as_markup()
