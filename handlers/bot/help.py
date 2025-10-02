from typing import Dict, Tuple

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

import keyboards.help as help_kb
from config import ADMIN_CHAT_ID
from keyboards.start import back_to_menu as back_to_menu_kb
from utils.schemas.ticket import TicketCreateSchemaDB
from utils.services.ticket import get_ticket_by_user_id, create_ticket

router = Router()


class HelpStates(StatesGroup):
    topic = State()
    message = State()


class ConversationStates(StatesGroup):
    wait_admin = State()
    wait_user = State()


@router.callback_query(F.data == "help:start")
async def start_help_request(callback: CallbackQuery, state: FSMContext) -> None:
    active_ticket = await get_ticket_by_user_id(callback.from_user.id)

    if active_ticket:
        await callback.message.answer(
            f"У вас уже есть активное обращение #{active_ticket.id}."
            "Пожалуйста, дождитесь ответа поддержки или закройте текущее обращение.",
            reply_markup=back_to_menu_kb()
        )
        await callback.answer()
        return

    await callback.message.edit_text("Виберіть тему для звернення", reply_markup=help_kb.choose_support_topic())
    await state.set_state(HelpStates.topic)
    await callback.answer()


@router.callback_query(F.data.startswith("help:support_topic_"), StateFilter(HelpStates.topic))
async def choose_support_topic(callback: CallbackQuery, state: FSMContext) -> None:
    topics_names_: Dict[str, str] = {
        "help:support_topic_1": "Тема повідомлення №1",
        "help:support_topic_2": "Тема повідомлення №2",
        "help:support_topic_3": "Тема повідомлення №3"
    }

    topic_id = callback.data.split("_")[-1]
    topic_name = topics_names_[callback.data]
    await state.update_data(selected_topic_id=topic_id, selected_topic_name=topic_name)

    await callback.message.edit_text(
        f"✅ Выбрана тема {topic_name}.\n"
        "📝 Опишіть вашу проблему якомога детальніше.\n\n"
        "📷 Ви також можете прикріпити фото до повідомлення.\n"
        "❌ Для скасування дії введіть «-»."
    )
    await state.set_state(HelpStates.message)

    await callback.answer()


@router.callback_query(F.data == "help:cancel", StateFilter(HelpStates.topic))
async def cancel_help_request(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("❌ Запит до технічної підтримки скасовано.", reply_markup=back_to_menu_kb())
    await callback.answer()


@router.message(F.text, StateFilter(HelpStates.message))
async def write_help_message_text(message: Message, state: FSMContext) -> None:
    if message.text == "-":
        await state.clear()
        await message.answer("❌ Запит до технічної підтримки скасовано.", reply_markup=back_to_menu_kb())
        return

    await _process_help_message(message, state, message_text=message.text)


@router.message(F.photo, StateFilter(HelpStates.message))
async def write_help_message_photo(message: Message, state: FSMContext) -> None:
    caption = message.caption if message.caption else "Без опису"

    await _process_help_message(message, state, message_text=caption, photo=message.photo[-1].file_id)


@router.callback_query(F.data.startswith("help:admin_respond_"))
async def admin_respond_to_ticket(callback: CallbackQuery, state: FSMContext) -> None:
    user_id, ticket_id = _get_last_ntl_data(callback)

    await state.update_data(user_id=user_id, ticket_id=ticket_id)

    await callback.message.edit_text(
        f"💬 Ви відповідаєте на звернення #{ticket_id} користувачеві {user_id}.\n\n"
        "📝 Введіть вашу відповідь:"
    )

    await state.set_state(ConversationStates.wait_admin)
    await callback.answer()


@router.callback_query(F.text, StateFilter(ConversationStates.wait_admin))
async def admin_send_response(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    user_id = data.get("user_id")
    ticket_id = data.get("ticket_id")

    return


async def _process_help_message(message: Message, state: FSMContext, message_text: str, photo=None) -> None:
    data = await state.get_data()
    selected_topic = data.get("selected_topic_name")

    user = message.from_user
    username = f"@{user.username}" if user.username else "Без Username"

    ticket = await create_ticket(TicketCreateSchemaDB(
        user_id=user.id,
        topic=selected_topic,
        text=message_text,
        attachments=photo
    ))

    support_message = (
        f"🆘 <b>Нове звернення #{ticket.id} вiд {username}</b>\n\n"
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
                caption=support_message
                # TODO: reply_markup=help_kb.choose_ticket_action(...)
            )
        else:
            await message.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=support_message,
                # TODO: reply_markup=help_kb.choose_ticket_action(...)
            )

        await message.answer(
            f"✅ Звернення №{ticket.id} отримано. Відповімо протягом 24 годин (10:00–18:00 за Києвом)",
            reply_markup=back_to_menu_kb()
        )

    except Exception as e:
        print(f"Error sending help ticket message to admin: {e}")
        await message.answer(
            "❌ Виникла помилка при відправці звернення. Спробуйте пізніше.",
            reply_markup=back_to_menu_kb()
        )

    await state.clear()


def _get_last_ntl_data(callback: CallbackQuery) -> Tuple[int, int]:
    parts = callback.data.split("_")
    return parts[-1], parts[-2]
