from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import outboxes.course as outbox
from middlewares.user import IsSubscribedMiddleware

router = Router()

router.message.middleware(IsSubscribedMiddleware())
router.callback_query.middleware(IsSubscribedMiddleware())


@router.message(F.text == "Навчання 📚")
async def lessons_menu(message: Message) -> None:
    await outbox.menu(message)


@router.callback_query(F.data.startswith("course:module_lesson_"))
async def show_module_lesson(callback: CallbackQuery) -> None:
    await outbox.show_module_lesson(callback)


@router.callback_query(F.data.startswith("course:module_"))
async def show_module(callback: CallbackQuery) -> None:
    await outbox.show_module(callback)


@router.callback_query(F.data.startswith("course:show_pdf_"))
async def show_module_lesson_pdf(callback: CallbackQuery) -> None:
    await outbox.show_module_lesson_pdf(callback)


@router.message(F.text == "Конспекти 📝")
async def notes_menu(message: Message) -> None:
    await outbox.notes_menu(message)


@router.callback_query(F.data.startswith("course:show_notes_"))
async def show_module_notes(callback: CallbackQuery) -> None:
    await outbox.show_module_notes(callback)


@router.callback_query(F.data.startswith("course:show_note_"))
async def show_lesson_note(callback: CallbackQuery) -> None:
    await outbox.show_lesson_note(callback)
