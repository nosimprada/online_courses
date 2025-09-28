from datetime import datetime, timedelta
from typing import List, Tuple

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InputMediaDocument, InputMediaVideo

import keyboards.admin as admin_kb
from utils.enums.order import OrderStatus
from utils.enums.subscription import SubscriptionStatus
from utils.schemas.lesson import LessonCreateSchemaDB, LessonUpdateSchemaDB, LessonReadSchemaDB
from utils.schemas.order import OrderCreateSchemaDB
from utils.schemas.subscription import SubscriptionReadSchemaDB, SubscriptionCreateSchemaDB
from utils.services.lesson import get_all_modules_with_lesson_count, get_lessons_by_module, create_lesson, \
    get_lesson_by_module_and_lesson_number, delete_lesson, get_lesson_by_id
from utils.services.lesson import update_lesson
from utils.services.order import get_orders_by_tg_id, create_order
from utils.services.subscription import get_subscriptions_by_tg_id, get_active_subscriptions, \
    close_subscriptions_access, open_subscriptions_access, create_subscription
from utils.services.user import get_all_users, get_user_by_tg_id

router = Router()


# class SetUserEmailState(StatesGroup):
#     email = State()


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


@router.callback_query(F.data.startswith("admin:show_user_orders_"))
async def show_user_orders(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])

    orders = await get_orders_by_tg_id(user_id)
    if not orders:
        await callback.message.edit_text("Користувач не має замовлень.", reply_markup=admin_kb.back_to_admin())
        await callback.answer()
        return

    msg = f"\n<i>Замовлення користувача (ID {user_id}):</i>\n\n"

    for order in orders:
        msg += f"📦 <b>ID:</b> <code>{order.id}</code>\n"
        msg += f"💰 <b>Сума:</b> <code>{order.amount}</code>\n"
        msg += f"🔔 <b>Статус:</b> <code>{order.status}</code>\n"
        msg += f"⌚ <b>Створено:</b> <code>{_normalize_date(order.created_at)}</code>\n"
        msg += f"💸 <b>Сплачено:</b> <code>{_normalize_date(order.paid_at)}</code>\n\n"

    await callback.message.edit_text(msg, reply_markup=admin_kb.back_to_admin_or_user(user_id))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:show_user_subscriptions_"))
async def show_user_subscriptions(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])

    subscriptions = await get_subscriptions_by_tg_id(user_id)
    if not subscriptions:
        await callback.message.edit_text(
            "Користувач не має доступів.",
            reply_markup=admin_kb.show_user_subscriptions(user_id, True)
        )
        await callback.answer()
        return

    msg = f"\n<i>Доступи користувача (ID {user_id}):</i>\n\n"

    for subscription in subscriptions:
        msg += f"🎟️ <b>ID:</b> <code>{subscription.id}</code>\n"
        msg += f"📦 <b>ID замовлення:</b> <code>{subscription.order_id}</code>\n"
        msg += f"📅 <b>Початок доступу:</b> <code>{subscription.access_from}</code>\n"
        msg += f"📅 <b>Кінець доступу:</b> <code>{subscription.access_to}</code>\n"
        msg += f"🔔 <b>Статус:</b> <code>{subscription.status}</code>\n"
        msg += f"⌚ <b>Створено:</b> <code>{_normalize_date(subscription.created_at)}</code>\n\n"

    await callback.message.edit_text(msg, reply_markup=admin_kb.show_user_subscriptions(user_id, False))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:show_user_"))
async def show_user_data(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])

    user = await get_user_by_tg_id(user_id)
    if not user:
        await callback.message.edit_text("Користувач не знайдено.", reply_markup=admin_kb.back_to_admin())
        await callback.answer()
        return

    msg = (
        f"👤 <b>Інформація про користувача</b>\n\n"
        f"🆔 <b>User ID:</b> <code>{user.user_id}</code>\n"
    )

    if user.username:
        msg += f"👤 <b>Username:</b> @{user.username}\n"

    msg += f"📅 <b>Створено:</b> <code>{_normalize_date(user.created_at)}</code>\n"

    msg += f"\n📋 Оберіть категорію для перегляду:"

    await callback.message.edit_text(msg, reply_markup=admin_kb.show_user_data(user_id))
    await callback.answer()


@router.callback_query(F.data == "admin:menu")
async def menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Виберіть дію:", reply_markup=admin_kb.menu())
    await callback.answer()


