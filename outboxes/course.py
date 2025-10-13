from typing import Tuple

from aiogram.types import Message, CallbackQuery

import keyboards.course as course_kb
from keyboards.admin import go_back
from outboxes.admin import ERROR_MESSAGE
from utils.services.lesson import get_all_modules_with_lesson_count, get_lessons_by_module, \
    get_lesson_by_module_and_lesson_number, get_all_lessons


async def menu(message: Message) -> None:
    try:
        modules = await get_all_modules_with_lesson_count() or []

        if not modules:
            await message.answer("❌ Немає модулів.")
            return

        await message.answer(
            "🚀 Виберіть модуль, який хочете пройти:",
            reply_markup=await course_kb.menu(modules)
        )

    except Exception as e:
        print(f"Error showing course menu for user: {str(e)}")
        await message.answer(ERROR_MESSAGE)


async def show_module(callback: CallbackQuery) -> None:
    try:
        module_number = int(callback.data.split("_")[-1])
        lessons = await get_lessons_by_module(module_number) or []

        if not lessons:
            await callback.message.answer("❌ Немає уроків для цього модуля.")
            return

        await callback.message.answer(
            f"📚 Виберіть урок модуля №{module_number}, який хочете пройти:",
            reply_markup=await course_kb.show_module(lessons)
        )

    except Exception as e:
        print(f"Error showing module lessons for user: {str(e)}")
        await callback.message.answer(ERROR_MESSAGE)

    await callback.answer()


async def show_module_lesson(callback: CallbackQuery) -> None:
    try:
        module_number, lesson_number = _get_module_lesson_number(callback)
        lesson = await get_lesson_by_module_and_lesson_number(module_number, lesson_number) or []

        if not lesson:
            await callback.message.answer("❌ Немає уроку з цими параметрами.")
            return

        module = await get_lessons_by_module(module_number)
        if not module:
            await callback.message.answer(ERROR_MESSAGE)

        msg = f"📑 <b>№{lesson.lesson_number} | {lesson.title}</b>"

        if lesson.video_file_id:
            await callback.message.answer_video(
                lesson.video_file_id,
                caption=msg,
                reply_markup=await course_kb.show_module_lesson(lesson, len(module)),
                protect_content=True, supports_streaming=True
            )
        else:
            await callback.message.answer(
                msg,
                reply_markup=await course_kb.show_module_lesson(lesson, len(module))
            )

    except Exception as e:
        print(f"Error showing module lesson for user: {str(e)}")
        await callback.message.answer(ERROR_MESSAGE)

    await callback.answer()


async def show_module_lesson_pdf(callback: CallbackQuery) -> None:
    try:
        module_number, lesson_number = _get_module_lesson_number(callback)
        lesson = await get_lesson_by_module_and_lesson_number(module_number, lesson_number) or []

        if not lesson:
            await callback.message.answer("❌ Немає уроку з цими параметрами.")
            return

        msg = f"📑 <b>№{lesson.lesson_number} | {lesson.title}</b>"

        if lesson.pdf_file_id:
            await callback.message.answer_document(
                lesson.pdf_file_id,
                caption=msg,
                reply_markup=await go_back(callback.data),
                protect_content=True
            )
        else:
            await callback.message.answer(
                ERROR_MESSAGE,
                reply_markup=await go_back(callback.data)
            )

    except Exception as e:
        print(f"Error showing module lesson for user: {str(e)}")
        await callback.message.answer(ERROR_MESSAGE)

    await callback.answer()


async def notes_menu(message: Message) -> None:
    try:
        lessons = await get_all_lessons() or []

        if not lessons:
            await message.answer("❌ Немає конспектів.")
            return

        await message.answer(
            "📝 Виберіть модуль для перегляду конспектів.",
            reply_markup=await course_kb.notes_menu(lessons)
        )

    except Exception as e:
        print(f"Error showing notes menu for user: {str(e)}")
        await message.answer(ERROR_MESSAGE)


async def show_module_notes(callback: CallbackQuery) -> None:
    try:
        module_number = int(callback.data.split("_")[-1])
        module = await get_lessons_by_module(module_number) or []

        if not module:
            await callback.message.answer("❌ Немає конспектів для цього модуля.")
            return

        await callback.message.answer(
            f"📝 Доступні конспекти для уроків модуля №{module_number}",
            reply_markup=await course_kb.show_module_notes(module)
        )

    except Exception as e:
        print(f"Error showing module notes for user: {str(e)}")
        await callback.message.answer(ERROR_MESSAGE)


async def show_lesson_note(callback: CallbackQuery) -> None:
    try:
        module_number, lesson_number = _get_module_lesson_number(callback)
        lesson = await get_lesson_by_module_and_lesson_number(module_number, lesson_number)

        if lesson is None:
            await callback.message.answer("❌ У цього уроку немає конспектів.")
            return

        await callback.message.answer_document(
            lesson.pdf_file_id,
            reply_markup=await go_back(callback.data)
        )

    except Exception as e:
        print(f"Error showing lesson note for user: {str(e)}")
        await callback.message.answer(ERROR_MESSAGE)


def _get_module_lesson_number(callback: CallbackQuery) -> Tuple[int, int]:
    parts = callback.data.split("_")
    return int(parts[-2]), int(parts[-1])
