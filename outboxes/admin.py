import time
from datetime import datetime, timedelta
from typing import Final, List, Tuple, Optional
from uuid import uuid4

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup

import keyboards.admin as admin_kb
from utils.enums.order import OrderStatus
from utils.enums.subscription import SubscriptionStatus
from utils.schemas.lesson import LessonCreateSchemaDB, LessonUpdateSchemaDB, LessonReadSchemaDB
from utils.schemas.order import OrderCreateSchemaDB
from utils.schemas.subscription import SubscriptionReadSchemaDB, SubscriptionCreateSchemaDB
from utils.services.lesson import (
    get_all_modules_with_lesson_count,
    get_lessons_by_module,
    create_lesson,
    get_lesson_by_module_and_lesson_number,
    delete_lesson,
    get_lesson_by_id,
    update_lesson,
)
from utils.services.order import create_order
from utils.services.subscription import (
    create_subscription,
    get_subscriptions_by_user_id,
    get_active_subscriptions_by_user_id,
    update_subscription_status,
    update_subscription_access_period,
    update_subscription_user_id_by_subscription_id, )
from utils.services.user import get_all_users, get_user_by_tg_id, get_user_full_info_by_tg_id

ERROR_MESSAGE: Final = "❌ Сталася помилка. Спробуйте пізніше."


# async def menu(callback: CallbackQuery) -> None:
#     try:
#         users_with_ = await get_all_users()
#
#         msg = (
#             f"Кількість користувачів з активними підписками: {len(users)}"
#
#         )


# ============================ Users & Orders ============================

# async def show_user_orders(callback: CallbackQuery) -> None:
#     go_back = await admin_kb.go_back(callback.data)
#     try:
#         tg_id = int(callback.data.split("_")[-1])
#
#         orders = await get_orders_by_tg_id(tg_id)
#         if not orders:
#             await callback.message.answer("Користувач не має замовлень.", reply_markup=go_back)
#             await callback.answer()
#             return
#
#         msg = f"\n<i>Замовлення користувача (TG {tg_id}):</i>\n\n"
#
#         for order in orders:
#             msg += f"📦 <b>ID:</b> <code>{order.order_id}</code>\n"
#             msg += f"💰 <b>Сума:</b> <code>{order.amount}</code>\n"
#             msg += f"🔔 <b>Статус:</b> <code>{order.status.value}</code>\n"
#             msg += f"⌚ <b>Створено:</b> <code>{_format_date(order.created_at)}</code>\n"
#             msg += f"💸 <b>Сплачено:</b> <code>{_format_date(order.paid_at)}</code>\n\n"
#
#         await callback.message.answer(msg, reply_markup=go_back)
#
#     except Exception as e:
#         print(f"Error showing user orders: {str(e)}")
#         await callback.message.answer(ERROR_MESSAGE, reply_markup=go_back)
#
#     await callback.answer()


async def show_users(callback: CallbackQuery) -> None:
    go_back = await admin_kb.go_back(callback.data)

    try:
        users = await get_all_users()
        await callback.message.answer(
            f"Кількість користувачів: <code>{len(users)}</code>",
            reply_markup=await admin_kb.show_users(users)
        )

    except Exception as e:
        print(f"Error showing users list: {str(e)}")
        await callback.message.answer(ERROR_MESSAGE, reply_markup=go_back)

    await callback.answer()


