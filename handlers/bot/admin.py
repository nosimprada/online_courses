from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

import outboxes.admin as outbox

router = Router()


# ---------------------------- FSM States ----------------------------

class GrantSubscriptionState(StatesGroup):
    access_to = State()


class CreateLessonState(StatesGroup):
    title = State()
    video = State()
    pdf = State()


class UpdateLessonTitle(StatesGroup):
    title = State()


class UpdateLessonVideo(StatesGroup):
    video = State()


class UpdateLessonPDF(StatesGroup):
    pdf = State()


# ---------------------------- Users / Orders ----------------------------

@router.callback_query(F.data.startswith("admin:show_user_subscriptions_"))
async def show_user_subscriptions(callback: CallbackQuery) -> None:
    await outbox.show_user_subscriptions(callback)


@router.callback_query(F.data == "admin:show_users")
async def show_users(callback: CallbackQuery) -> None:
    await outbox.show_users(callback)


@router.callback_query(F.data.startswith("admin:show_user_"))
async def show_user_data(callback: CallbackQuery) -> None:
    await outbox.show_user_data(callback)


# ---------------------------- Subscriptions ----------------------------


@router.callback_query(F.data == "admin:show_active_accesses")
async def show_active_accesses(callback: CallbackQuery) -> None:
    await outbox.show_active_accesses(callback)


@router.callback_query(F.data.startswith("admin:grant_access_"))
async def handle_grant_access(callback: CallbackQuery, state: FSMContext) -> None:
    tg_id = int(callback.data.split("_")[-1])

    await state.set_state(GrantSubscriptionState.access_to)
    await state.update_data(user_id=tg_id)

    await outbox.handle_grant_access_prompt(callback)


@router.message(F.text, StateFilter(GrantSubscriptionState.access_to))
async def input_grant_access(message: Message, state: FSMContext) -> None:
    await outbox.input_grant_access(message, state)


@router.callback_query(F.data.startswith("admin:open_all_accesses_"))
async def open_all_accesses(callback: CallbackQuery) -> None:
    await outbox.open_all_accesses(callback)


@router.callback_query(F.data.startswith("admin:close_all_accesses_"))
async def close_all_accesses(callback: CallbackQuery) -> None:
    await outbox.close_all_accesses(callback)


# ---------------------------- Courses / Lessons ----------------------------

@router.callback_query(F.data == "admin:courses")
async def manage_courses(callback: CallbackQuery) -> None:
    await outbox.manage_courses_page(callback)


@router.callback_query(F.data.startswith("admin:manage_course_"))
async def manage_course_page(callback: CallbackQuery) -> None:
    await outbox.manage_course_page(callback)


@router.callback_query(F.data.startswith("admin:add_module_lesson_"))
async def add_module_lesson(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CreateLessonState.title)
    await outbox.add_module_lesson(callback, state)


@router.message(F.text, StateFilter(CreateLessonState.title))
async def add_module_lesson_title(message: Message, state: FSMContext) -> None:
    await state.set_state(CreateLessonState.video)
    await outbox.add_module_lesson_title(message, state)


@router.message(F.content_type == ContentType.VIDEO, StateFilter(CreateLessonState.video))
async def add_module_lesson_video(message: Message, state: FSMContext) -> None:
    await state.set_state(CreateLessonState.pdf)
    await outbox.add_module_lesson_video(message, state)


@router.message(F.text == "-", StateFilter(CreateLessonState.video))
async def skip_add_module_lesson_video(message: Message, state: FSMContext) -> None:
    await state.set_state(CreateLessonState.pdf)
    await outbox.skip_add_module_lesson_video(message, state)


@router.message(F.content_type == ContentType.DOCUMENT, StateFilter(CreateLessonState.pdf))
async def add_module_lesson_pdf(message: Message, state: FSMContext) -> None:
    await outbox.add_module_lesson_pdf(message, state)


@router.message(F.text == "-", StateFilter(CreateLessonState.pdf))
async def skip_add_module_lesson_pdf(message: Message, state: FSMContext) -> None:
    await outbox.skip_add_module_lesson_pdf(message, state)


@router.callback_query(F.data.startswith("admin:manage_module_lesson_"))
async def manage_module_lesson(callback: CallbackQuery) -> None:
    await outbox.manage_module_lesson(callback)


@router.callback_query(F.data.startswith("admin:show_video_"))
async def show_lesson_video(callback: CallbackQuery) -> None:
    await outbox.show_lesson_video(callback)


@router.callback_query(F.data.startswith("admin:show_pdf_"))
async def show_lesson_pdf(callback: CallbackQuery) -> None:
    await outbox.show_lesson_pdf(callback)


@router.callback_query(F.data.startswith("admin:change_title_"))
async def update_lesson_title(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UpdateLessonTitle.title)
    await outbox.update_lesson_title(callback, state)


@router.message(F.text, StateFilter(UpdateLessonTitle.title))
async def update_lesson_title_text(message: Message, state: FSMContext) -> None:
    await outbox.update_lesson_title_text(message, state)


@router.callback_query(F.data.startswith("admin:change_video_"))
async def update_lesson_video(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UpdateLessonVideo.video)
    await outbox.update_lesson_video(callback, state)


@router.message(F.content_type == ContentType.VIDEO, StateFilter(UpdateLessonVideo.video))
async def update_lesson_video_content(message: Message, state: FSMContext) -> None:
    await outbox.update_lesson_video_content(message, state)


@router.message(F.text == "-", StateFilter(UpdateLessonVideo.video))
async def cancel_update_lesson_video(message: Message, state: FSMContext) -> None:
    await outbox.cancel_update_lesson_video(message, state)


@router.callback_query(F.data.startswith("admin:change_pdf_"))
async def update_lesson_pdf(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UpdateLessonPDF.pdf)
    await outbox.update_lesson_pdf(callback, state)


@router.message(F.content_type == ContentType.DOCUMENT, StateFilter(UpdateLessonPDF.pdf))
async def update_lesson_pdf_content(message: Message, state: FSMContext) -> None:
    await outbox.update_lesson_pdf_content(message, state)


@router.message(F.text == "-", StateFilter(UpdateLessonPDF.pdf))
async def cancel_update_lesson_pdf(message: Message, state: FSMContext) -> None:
    await outbox.cancel_update_lesson_pdf(message, state)


@router.callback_query(F.data.startswith("admin:ask_delete_lesson_"))
async def ask_delete_module_lesson(callback: CallbackQuery) -> None:
    await outbox.ask_delete_module_lesson(callback)


@router.callback_query(F.data.startswith("admin:delete_lesson_"))
async def delete_module_lesson(callback: CallbackQuery) -> None:
    await outbox.delete_module_lesson(callback)


# TODO: Tickets

# ---------------------------- Tickets -------------------------


@router.message(F.text == "❓ Тикети")
async def show_tickets(message: Message) -> None:
    await message.answer("TODO: show tickets")


# ---------------------------- Menu ----------------------------

@router.message(F.text == "Адмін панель 🔧", StateFilter(None))
async def menu(message: Message) -> None:
    await outbox.menu(message)