@router.callback_query(F.data == "admin:show_users")
async def show_users(callback: CallbackQuery) -> None:
    users = await get_all_users()

    await callback.message.edit_text(
        f"Кількість користувачів: <code>{len(users)}</code>",
        reply_markup=admin_kb.show_users(users)
    )

    await callback.answer()


@router.callback_query(F.data == "admin:show_active_accesses")
async def show_active_accesses(callback: CallbackQuery) -> None:
    active_subscriptions = await get_active_subscriptions()
    if not active_subscriptions:
        await callback.message.edit_text("Немає активних доступів.", reply_markup=admin_kb.back_to_admin())
        await callback.answer()
        return

    msg = "\n<i>Активні доступи користувачів:</i>\n\n"

    for subscription in active_subscriptions:
        if subscription.user_id:
            msg += f"🆔 <b>ID користувача:</b> <code>{subscription.user_id}</code>\n"

        msg += f"📅 <b>Кінець доступу:</b> <code>{_normalize_date(subscription.access_to)}</code>\n"
        msg += f"⏰ <b>Створено:</b> <code>{_normalize_date(subscription.created_at)}</code>\n\n"

    await callback.message.edit_text(msg, reply_markup=admin_kb.back_to_admin())
    await callback.answer()


# @router.callback_query(F.data.startswith("admin:set_user_email_"))
# async def handle_set_user_email(callback: CallbackQuery, state: FSMContext) -> None:
#     user_id = int(callback.data.split("_")[-1])
#
#     await state.set_state(SetUserEmailState.email)
#     await state.update_data(user_id=user_id)
#
#     await callback.message.edit_text(
#         "Введіть нову електронну пошту користувача.\n"
#         "Для скасування дії введіть «-»."
#     )
#
#     await callback.answer()
#
#
# @router.message(F.text, StateFilter(SetUserEmailState.email))
# async def input_set_user_email(message: Message, state: FSMContext) -> None:
#     data = await state.get_data()
#     user_id = data.get("user_id")
#
#     if message.text == "-":
#         await state.clear()
#         await message.answer("❌ Дія скасована.", reply_markup=admin_kb.back_to_admin_or_user(user_id))
#         return
#
#     try:
#         set_email = await set_user_email(user_id, message.text)
#         if set_email and set_email.email == message.text:
#             await message.answer(
#                 "✅ Електронна пошта успішно змінена.",
#                 reply_markup=admin_kb.back_to_admin_or_user(user_id)
#             )
#             await state.clear()
#             return
#
#     except Exception as e:
#         print(f"Error setting email for user {user_id}: {str(e)}")
#
#     await message.answer(
#         "❌ Сталася помилка під час зміни електронної пошти. Спробуйте пізніше.",
#         reply_markup=admin_kb.back_to_admin_or_user(user_id)
#     )
#     await state.clear()


