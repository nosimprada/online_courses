import random
from typing import Dict

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

import keyboards.help as help_kb
from config import ADMIN_CHAT_ID
from keyboards.start import back_to_menu as back_to_menu_kb

router = Router()


class HelpStates(StatesGroup):
    choosing_topic = State()
    writing_message = State()


@router.callback_query(F.data == "help:start")
async def start_help_request(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text("Виберіть тему для звернення", reply_markup=help_kb.choose_support_topic())
    await state.set_state(HelpStates.choosing_topic)
    await callback.answer()


@router.callback_query(F.data.startswith("help:support_topic_"), StateFilter(HelpStates.choosing_topic))
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
        f"Выбрана тема {topic_name}.\n"
        "Опишіть вашу проблему якомога детальніше.\n\n"
        "📷 Ви також можете прикріпити фото до повідомлення.\n"
        "Для скасування дії введіть «-»."
    )
    await state.set_state(HelpStates.writing_message)

    await callback.answer()


@router.callback_query(F.data == "help:cancel", StateFilter(HelpStates.choosing_topic))
async def cancel_help_request(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("❌ Запит до технічної підтримки скасовано.", reply_markup=back_to_menu_kb())
    await callback.answer()


@router.message(F.text, StateFilter(HelpStates.writing_message))
async def write_help_message_text(message: Message, state: FSMContext) -> None:
    if message.text == "-":
        await state.clear()
        await message.answer("❌ Запит до технічної підтримки скасовано.", reply_markup=back_to_menu_kb())
        return

    await _process_help_message(message, state, message_text=message.text)


@router.message(F.photo, StateFilter(HelpStates.writing_message))
async def write_help_message_photo(message: Message, state: FSMContext) -> None:
    caption = message.caption if message.caption else "Без опису"

    await _process_help_message(message, state, message_text=caption, photo=message.photo[-1].file_id)


async def _process_help_message(message: Message, state: FSMContext, message_text: str, photo=None) -> None:
    data = await state.get_data()

    selected_topic = data.get('selected_topic_name')
    if not selected_topic:
        await state.set_state(HelpStates.choosing_topic)
        await message.answer("Виберіть тему для звернення", reply_markup=help_kb.choose_support_topic())
        return

    user = message.from_user
    username = f"@{user.username}" if user.username else "Без Username"
    support_number = random.randint(5000, 8000000)

    support_message = (
        f"🆘 <b>Нове звернення #{support_number} вiд {username}</b>\n\n"
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
                reply_markup=help_kb.choose_message_action_for_helpers(user.username)
            )
        else:
            await message.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=support_message,
                reply_markup=help_kb.choose_message_action_for_helpers(user.username)
            )

        await message.answer(
            f"Звернення №{support_number} отримано. Відповімо протягом 24 годин (10:00–18:00 за Києвом)",
            reply_markup=back_to_menu_kb()
        )

    except Exception as e:
        print(f"Error sending message to support group: {e}")
        await message.answer(
            "❌ Виникла помилка при відправці звернення. Спробуйте пізніше.",
            reply_markup=back_to_menu_kb()
        )

    await state.clear()
