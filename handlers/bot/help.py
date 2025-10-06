from typing import Tuple

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

import keyboards.help as help_kb
from config import ADMIN_CHAT_ID
from utils.enums.ticket import TicketStatus
from utils.schemas.ticket import TicketCreateSchemaDB
from utils.services.ticket import get_ticket_by_user_id, create_ticket, close_ticket, open_ticket

router = Router()


class HelpStates(StatesGroup):
    topic = State()
    message = State()
    admin_responding = State()


@router.message(F.text == "Help ❓", StateFilter(None))
async def start_help_request(message: Message, state: FSMContext) -> None:
    active_ticket = await get_ticket_by_user_id(message.from_user.id)

    if active_ticket and active_ticket.status != TicketStatus.CLOSED:
        await message.answer(
            f"❌ У вас вже є активне звернення №{active_ticket.id}. "
            "Будь ласка, дочекайтеся відповіді служби підтримки.",
            reply_markup=await help_kb.back_to_menu()
        )
        return

    await message.answer("💬 Напишіть тему для звернення:", reply_markup=await help_kb.cancel())
    await state.set_state(HelpStates.topic)


@router.message(F.text == "❌ Скасувати звернення", StateFilter(HelpStates.topic, HelpStates.message))
async def cancel_help_request(message: Message, state: FSMContext) -> None:
    await message.answer("❌ Запит до технічної підтримки скасовано.", reply_markup=await help_kb.back_to_menu())
    await state.clear()


@router.message(F.text, StateFilter(HelpStates.topic))
async def choose_support_topic(message: Message, state: FSMContext) -> None:
    await state.update_data(selected_topic=message.text)

    await message.answer(
        f"✅ Выбрана тема {message.text}.\n"
        "📝 Опишіть вашу проблему якомога детальніше.\n\n"
        "📷 Ви також можете прикріпити фото до повідомлення.\n"
    )
    await state.set_state(HelpStates.message)


@router.message(F.text, StateFilter(HelpStates.message))
async def write_help_message_text(message: Message, state: FSMContext) -> None:
    await _process_help_message(message, state, message.text)


@router.message(F.photo, StateFilter(HelpStates.message))
async def write_help_message_photo(message: Message, state: FSMContext) -> None:
    caption = message.caption if message.caption else "Без опису"
    await _process_help_message(message, state, message_text=caption, photo=message.photo[-1].file_id)


@router.callback_query(F.data.startswith("help:admin_respond_"))
async def admin_respond_to_ticket(callback: CallbackQuery, state: FSMContext) -> None:
    ticket_id, user_id = _get_ntl_last_data(callback)

    ticket = await get_ticket_by_user_id(user_id)
    if ticket.status == TicketStatus.CLOSED:
        await callback.message.answer(
            "❌ Звернення вже закрито.",
            reply_markup=await help_kb.admin_back_to_tickets()
        )
        await state.clear()
        await callback.answer()
        return

    await state.update_data(ticket_id=ticket_id, user_id=user_id)

    await callback.message.answer(
        f"💬 Ви відповідаєте на звернення №{ticket_id} користувачеві {user_id}.\n"
        "❌ Для скасування відправлення відповіді натисніть кнопку переходу до квитків.\n\n"
        "📝 Введіть вашу відповідь:",
        reply_markup=await help_kb.admin_back_to_tickets()
    )

    await state.set_state(HelpStates.admin_responding)
    await callback.answer()


@router.message(F.text, StateFilter(HelpStates.admin_responding))
async def admin_send_response(message: Message, state: FSMContext) -> None:
    # TODO: не работает отмена
    if message.text == "❓ Тикетi":
        await state.clear()
        return

    data = await state.get_data()

    user_id = data.get("user_id")
    ticket_id = data.get("ticket_id")

    try:
        await message.bot.send_message(
            user_id,
            f"💬 <b>Відповідь від підтримки по зверненню №{ticket_id}:</b>\n\n{message.text}"
        )

        await open_ticket(ticket_id)

        await message.answer(
            f"✅ Відповідь по зверненню №{ticket_id} відправлена користувачу.\n"
            "Тепер ви можете продовжувати спілкування до закриття тикету.",
            reply_markup=await help_kb.admin_back_to_tickets()
        )

    except Exception as e:
        print(f"Error sending message to help ticket user: {e}")
        await message.answer(
            "❌ Не вдалося відправити повідомлення користувачу. Спробуйте пізніше.",
            reply_markup=await help_kb.admin_back_to_tickets()
        )

    await state.clear()


@router.callback_query(F.data.startswith("help:admin_close_"))
async def admin_close_ticket(callback: CallbackQuery) -> None:
    ticket_id, user_id = _get_ntl_last_data(callback)

    try:
        await close_ticket(ticket_id)
        # TODO: удаление тикета

        await callback.bot.send_message(
            user_id,
            f"✅ Ваше звернення №{ticket_id} закрито адміністратором. "
            f"Якщо у вас виникнуть нові питання, звертайтеся знову!",
            reply_markup=await help_kb.back_to_menu(),
        )

        await callback.message.answer(
            f"✅ Звернення №{ticket_id} успішно закрито.",
            reply_markup=await help_kb.admin_back_to_tickets()
        )

    except Exception as e:
        print(f"Error closing ticket #{ticket_id}: {e}")
        await callback.message.answer(
            "❌ Помилка при закритті звернення. Спробуйте пізніше.",
            reply_markup=await help_kb.admin_back_to_tickets()
        )

    await callback.answer()