async def show_user_data(callback: CallbackQuery) -> None:
    try:
        tg_id = int(callback.data.split("_")[-1])

        user = await get_user_full_info_by_tg_id(tg_id)
        if not user:
            await callback.message.answer("Користувач не знайдено.", reply_markup=await admin_kb.go_back(callback.data))
            await callback.answer()
            return

        username = f"@{getattr(user, 'username', '')}" if getattr(user, "username", None) else "Без Username"

        is_sub_text = "✅ Так" if getattr(user, "is_subscribed", False) else "❌ Ні"
        access_to_text = _format_date(getattr(user, "subscription_access_to", None))
        progress_text = f"{getattr(user, 'leaning_progress_procent', 0.0):.2f}%"

        emails_list = getattr(user, "emails", []) or []
        emails_text = ", ".join(emails_list) if emails_list else "—"

        completed_order_ids = getattr(user, "completed_order_ids", []) or []
        completed_orders_text = ", ".join(map(str, completed_order_ids)) if completed_order_ids else "—"

        expired_subscription_ids = getattr(user, "expired_subscription_ids", []) or []
        expired_subs_text = ", ".join(map(str, expired_subscription_ids)) if expired_subscription_ids else "—"

        created_at_text = _format_date(getattr(user, "created_at", None))

        msg = (
            "👤 <b>Інформація про користувача</b>\n\n"
            f"🆔 <b>TG ID:</b> <code>{tg_id}</code>\n"
            f"👤 <b>Username:</b> {username}\n"
            f"📅 <b>Створено:</b> <code>{created_at_text}</code>\n\n"
            f"🎟️ <b>Активна підписка:</b> {is_sub_text}\n"
            f"📆 <b>Доступ до:</b> <code>{access_to_text}</code>\n"
            f"📈 <b>Прогрес навчання:</b> {progress_text}\n"
            f"✉️ <b>Emails:</b> {emails_text}\n"
            f"✅ <b>Завершені замовлення (IDs):</b> {completed_orders_text}\n"
            f"⌛ <b>Протерміновані підписки (IDs):</b> {expired_subs_text}\n"
            f"\n📋 Оберіть категорію для перегляду:"
        )

        await callback.message.answer(msg, reply_markup=await admin_kb.show_user_data(tg_id))

    except Exception as e:
        print(f"Error showing user data: {str(e)}")
        await callback.message.answer(ERROR_MESSAGE, reply_markup=await admin_kb.go_back(callback.data))

    await callback.answer()


# ============================ Subscriptions ============================

async def show_user_subscriptions(callback: CallbackQuery) -> None:
    try:
        tg_id = int(callback.data.split("_")[-1])

        subscriptions = await _get_subscriptions_by_tg_id(tg_id)
        if not subscriptions:
            await callback.message.answer(
                "Користувач не має доступів.",
                reply_markup=await admin_kb.show_user_subscriptions(tg_id, True)
            )
            await callback.answer()
            return

        msg = f"\n<i>Доступи користувача (TG {tg_id}):</i>\n\n"
        for subscription in subscriptions:
            msg += f"🎟️ <b>ID:</b> <code>{subscription.id}</code>\n"
            msg += f"📦 <b>ID замовлення:</b> <code>{subscription.order_id}</code>\n"
            msg += f"📅 <b>Початок доступу:</b> <code>{_format_date(subscription.access_from)}</code>\n"
            msg += f"📅 <b>Кінець доступу:</b> <code>{_format_date(subscription.access_to)}</code>\n"
            msg += f"🔔 <b>Статус:</b> <code>{subscription.status.value}</code>\n"
            msg += f"⌚ <b>Створено:</b> <code>{_format_date(subscription.created_at)}</code>\n\n"

        await callback.message.answer(
            msg,
            reply_markup=await admin_kb.show_user_subscriptions(tg_id, False)
        )

    except Exception as e:
        print(f"Error showing user subscriptions: {str(e)}")
        await callback.message.answer(ERROR_MESSAGE, reply_markup=await admin_kb.go_back(callback.data))

    await callback.answer()


async def show_active_accesses(callback: CallbackQuery) -> None:
    go_back = await admin_kb.go_back(callback.data)

    try:
        active_subscriptions = await _get_all_active_subscriptions()
        if not active_subscriptions:
            await callback.message.answer("Немає активних доступів.", reply_markup=go_back)
            await callback.answer()
            return

        msg = "\n<i>Активні доступи користувачів:</i>\n\n"

        for subscription in active_subscriptions:
            if subscription.user_id:
                msg += f"🆔 <b>ID користувача:</b> <code>{subscription.user_id}</code>\n"

            msg += f"📅 <b>Кінець доступу:</b> <code>{_format_date(subscription.access_to)}</code>\n"
            msg += f"⏰ <b>Створено:</b> <code>{_format_date(subscription.created_at)}</code>\n\n"

        await callback.message.answer(msg, reply_markup=go_back)

    except Exception as e:
        print(f"Error showing active accesses: {str(e)}")
        await callback.message.answer(ERROR_MESSAGE, reply_markup=go_back)

    await callback.answer()


async def handle_grant_access_prompt(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "Введіть термін для надання доступу (у місяцях).\n"
        "Для скасування дії введіть «-»."
    )
    await callback.answer()


