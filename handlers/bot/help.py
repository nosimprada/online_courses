from typing import Tuple, List, Optional

from aiogram import Router, F
from aiogram.filters import Filter
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, PhotoSize

import keyboards.help as help_kb
from config import ADMIN_CHAT_ID
from keyboards.start import start_menu_keyboard
from outboxes.admin import tickets_menu as admin_tickets_menu
from utils.enums.ticket import TicketStatus
from utils.schemas.ticket import TicketCreateSchemaDB, TicketReadSchemaDB
from utils.services.ticket import get_tickets_by_user_id, create_ticket, close_ticket, open_ticket, get_ticket_by_id

router = Router()


class HelpStates(StatesGroup):
    topic = State()
    message = State()
    admin_responding = State()


class HasOpenTicket(Filter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        tickets = await get_tickets_by_user_id(message.from_user.id)
        ticket = await _find_open_ticket(tickets)

        if ticket:
            await state.update_data(open_ticket_id=ticket.id)
            return True

        return False


@router.message(F.text == "Help ❓")
async def start_help_request(message: Message, state: FSMContext) -> None:
    tickets = await get_tickets_by_user_id(message.from_user.id)

    for ticket in tickets:
        if ticket.status != TicketStatus.CLOSED:
            await message.answer(
                f"❌ У вас вже є активне звернення №{ticket.id}. "
                "Будь ласка, дочекайтеся відповіді служби підтримки."
            )
            return

    await message.answer("💬 Напишіть тему для звернення:", reply_markup=await help_kb.cancel())
    await state.set_state(HelpStates.topic)


@router.message(F.text == "❌ Скасувати звернення", StateFilter(HelpStates.topic, HelpStates.message))
async def cancel_help_request(message: Message, state: FSMContext) -> None:
    await message.answer(
        "❌ Запит до технічної підтримки скасовано.",
        reply_markup=await start_menu_keyboard(message.from_user.id == ADMIN_CHAT_ID)
    )
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
    await _process_help_message(message, state, message_text=caption, photos=_get_unique_photos(message.photo))


@router.callback_query(F.data.startswith("help:admin_respond_"))
async def admin_respond_to_ticket(callback: CallbackQuery, state: FSMContext) -> None:
    ticket_id, user_id = _get_ntl_last_data(callback)
    ticket = await get_ticket_by_id(ticket_id)

    if ticket.status == TicketStatus.CLOSED:
        await callback.message.answer(
            "❌ Звернення вже закрито.",
            reply_markup=await help_kb.admin_back_to_tickets()
        )
        await callback.answer()
        return

    await state.update_data(ticket_id=ticket.id, user_id=user_id)

    await callback.message.answer(
        f"💬 Ви відповідаєте на звернення №{ticket_id} користувачеві {user_id}.\n"
        "❌ Для скасування відправлення відповіді натисніть кнопку переходу до тiкетив.\n\n"
        "📝 Введіть вашу відповідь:",
        reply_markup=await help_kb.admin_back_to_tickets()
    )

    await state.set_state(HelpStates.admin_responding)
    await callback.answer()


@router.message(F.text, StateFilter(HelpStates.admin_responding))
async def admin_send_response(message: Message, state: FSMContext) -> None:
    if message.text == "❓ Тiкети":
        await state.clear()
        await admin_tickets_menu(message, False)
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
            "Тепер ви можете продовжувати спілкування до закриття тiкету.",
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

        await callback.bot.send_message(
            user_id,
            f"✅ Ваше звернення №{ticket_id} закрито адміністратором. "
            f"Якщо у вас виникнуть нові питання, звертайтеся знову!",
            reply_markup=await start_menu_keyboard()
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


@router.message(HasOpenTicket(), F.text)
async def user_respond_to_ticket(message: Message, state: FSMContext) -> None:
    try:
        data = await state.get_data()
        ticket_id = data.get("open_ticket_id")

        ticket = await get_ticket_by_id(ticket_id)

        user = message.from_user
        username = f"@{user.username}" if user.username else "Без Username"

        support_message = (
            f"💬 <b>Нове повідомлення по зверненню №{ticket.id}</b>\n\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"👤 <b>Username:</b> {username}\n\n"
            f"💬 <b>Повідомлення:</b>\n{message.text}"
        )

        await message.bot.send_message(
            ADMIN_CHAT_ID, support_message,
            reply_markup=await help_kb.admin_choose_ticket_action(user.id, ticket.id)
        )

        await message.answer("✅ Ваше повідомлення відправлено адміністратору.")

    except Exception as e:
        print(f"Error sending user response to admin: {e}")
        await message.answer("❌ Не вдалося відправити повідомлення адміністратору.")


@router.message(HasOpenTicket(), F.photo)
async def user_respond_to_ticket_with_photo(message: Message, state: FSMContext) -> None:
    try:
        data = await state.get_data()
        ticket_id = data.get("open_ticket_id")

        ticket = await get_ticket_by_id(ticket_id)

        user = message.from_user
        username = f"@{user.username}" if user.username else "Без Username"

        caption = message.caption if message.caption else "Без опису"

        support_message = (
            f"💬 <b>Нове повідомлення по зверненню №{ticket.id}</b>\n\n"
            f"🆔 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
            f"👤 <b>Username:</b> {username}\n\n"
            f"💬 <b>Повідомлення:</b>\n{caption}"
        )

        unique_photos = _get_unique_photos(message.photo)

        if len(unique_photos) == 1:
            await message.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=unique_photos[0].file_id,
                caption=support_message,
                reply_markup=await help_kb.admin_choose_ticket_action(message.from_user.id, ticket.id)
            )

        else:
            media_group: List[InputMediaPhoto] = []

            for idx, photo in enumerate(unique_photos):
                if idx == 0:
                    media_group.append(InputMediaPhoto(
                        media=photo.file_id,
                        caption=support_message
                    ))
                else:
                    media_group.append(InputMediaPhoto(media=photo.file_id))

            await message.bot.send_media_group(
                chat_id=ADMIN_CHAT_ID,
                media=media_group
            )

            await message.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text="🔧 Оберіть дію:",
                reply_markup=await help_kb.admin_choose_ticket_action(message.from_user.id, ticket.id)
            )

        await message.answer("✅ Ваше повідомлення відправлено адміністратору.")

    except Exception as e:
        print(f"Error sending user response with photo to admin: {e}")
        await message.answer("❌ Не вдалося відправити повідомлення адміністратору.")


