from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import outboxes.course as outbox

router = Router()


@router.message(F.text == "Навчання 📚")
async def menu(message: Message) -> None:
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
