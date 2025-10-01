from typing import Tuple

from aiogram import Router, F
from aiogram.types import CallbackQuery

import keyboards.course as course_kb
from keyboards.start import back_to_menu
from utils.services.lesson import get_all_modules_with_lesson_count, get_lessons_by_module

router = Router()


@router.callback_query(F.data.startswith("course:menu_page_"))
async def courses_menu(callback: CallbackQuery) -> None:
    try:
        page = int(callback.data.split("_")[-1])

        modules = await get_all_modules_with_lesson_count()

        if not modules:
            await callback.answer("❗ Немає курсів.")
            return

        await callback.message.edit_text(
            "Активні курси:",
            reply_markup=course_kb.courses_menu(modules, page)
        )

    except Exception as e:
        print(f"Error sending lesson modules for user {callback.from_user.id}: {e}")
        await callback.message.edit_text(
            "⛔️ Помилка показу модулів уроків. Спробуйте пізніше.",
            reply_markup=back_to_menu(),
        )

    await callback.answer()


@router.callback_query(F.data.startswith("course:module_"))
async def course_menu(callback: CallbackQuery) -> None:
    try:
        module_number, page = _get_module_lesson_number(callback)

        lessons = await get_lessons_by_module(module_number)

        if not lessons:
            await callback.answer("❗ Немає уроків модуля.")
            return

        await callback.message.edit_text(
            f"Активні уроки модуля №{module_number}:",
            reply_markup=course_kb.course_menu(lessons, module_number, page)
        )

    except Exception as e:
        print(f"Error sending module lessons for user {callback.from_user.id}: {e}")
        await callback.message.edit_text(
            "⛔️ Помилка показу уроків модуля. Спробуйте пізніше.",
            reply_markup=back_to_menu(),
        )

    await callback.answer()


def _get_module_lesson_number(callback: CallbackQuery) -> Tuple[int, int]:
    parts = callback.data.split("_")
    return int(parts[-2]), int(parts[-1])