async def _find_open_ticket(tickets: List[TicketReadSchemaDB]) -> Optional[TicketReadSchemaDB]:
    return next((t for t in tickets if t.status == TicketStatus.OPEN), None)


async def _process_help_message(message: Message, state: FSMContext, message_text: str, photos=None) -> None:
    data = await state.get_data()
    selected_topic = data.get("selected_topic", "Без теми")

    user = message.from_user
    username = f"@{user.username}" if user.username else "Без Username"

    if not message_text.strip():
        message_text = "Без опису"

    unique_photos = _get_unique_photos(photos)

    attachment_files = [photo.file_id for photo in unique_photos] if unique_photos else []
    attachments = ",".join(attachment_files) if attachment_files else None

    ticket = await create_ticket(TicketCreateSchemaDB(
        user_id=user.id,
        topic=selected_topic,
        text=message_text,
        attachments=attachments
    ))

    support_message = (
        f"🆘 <b>Нове звернення №{ticket.id} вiд {username}</b>\n\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"📋 <b>Тема:</b> {selected_topic}\n\n"
        f"💬 <b>Повідомлення:</b>\n{message_text}"
    )

    if unique_photos:
        support_message += f"\n\n📷 <b>Прикріплено фото.</b>"

    try:
        if unique_photos:
            if len(unique_photos) == 1:
                await message.bot.send_photo(
                    chat_id=ADMIN_CHAT_ID,
                    photo=unique_photos[0].file_id,
                    caption=support_message,
                    reply_markup=await help_kb.admin_choose_ticket_action(user.id, ticket.id)
                )
            else:
                media_group: List[InputMediaPhoto] = []

                for idx, photo in enumerate(unique_photos):
                    if idx == 0:
                        media_group.append(InputMediaPhoto(
                            media=photo.file_id, caption=support_message
                        ))
                    else:
                        media_group.append(InputMediaPhoto(
                            media=photo.file_id
                        ))

                await message.bot.send_media_group(
                    chat_id=ADMIN_CHAT_ID,
                    media=media_group
                )

                await message.bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text="🔧 Оберіть дію:",
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
            reply_markup=await start_menu_keyboard()
        )

    except Exception as e:
        print(f"Error sending help ticket message to admin: {e}")
        await message.answer(
            "❌ Виникла помилка при відправці звернення. Спробуйте пізніше.",
            reply_markup=await start_menu_keyboard()
        )

    await state.clear()


def _get_unique_photos(photos: List[PhotoSize]) -> List[PhotoSize]:
    unique_photos: List[PhotoSize] = []

    if photos:
        seen_file_ids = set()

        for photo in photos:
            if photo.file_id not in seen_file_ids:
                seen_file_ids.add(photo.file_id)
                unique_photos.append(photo)

    return unique_photos


def _get_ntl_last_data(callback: CallbackQuery) -> Tuple[int, int]:
    parts = callback.data.split("_")
    return int(parts[-2]), int(parts[-1])