async def input_grant_access(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    tg_id = data.get("user_id")

    if message.text == "-":
        await state.clear()
        await message.answer("❌ Дія скасована.", reply_markup=await admin_kb.go_back(f"admin:grant_access_{tg_id}"))
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
        manual_order_id = int(time.time())
        manual_invoice_id = f"MANUAL-{uuid4().hex[:12].upper()}"

        order = await create_order(OrderCreateSchemaDB(
            user_id=tg_id,
            amount=0.0,
            invoice_id=manual_invoice_id,
            order_id=manual_order_id,
            status=OrderStatus.COMPLETED
        ))

        subscription = await create_subscription(SubscriptionCreateSchemaDB(order_id=order.order_id))

        user = await get_user_by_tg_id(tg_id)
        if not user:
            raise RuntimeError("User not found by TG ID")

        access_from = datetime.now()
        access_to = access_from + timedelta(days=months * 30)

        await update_subscription_user_id_by_subscription_id(subscription.id, user.user_id)
        await update_subscription_access_period(subscription.id, access_from, access_to)
        await update_subscription_status(subscription.id, SubscriptionStatus.ACTIVE)

        await message.answer(
            f"✅ Доступ успішно надано користувачу (TG {tg_id}) на {months} міс.\n"
            f"📅 Доступ до: {_format_date(access_to)}",
            reply_markup=await admin_kb.go_back(f"admin:show_user_subscriptions_{tg_id}")
        )
        await state.clear()

    except Exception as e:
        print(f"Error granting access to TG {tg_id}: {str(e)}")
        await message.answer(
            "❌ Сталася помилка під час надання доступу. Спробуйте пізніше.",
            reply_markup=await admin_kb.go_back(f"admin:grant_access_{tg_id}")
        )
        await state.clear()


async def open_all_accesses(callback: CallbackQuery) -> None:
    tg_id = int(callback.data.split("_")[-1])
    try:
        opened = await _open_subscriptions_access(tg_id)
        message_text, reply_markup = await _are_subscriptions_updated(opened, "open", tg_id)
        await callback.message.answer(message_text, reply_markup=reply_markup)
    except Exception as e:
        print(f"Error opening access for TG {tg_id}: {str(e)}")
        await callback.message.answer(
            f"❌ Сталася помилка при відкритті доступів користувача (TG {tg_id}).",
            reply_markup=await admin_kb.go_back(callback.data)
        )
    await callback.answer()


async def close_all_accesses(callback: CallbackQuery) -> None:
    tg_id = int(callback.data.split("_")[-1])
    try:
        closed = await _close_subscriptions_access(tg_id)
        message_text, reply_markup = await _are_subscriptions_updated(closed, "close", tg_id)
        await callback.message.answer(message_text, reply_markup=reply_markup)
    except Exception as e:
        print(f"Error closing access for TG {tg_id}: {str(e)}")
        await callback.message.answer(
            f"❌ Сталася помилка при закритті доступів користувача (TG {tg_id}).",
            reply_markup=await admin_kb.go_back(callback.data)
        )
    await callback.answer()


# ============================ Courses / Lessons ============================

async def manage_courses_page(callback: CallbackQuery) -> None:
    modules = await get_all_modules_with_lesson_count() or []
    if not modules:
        await callback.message.answer(
            "Немає активних модулів.",
            reply_markup=await admin_kb.manage_courses_menu(modules)
        )
        await callback.answer()
        return

    await callback.message.answer(
        "Активні модулі:\n",
        reply_markup=await admin_kb.manage_courses_menu(modules)
    )
    await callback.answer()


async def manage_course_page(callback: CallbackQuery) -> None:
    module_number = int(callback.data.split("_")[-1])
    lessons = await get_lessons_by_module(module_number)

    if not lessons:
        await callback.message.answer("Немає модуля з цим номером.", reply_markup=await admin_kb.go_back(callback.data))
        await callback.answer()
        return

    await callback.message.answer(
        f"Активні уроки модуля №{module_number}:",
        reply_markup=await admin_kb.manage_course_menu(module_number, lessons)
    )
    await callback.answer()


async def add_module_lesson(callback: CallbackQuery, state: FSMContext) -> None:
    module_number = int(callback.data.split("_")[-1])

    lessons = await get_lessons_by_module(module_number)
    lesson_number = _find_next_available_lesson_number(lessons)

    await state.update_data(module_number=module_number, lesson_number=lesson_number)
    await callback.message.answer(
        "Введіть заголовок урока:\n"
        "Для скасування дії введіть «-»."
    )
    await callback.answer()


async def add_module_lesson_title(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    module_number = data.get("module_number")

    if message.text == "-":
        await state.clear()
        await message.answer("❌ Дія скасована.",
                             reply_markup=await admin_kb.go_back(f"admin:manage_course_{module_number}"))
        return

    await state.update_data(title=message.text)
    await message.answer("Надішліть відео для курсу (якщо хочете залишити поле порожнім, надішліть «-»).")


async def add_module_lesson_video(message: Message, state: FSMContext) -> None:
    await state.update_data(video=message.video.file_id)
    await message.answer("Надішліть PDF для курсу (якщо хочете залишити поле порожнім, надішліть «-»).")


async def add_module_lesson_video_document(message: Message, state: FSMContext) -> None:
    try:
        doc = getattr(message, "document", None)
        mime = getattr(doc, "mime_type", None) if doc else None

        if not doc or not mime or not mime.startswith("video/"):
            await message.answer(
                "❌ Це не відеофайл.\n"
                "Надішліть відео як медіа або файлом з типом video/*, або введіть «-» щоб пропустити."
            )
            return

        await state.update_data(video=doc.file_id)
        await message.answer("Надішліть PDF для курсу (якщо хочете залишити поле порожнім, надішліть «-»).")

    except Exception as e:
        print(f"Error in add_module_lesson_video_document: {e}")
        await message.answer(
            "❌ Сталася помилка при обробці відеофайлу. Спробуйте ще раз або введіть «-» щоб пропустити."
        )


async def skip_add_module_lesson_video(message: Message, state: FSMContext) -> None:
    await state.update_data(video=None)
    await message.answer("Надішліть PDF для курсу (якщо хочете залишити поле порожнім, надішліть «-»).")


async def add_module_lesson_pdf(message: Message, state: FSMContext) -> None:
    await _process_create_module_lesson(message, state, message.document.file_id)


async def skip_add_module_lesson_pdf(message: Message, state: FSMContext) -> None:
    await _process_create_module_lesson(message, state, None)


async def manage_module_lesson(callback: CallbackQuery) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)
    lesson = await get_lesson_by_module_and_lesson_number(module_number, lesson_number)

    if not lesson:
        await callback.message.answer(
            f"❌ Урок №{lesson_number} у модулі №{module_number} не знайдено.",
            reply_markup=await admin_kb.go_back(callback.data)
        )
        await callback.answer()
        return

    msg = (
        f"📖 Модуль №{module_number} - Урок №{lesson_number}\n\n"
        f"📝 Назва: {lesson.title}\n"
        f"🎥 Відео: {'✅ Є' if lesson.video_file_id else '❌ Немає'}\n"
        f"📄 PDF: {'✅ Є' if lesson.pdf_file_id else '❌ Немає'}\n"
        f"📅 Створено: {_format_date(lesson.created_at)}\n"
    )

    await callback.message.answer(
        msg,
        reply_markup=await admin_kb.manage_module_lesson_menu(module_number, lesson_number, lesson)
    )
    await callback.answer()


async def show_lesson_video(callback: CallbackQuery) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)
    lesson = await get_lesson_by_module_and_lesson_number(module_number, lesson_number)

    if not lesson:
        await callback.message.answer(
            f"❌ Урок №{lesson_number} у модулі №{module_number} не знайдено.",
            reply_markup=await admin_kb.go_back(callback.data)
        )
        await callback.answer()
        return

    await callback.message.answer_video(
        video=lesson.video_file_id,
        reply_markup=await admin_kb.go_back(callback.data)
    )
    await callback.answer()