@router.callback_query(F.data.startswith("admin:grant_access_"))
async def handle_grant_access(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = int(callback.data.split("_")[-1])

    await state.set_state(GrantSubscriptionState.access_to)
    await state.update_data(user_id=user_id)

    await callback.message.edit_text(
        "Введіть термін для надання доступу (у місяцях).\n"
        "Для скасування дії введіть «-»."
    )

    await callback.answer()


@router.message(F.text, StateFilter(GrantSubscriptionState.access_to))
async def input_grant_access(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get("user_id")

    if message.text == "-":
        await state.clear()
        await message.answer("❌ Дія скасована.", reply_markup=admin_kb.back_to_admin_or_user(user_id))
        return

    try:
        months = int(message.text)
        if months <= 0:
            await message.answer(
                "❌ Введіть позитивне число місяців.\n"
                "Спробуйте ще раз або введіть «-» для скасування."
            )
            return
    except ValueError:
        await message.answer(
            "❌ Введіть коректне число місяців.\n"
            "Спробуйте ще раз або введіть «-» для скасування."
        )
        return

    try:
        order = await create_order(OrderCreateSchemaDB(
            user_id=user_id,
            amount=0.0,
            status=OrderStatus.COMPLETED.value
        ))

        access_from = datetime.now()
        access_to = access_from + timedelta(days=months * 30)

        subscription = await create_subscription(SubscriptionCreateSchemaDB(
            user_id=user_id,
            order_id=order.id,
            access_from=access_from,
            access_to=access_to,
            status=SubscriptionStatus.CREATED.value
        ))

        if subscription.user_id == user_id:
            await message.answer(
                f"✅ Доступ успішно надано користувачу (ID {user_id}) на {months} місяць(ів).\n"
                f"📅 Доступ до: {_normalize_date(access_to)}",
                reply_markup=admin_kb.back_to_admin_or_user(user_id)
            )
            await state.clear()
            return

    except Exception as e:
        print(f"Error granting access to user {user_id}: {str(e)}")
        await message.answer(
            "❌ Сталася помилка під час надання доступу. Спробуйте пізніше.",
            reply_markup=admin_kb.back_to_admin_or_user(user_id)
        )
        await state.clear()


@router.callback_query(F.data.startswith("admin:open_all_accesses_"))
async def open_all_accesses(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])

    try:
        opened = await open_subscriptions_access(user_id)
        message_text, reply_markup = _are_subscriptions_updated(opened, "open", user_id)
        await callback.message.edit_text(message_text, reply_markup=reply_markup)

    except Exception as e:
        print(f"Error opening access for user {user_id}: {str(e)}")
        await callback.message.edit_text(
            f"❌ Сталася помилка при відкритті доступів користувача (ID {user_id}).",
            reply_markup=admin_kb.back_to_admin_or_user(user_id)
        )

    await callback.answer()


@router.callback_query(F.data.startswith("admin:close_all_accesses_"))
async def close_all_accesses(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split("_")[-1])

    try:
        closed = await close_subscriptions_access(user_id)
        message_text, reply_markup = _are_subscriptions_updated(closed, "close", user_id)
        await callback.message.edit_text(message_text, reply_markup=reply_markup)

    except Exception as e:
        print(f"Error closing access for user {user_id}: {str(e)}")
        await callback.message.edit_text(
            f"❌ Сталася помилка при закритті доступів користувача (ID {user_id}).",
            reply_markup=admin_kb.back_to_admin_or_user(user_id)
        )

    await callback.answer()


@router.callback_query(F.data == "admin:courses")
async def manage_courses(callback: CallbackQuery) -> None:
    modules = await get_all_modules_with_lesson_count()

    if modules is None:
        modules = []

    if not modules:
        await callback.message.edit_text(
            "Немає активних модулів.", reply_markup=admin_kb.manage_courses_menu(modules)
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "Активні модулі:\n",
        reply_markup=admin_kb.manage_courses_menu(modules)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:manage_course_"))
async def manage_course(callback: CallbackQuery) -> None:
    module_number = int(callback.data.split("_")[-1])

    lessons = await get_lessons_by_module(module_number)
    if not lessons:
        await callback.message.edit_text("Немає модуля з цим номером.", reply_markup=admin_kb.back_to_admin())
        await callback.answer()
        return

    await callback.message.edit_text(
        f"Активні уроки модуля №{module_number}:",
        reply_markup=admin_kb.manage_course_menu(module_number, lessons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:add_module_lesson_"))
async def add_module_lesson(callback: CallbackQuery, state: FSMContext) -> None:
    module_number = int(callback.data.split("_")[-1])

    lessons = await get_lessons_by_module(module_number)
    lesson_number = _find_next_available_lesson_number(lessons)

    await state.update_data(module_number=module_number, lesson_number=lesson_number)
    await state.set_state(CreateLessonState.title)

    await callback.message.edit_text(
        "Введіть заголовок урока:\n"
        "Для скасування дії введіть «-»."
    )
    await callback.answer()


@router.message(F.text, StateFilter(CreateLessonState.title))
async def add_module_lesson_title(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    module_number = data.get("module_number")

    if message.text == "-":
        await state.clear()
        await message.answer("❌ Дія скасована.", reply_markup=admin_kb.back_to_module(module_number))
        return

    await state.update_data(title=message.text)
    await state.set_state(CreateLessonState.video)

    await message.answer("Надішліть відео для курсу (якщо хочете залишити поле порожнім, надішліть «-»).")


@router.message(F.content_type == ContentType.VIDEO, StateFilter(CreateLessonState.video))
async def add_module_lesson_video(message: Message, state: FSMContext) -> None:
    await state.update_data(video=message.video.file_id)
    await state.set_state(CreateLessonState.pdf)

    await message.answer("Надішліть PDF для курсу (якщо хочете залишити поле порожнім, надішліть «-»).")


@router.message(F.text == "-", StateFilter(CreateLessonState.video))
async def skip_add_module_lesson_video(message: Message, state: FSMContext) -> None:
    await state.update_data(video=None)
    await state.set_state(CreateLessonState.pdf)

    await message.answer("Надішліть PDF для курсу (якщо хочете залишити поле порожнім, надішліть «-»).")


@router.message(F.content_type == ContentType.DOCUMENT, StateFilter(CreateLessonState.pdf))
async def add_module_lesson_pdf(message: Message, state: FSMContext) -> None:
    await _process_create_module_lesson(message, state, message.document.file_id)


@router.message(F.text == "-", StateFilter(CreateLessonState.pdf))
async def skip_add_module_lesson_pdf(message: Message, state: FSMContext) -> None:
    await _process_create_module_lesson(message, state, None)


@router.callback_query(F.data.startswith("admin:manage_module_lesson_"))
async def manage_module_lesson(callback: CallbackQuery) -> None:
    parts = callback.data.split("_")

    module_number = int(parts[-2])
    lesson_number = int(parts[-1])

    lesson = await get_lesson_by_module_and_lesson_number(module_number, lesson_number)

    if not lesson:
        await callback.message.edit_text(
            f"❌ Урок №{lesson_number} у модулі №{module_number} не знайдено.",
            reply_markup=admin_kb.back_to_module(module_number)
        )
        await callback.answer()
        return

    msg = (
        f"📖 Модуль №{module_number} - Урок №{lesson_number}\n\n"
        f"📝 Назва: {lesson.title}\n"
        f"🎥 Відео: {'✅ Є' if lesson.video_file_id else '❌ Немає'}\n"
        f"📄 PDF: {'✅ Є' if lesson.pdf_file_id else '❌ Немає'}\n"
        f"📅 Створено: {_normalize_date(lesson.created_at)}\n"
    )

    if not callback.message.text:
        await callback.message.answer(
            msg,
            reply_markup=admin_kb.manage_module_lesson_menu(module_number, lesson_number, lesson)
        )
    else:
        await callback.message.edit_text(
            msg,
            reply_markup=admin_kb.manage_module_lesson_menu(module_number, lesson_number, lesson)
        )

    await callback.answer()


@router.callback_query(F.data.startswith("admin:show_video_"))
async def show_lesson_video(callback: CallbackQuery) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)

    lesson = await get_lesson_by_module_and_lesson_number(module_number, lesson_number)

    if not lesson:
        await callback.message.edit_text(
            f"❌ Урок №{lesson_number} у модулі №{module_number} не знайдено.",
            reply_markup=admin_kb.back_to_lesson(module_number, lesson_number)
        )
        await callback.answer()
        return

    await callback.message.edit_media(
        InputMediaVideo(media=lesson.video_file_id),
        reply_markup=admin_kb.back_to_lesson(module_number, lesson_number)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:show_pdf_"))
async def show_lesson_pdf(callback: CallbackQuery) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)

    lesson = await get_lesson_by_module_and_lesson_number(module_number, lesson_number)

    if not lesson:
        await callback.message.edit_text(
            f"❌ Урок №{lesson_number} у модулі №{module_number} не знайдено.",
            reply_markup=admin_kb.back_to_lesson(module_number, lesson_number)
        )
        await callback.answer()
        return

    await callback.message.edit_media(
        InputMediaDocument(media=lesson.pdf_file_id),
        reply_markup=admin_kb.back_to_lesson(module_number, lesson_number)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:change_title_"))
async def update_lesson_title(callback: CallbackQuery, state: FSMContext) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)

    await state.update_data(module_number=module_number, lesson_number=lesson_number)
    await state.set_state(UpdateLessonTitle.title)

    await callback.message.edit_text(
        "Введіть заголовок урока:\n"
        "Для скасування дії введіть «-»."
    )
    await callback.answer()


@router.message(F.text, StateFilter(UpdateLessonTitle.title))
async def update_lesson_title_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    module_number = data.get("module_number")
    lesson_number = data.get("lesson_number")

    if message.text == "-":
        await state.clear()
        await message.answer(
            "❌ Дія скасована.",
            reply_markup=admin_kb.back_to_lesson(module_number, lesson_number)
        )
        return

    await _process_update_module_lesson(
        message, state,
        update_type="title",
        new_value=message.text,
        success_message=f"✅ Заголовок урока успішно змінено на '{message.text}'."
    )


@router.callback_query(F.data.startswith("admin:change_video_"))
async def update_lesson_video(callback: CallbackQuery, state: FSMContext) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)

    await state.update_data(module_number=module_number, lesson_number=lesson_number)
    await state.set_state(UpdateLessonVideo.video)

    await callback.message.answer(
        "Надішліть відео уроку:\n"
        "Для скасування дії введіть «-»."
    )
    await callback.answer()


@router.message(F.content_type == ContentType.VIDEO, StateFilter(UpdateLessonVideo.video))
async def update_lesson_video_content(message: Message, state: FSMContext) -> None:
    await _process_update_module_lesson(
        message, state,
        update_type="video_file_id",
        new_value=message.video.file_id,
        success_message="✅ Відео урока успішно оновлено."
    )


@router.message(F.text == "-", StateFilter(UpdateLessonVideo.video))
async def cancel_update_lesson_video(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    module_number = data.get("module_number")
    lesson_number = data.get("lesson_number")

    await message.answer(
        "❌ Дія скасована.",
        reply_markup=admin_kb.back_to_lesson(module_number, lesson_number)
    )
    await state.clear()


@router.callback_query(F.data.startswith("admin:change_pdf_"))
async def update_lesson_pdf(callback: CallbackQuery, state: FSMContext) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)

    await state.update_data(module_number=module_number, lesson_number=lesson_number)
    await state.set_state(UpdateLessonPDF.pdf)

    await callback.message.answer(
        "Надішліть PDF файл уроку:\n"
        "Для скасування дії введіть «-»."
    )
    await callback.answer()


@router.message(F.content_type == ContentType.DOCUMENT, StateFilter(UpdateLessonPDF.pdf))
async def update_lesson_pdf_content(message: Message, state: FSMContext) -> None:
    pdf_name = message.document.file_name if message.document.file_name else "файл"
    success_message = f"✅ PDF урока успішно обновлено ({pdf_name})."

    await _process_update_module_lesson(
        message, state,
        update_type="pdf_file_id",
        new_value=message.document.file_id,
        success_message=success_message
    )


@router.message(F.text == "-", StateFilter(UpdateLessonPDF.pdf))
async def cancel_update_lesson_pdf(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    module_number = data.get("module_number")
    lesson_number = data.get("lesson_number")

    await message.answer(
        "❌ Дія скасована.",
        reply_markup=admin_kb.back_to_lesson(module_number, lesson_number)
    )
    await state.clear()


@router.callback_query(F.data.startswith("admin:ask_delete_lesson_"))
async def ask_delete_module_lesson(callback: CallbackQuery) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)

    await callback.message.edit_text(
        f"Ви дійсно хочете видалити урок {lesson_number} модуля {module_number}?",
        reply_markup=admin_kb.delete_module_lesson(module_number, lesson_number)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:delete_lesson_"))
async def delete_module_lesson(callback: CallbackQuery) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)

    try:
        lesson = await get_lesson_by_module_and_lesson_number(module_number, lesson_number)

        if not lesson:
            await callback.message.edit_text(
                f"❌ Урок №{lesson_number} у модулі №{module_number} не знайдено.",
                reply_markup=admin_kb.back_to_module(module_number)
            )
            await callback.answer()
            return

        await delete_lesson(lesson.id)

        deleted = await get_lesson_by_id(lesson.id)

        if not deleted:
            await callback.message.edit_text(
                f"✅ Урок {lesson_number} модуля {module_number} успішно видалено.",
                reply_markup=admin_kb.back_to_module(module_number)
            )
        else:
            await callback.message.edit_text(
                f"❌ Не вдалося видалити урок {lesson_number} модуля {module_number}. Спробуйте пізніше.",
                reply_markup=admin_kb.back_to_module(module_number)
            )

    except Exception as e:
        print(f"Error deleting lesson {lesson_number} in module {module_number}: {str(e)}")
        await callback.message.edit_text(
            f"❌ Сталася помилка під час видалення урока {lesson_number} модуля {module_number}. Спробуйте пізніше.",
            reply_markup=admin_kb.back_to_module(module_number)
        )

    await callback.answer()


@router.callback_query(F.data == "admin:back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Виберіть дію:", reply_markup=admin_kb.menu())
    await callback.answer()


def _are_subscriptions_updated(subscriptions: List[SubscriptionReadSchemaDB], action: str, user_id: int
                               ) -> Tuple[str, InlineKeyboardMarkup]:
    messages = {
        "open": {
            "success": f"✅ Всі доступи користувача (ID {user_id}) успішно відкрито.",
            "warn": f"⚠️ Частково відкрито доступи користувача (ID {user_id}). Деякі доступи не вдалося відкрити.",
            "error": f"❌ Не вдалося відкрити доступи користувача (ID {user_id})."
        },
        "close": {
            "success": f"✅ Всі доступи користувача (ID {user_id}) успішно закрито.",
            "warn": f"⚠️ Частково закрито доступи користувача (ID {user_id}). Деякі доступи не вдалося закрити.",
            "error": f"❌ Не вдалося закрити доступи користувача (ID {user_id})."
        }
    }

    if not subscriptions:
        return messages[action]["error"], admin_kb.back_to_admin()

    expected_status = SubscriptionStatus.ACTIVE.value if action == "open" else SubscriptionStatus.CANCELED.value
    success_count = sum(1 for sub in subscriptions if sub.status == expected_status)
    total_count = len(subscriptions)

    if success_count == total_count:
        return messages[action]["success"], admin_kb.back_to_admin_or_user(user_id)
    elif success_count > 0:
        return messages[action]["warn"], admin_kb.back_to_admin_or_user(user_id)
    else:
        return messages[action]["error"], admin_kb.back_to_admin_or_user(user_id)


async def _process_create_module_lesson(message: Message, state: FSMContext, pdf_file_id: str | None) -> None:
    data = await state.get_data()

    module_number = data.get("module_number")
    lesson_number = data.get("lesson_number")

    title = data.get("title")
    video_file_id = data.get("video")

    try:
        lesson = await create_lesson(LessonCreateSchemaDB(
            module_number=module_number,
            lesson_number=lesson_number,
            title=title,
            video_file_id=video_file_id,
            pdf_file_id=pdf_file_id
        ))

        video_status = "✅ Додано" if video_file_id else "❌ Не додано"
        pdf_status = "❌ Не додано"

        if pdf_file_id and hasattr(message, "document") and message.document:
            pdf_status = f"✅ Додано ({message.document.file_name})"
        elif pdf_file_id:
            pdf_status = "✅ Додано"

        if lesson.title == title:
            await message.answer(
                f"✅ Урок успішно створено!\n\n"
                f"📖 Модуль: {module_number}\n"
                f"📝 Урок: №{lesson_number} - {title}\n"
                f"🎥 Відео: {video_status}\n"
                f"📄 PDF: {pdf_status}\n",
                reply_markup=admin_kb.back_to_module(module_number)
            )
            await state.clear()
            return

    except Exception as e:
        print(f"Error creating lesson for module {module_number}: {str(e)}")
        await message.answer(
            "❌ Сталася помилка під час створення урока. Спробуйте пізніше.",
            reply_markup=admin_kb.back_to_module(module_number)
        )
        await state.clear()


async def _process_update_module_lesson(
        message: Message, state: FSMContext,
        update_type: str, new_value: str,
        success_message: str
) -> None:
    data = await state.get_data()

    module_number = data.get("module_number")
    lesson_number = data.get("lesson_number")

    try:
        update_data = {
            "module_no": module_number,
            "lesson_no": lesson_number,
            update_type: new_value
        }

        updated = await update_lesson(LessonUpdateSchemaDB(**update_data))

        if updated:
            updated_field_value = getattr(updated, update_type, None)
            if updated_field_value == new_value:
                await message.answer(
                    success_message,
                    reply_markup=admin_kb.back_to_lesson(module_number, lesson_number)
                )
                await state.clear()
                return

        raise Exception("Update verification failed")

    except Exception as e:
        print(f"Error updating {update_type} for lesson {lesson_number} in module {module_number}: {str(e)}")

        error_messages = {
            "title": "❌ Сталася помилка під час зміни назви уроку. Спробуйте пізніше.",
            "video_file_id": "❌ Сталася помилка під час оновлення відео. Спробуйте пізніше.",
            "pdf_file_id": "❌ Сталася помилка під час оновлення PDF. Спробуйте пізніше."
        }

        error_message = error_messages.get(update_type, "❌ Сталася помилка під час оновлення уроку. Спробуйте пізніше.")

        await message.answer(
            error_message,
            reply_markup=admin_kb.back_to_lesson(module_number, lesson_number)
        )
        await state.clear()


def _find_next_available_lesson_number(lessons: List[LessonReadSchemaDB]) -> int:
    if not lessons:
        return 1

    lesson_numbers = sorted([lesson.lesson_number for lesson in lessons])

    for i, lesson_number in enumerate(lesson_numbers, start=1):
        if lesson_number != i:
            return i

    return max(lesson_numbers) + 1


def _normalize_date(date: datetime) -> str:
    if date is None:
        return "Не вказано"

    return date.strftime('%d.%m.%Y %H:%M:%S')


def _get_module_lesson_number(callback: CallbackQuery) -> Tuple[int, int]:
    parts = callback.data.split("_")
    return int(parts[-2]), int(parts[-1])