@router.message(F.text)
async def user_respond_to_ticket(message: Message) -> None:
    try:
        ticket = await get_ticket_by_user_id(message.from_user.id)

        if not ticket or ticket.status == TicketStatus.CLOSED:
            return

        if ticket.status != TicketStatus.OPEN:
            await message.answer(
                "⏳ Ваше звернення ще не розглянуто адміністратором.\n"
                "Будь ласка, дочекайтеся першої відповіді.",
                reply_markup=await help_kb.back_to_menu()
            )
            return

        user = message.from_user
        username = f"@{user.username}" if user.username else "Без Username"

        support_message = (
            f"💬 <b>Нове повідомлення по зверненню №{ticket.id}</b>\n\n"
            f"🆔 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
            f"👤 <b>Username:</b> {username}\n\n"
            f"💬 <b>Повідомлення:</b>\n{message.text}"
        )

        await message.bot.send_message(
            ADMIN_CHAT_ID, support_message,
            reply_markup=await help_kb.admin_choose_ticket_action(message.from_user.id, ticket.id)
        )

        await message.answer("✅ Ваше повідомлення відправлено адміністратору.")

    except Exception as e:
        print(f"Error sending user response to admin: {e}")
        await message.answer("❌ Не вдалося відправити повідомлення адміністратору.")


@router.message(F.photo)
async def user_respond_to_ticket_with_photo(message: Message) -> None:
    try:
        ticket = await get_ticket_by_user_id(message.from_user.id)

        if not ticket or ticket.status == TicketStatus.CLOSED:
            return

        if ticket.status != TicketStatus.OPEN:
            await message.answer(
                "⏳ Ваше звернення ще не розглянуто адміністратором.\n"
                "Будь ласка, дочекайтеся першої відповіді.",
                reply_markup=await help_kb.back_to_menu()
            )
            return

        user = message.from_user
        username = f"@{user.username}" if user.username else "Без Username"

        caption = message.caption if message.caption else "Без опису"

        support_message = (
            f"💬 <b>Нове повідомлення по зверненню №{ticket.id}</b>\n\n"
            f"🆔 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
            f"👤 <b>Username:</b> {username}\n\n"
            f"💬 <b>Повідомлення:</b>\n{caption}"
        )

        await message.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=message.photo[-1].file_id,
            caption=support_message,
            reply_markup=await help_kb.admin_choose_ticket_action(message.from_user.id, ticket.id)
        )

        await message.answer(
            "✅ Ваше повідомлення відправлено адміністратору.",
            reply_markup=await help_kb.back_to_menu()
        )

    except Exception as e:
        print(f"Error sending user response with photo to admin: {e}")
        await message.answer(
            "❌ Не вдалося відправити повідомлення адміністратору.",
            reply_markup=await help_kb.back_to_menu()
        )


async def _process_help_message(message: Message, state: FSMContext, message_text: str, photo=None) -> None:
    data = await state.get_data()
    selected_topic = data.get("selected_topic")

    user = message.from_user
    username = f"@{user.username}" if user.username else "Без Username"

    ticket = await create_ticket(TicketCreateSchemaDB(
        user_id=user.id,
        topic=selected_topic,
        text=message_text,
        attachments=photo
    ))

    support_message = (
        f"🆘 <b>Нове звернення №{ticket.id} вiд {username}</b>\n\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"📋 <b>Тема:</b> {selected_topic}\n\n"
        f"💬 <b>Повідомлення:</b>\n{message_text}"
    )

    if photo:
        support_message += "\n\n📷 <b>Прикріплено фото.</b>"

    try:
        if photo:
            await message.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=photo,
                caption=support_message,
                reply_markup=await help_kb.admin_choose_ticket_action(user.id, ticket.id)
            )
        else:
            await message.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=support_message,
                reply_markup=await help_kb.admin_choose_ticket_action(user.id, ticket.id)
            )

        await message.answer(
            f"✅ Звернення №{ticket.id} отримано.\n"
            "⏳ Дочекайтеся відповіді від адміністратора.\n"
            "Після першої відповіді ви зможете продовжити спілкування.\n\n"
            "🕐 Відповімо протягом 24 годин (10:00–18:00 за Києвом)",
            reply_markup=await help_kb.back_to_menu()
        )

    except Exception as e:
        print(f"Error sending help ticket message to admin: {e}")
        await message.answer(
            "❌ Виникла помилка при відправці звернення. Спробуйте пізніше.",
            reply_markup=await help_kb.back_to_menu()
        )

    await state.clear()


def _get_ntl_last_data(callback: CallbackQuery) -> Tuple[int, int]:
    parts = callback.data.split("_")
    return int(parts[-2]), int(parts[-1])