async def show_lesson_pdf(callback: CallbackQuery) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)
    lesson = await get_lesson_by_module_and_lesson_number(module_number, lesson_number)

    if not lesson:
        await callback.message.answer(
            f"❌ Урок №{lesson_number} у модулі №{module_number} не знайдено.",
            reply_markup=await admin_kb.go_back(callback.data)
        )
        await callback.answer()
        return

    await callback.message.answer_document(
        document=lesson.pdf_file_id,
        reply_markup=await admin_kb.go_back(callback.data)
    )
    await callback.answer()


async def update_lesson_title(callback: CallbackQuery, state: FSMContext) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)
    await state.update_data(module_number=module_number, lesson_number=lesson_number)
    await callback.message.answer(
        "Введіть заголовок урока:\n"
        "Для скасування дії введіть «-»."
    )
    await callback.answer()


async def update_lesson_title_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    module_number = data.get("module_number")
    lesson_number = data.get("lesson_number")

    if message.text == "-":
        await state.clear()
        await message.answer(
            "❌ Дія скасована.",
            reply_markup=await admin_kb.go_back(f"admin:manage_module_lesson_{module_number}_{lesson_number}")
        )
        return

    await _process_update_module_lesson(
        message, state,
        update_type="title",
        new_value=message.text,
        success_message=f"✅ Заголовок урока успішно змінено на '{message.text}'."
    )


async def update_lesson_video(callback: CallbackQuery, state: FSMContext) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)
    await state.update_data(module_number=module_number, lesson_number=lesson_number)
    await callback.message.answer(
        "Надішліть відео уроку:\n"
        "Для скасування дії введіть «-»."
    )
    await callback.answer()


async def update_lesson_video_content(message: Message, state: FSMContext) -> None:
    await _process_update_module_lesson(
        message, state,
        update_type="video_file_id",
        new_value=message.video.file_id,
        success_message="✅ Відео урока успішно оновлено."
    )


async def cancel_update_lesson_video(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    module_number = data.get("module_number")
    lesson_number = data.get("lesson_number")

    await message.answer(
        "❌ Дія скасована.",
        reply_markup=await admin_kb.go_back(f"admin:manage_module_lesson_{module_number}_{lesson_number}")
    )
    await state.clear()


async def update_lesson_pdf(callback: CallbackQuery, state: FSMContext) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)
    await state.update_data(module_number=module_number, lesson_number=lesson_number)
    await callback.message.answer(
        "Надішліть PDF файл уроку:\n"
        "Для скасування дії введіть «-»."
    )
    await callback.answer()


async def update_lesson_pdf_content(message: Message, state: FSMContext) -> None:
    pdf_name = message.document.file_name if message.document.file_name else "файл"
    success_message = f"✅ PDF урока успішно обновлено ({pdf_name})."
    await _process_update_module_lesson(
        message, state,
        update_type="pdf_file_id",
        new_value=message.document.file_id,
        success_message=success_message
    )


async def cancel_update_lesson_pdf(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    module_number = data.get("module_number")
    lesson_number = data.get("lesson_number")

    await message.answer(
        "❌ Дія скасована.",
        reply_markup=await admin_kb.go_back(f"admin:manage_module_lesson_{module_number}_{lesson_number}")
    )
    await state.clear()


async def ask_delete_module_lesson(callback: CallbackQuery) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)
    await callback.message.answer(
        f"Ви дійсно хочете видалити урок {lesson_number} модуля {module_number}?",
        reply_markup=await admin_kb.delete_module_lesson(module_number, lesson_number)
    )
    await callback.answer()


async def delete_module_lesson(callback: CallbackQuery) -> None:
    module_number, lesson_number = _get_module_lesson_number(callback)

    try:
        lesson = await get_lesson_by_module_and_lesson_number(module_number, lesson_number)
        if not lesson:
            await callback.message.answer(
                f"❌ Урок №{lesson_number} у модулі №{module_number} не знайдено.",
                reply_markup=await admin_kb.go_back(callback.data)
            )
            await callback.answer()
            return

        await delete_lesson(lesson.id)
        deleted = await get_lesson_by_id(lesson.id)

        if not deleted:
            await callback.message.answer(
                f"✅ Урок {lesson_number} модуля {module_number} успішно видалено.",
                reply_markup=await admin_kb.go_back(f"admin:manage_course_{module_number}")
            )
        else:
            await callback.message.answer(
                f"❌ Не вдалося видалити урок {lesson_number} модуля {module_number}. Спробуйте пізніше.",
                reply_markup=await admin_kb.go_back(f"admin:manage_course_{module_number}")
            )

    except Exception as e:
        print(f"Error deleting lesson {lesson_number} in module {module_number}: {str(e)}")
        await callback.message.answer(
            f"❌ Сталася помилка під час видалення урока {lesson_number} модуля {module_number}. Спробуйте пізніше.",
            reply_markup=await admin_kb.go_back(f"admin:manage_course_{module_number}")
        )

    await callback.answer()


# ============================ Helpers (internal) ============================

async def _get_subscriptions_by_tg_id(tg_id: int) -> List[SubscriptionReadSchemaDB]:
    user = await get_user_by_tg_id(tg_id)
    if not user:
        return []
    return await get_subscriptions_by_user_id(user.user_id)


async def _get_all_active_subscriptions() -> List[SubscriptionReadSchemaDB]:
    active: List[SubscriptionReadSchemaDB] = []
    users = await get_all_users()
    for u in users:
        subs = await get_active_subscriptions_by_user_id(u.user_id)
        active.extend(subs)
    return active


async def _open_subscriptions_access(tg_user_id: int) -> List[SubscriptionReadSchemaDB]:
    subs = await _get_subscriptions_by_tg_id(tg_user_id)
    updated: List[SubscriptionReadSchemaDB] = []
    for s in subs:
        if s.status != SubscriptionStatus.ACTIVE:
            up = await update_subscription_status(s.id, SubscriptionStatus.ACTIVE)
            if up:
                updated.append(up)
        else:
            updated.append(s)
    return updated


async def _close_subscriptions_access(tg_user_id: int) -> List[SubscriptionReadSchemaDB]:
    subs = await _get_subscriptions_by_tg_id(tg_user_id)
    updated: List[SubscriptionReadSchemaDB] = []
    for s in subs:
        if s.status != SubscriptionStatus.CANCELED:
            up = await update_subscription_status(s.id, SubscriptionStatus.CANCELED)
            if up:
                updated.append(up)
        else:
            updated.append(s)
    return updated


async def _are_subscriptions_updated(subscriptions: List[SubscriptionReadSchemaDB], action: str, tg_id: int
                                     ) -> Tuple[str, InlineKeyboardMarkup]:
    messages = {
        "open": {
            "success": f"✅ Всі доступи користувача (TG {tg_id}) успішно відкрито.",
            "warn": f"⚠️ Частково відкрито доступи користувача (TG {tg_id}). Деякі доступи не вдалося відкрити.",
            "error": f"❌ Не вдалося відкрити доступи користувача (TG {tg_id})."
        },
        "close": {
            "success": f"✅ Всі доступи користувача (TG {tg_id}) успішно закрито.",
            "warn": f"⚠️ Частково закрито доступи користувача (TG {tg_id}). Деякі доступи не вдалося закрити.",
            "error": f"❌ Не вдалося закрити доступи користувача (TG {tg_id})."
        }
    }

    if not subscriptions:
        return messages[action]["error"], await admin_kb.go_back(f"admin:show_user_subscriptions_{tg_id}")

    expected_status = SubscriptionStatus.ACTIVE if action == "open" else SubscriptionStatus.CANCELED
    success_count = sum(1 for sub in subscriptions if sub.status == expected_status)
    total_count = len(subscriptions)

    if success_count == total_count:
        return messages[action]["success"], await admin_kb.show_user_subscriptions(tg_id, False)
    elif success_count > 0:
        return messages[action]["warn"], await admin_kb.show_user_subscriptions(tg_id, False)
    else:
        return messages[action]["error"], await admin_kb.show_user_subscriptions(tg_id, False)


async def _process_create_module_lesson(message: Message, state: FSMContext, pdf_file_id: Optional[str]) -> None:
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
                reply_markup=await admin_kb.go_back(f"admin:manage_course_{module_number}")
            )
            await state.clear()
            return

        raise RuntimeError("Create lesson verification failed")

    except Exception as e:
        print(f"Error creating lesson for module {module_number}: {str(e)}")
        await message.answer(
            "❌ Сталася помилка під час створення урока. Спробуйте пізніше.",
            reply_markup=await admin_kb.go_back(f"admin:manage_course_{module_number}")
        )
        await state.clear()


async def _process_update_module_lesson(
        message: Message,
        state: FSMContext,
        update_type: str,
        new_value: str,
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
                    reply_markup=await admin_kb.go_back(f"admin:manage_module_lesson_{module_number}_{lesson_number}")
                )
                await state.clear()
                return

        raise RuntimeError("Update verification failed")

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
            reply_markup=await admin_kb.go_back(f"admin:manage_module_lesson_{module_number}_{lesson_number}")
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


def _format_date(date: Optional[datetime]) -> str:
    if date is None:
        return "Не вказано"
    return date.strftime('%d.%m.%Y %H:%M:%S')


def _get_module_lesson_number(callback: CallbackQuery) -> Tuple[int, int]:
    parts = callback.data.split("_")
    return int(parts[-2]), int(parts[-1])
