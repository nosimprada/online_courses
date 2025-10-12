from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from config import ADMIN_CHAT_ID
from utils.services.subscription import get_active_subscriptions_by_user_id


class IsSubscribedMiddleware(BaseMiddleware):
    """
    Middleware для проверки подписки пользователя.
    Проверяет есть ли у пользователя активная подписка.
    """

    async def __call__(
            self,
            handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        user_tg_id: int = event.from_user.id

        if user_tg_id == ADMIN_CHAT_ID:
            return await handler(event, data)

        subscriptions = await get_active_subscriptions_by_user_id(user_tg_id)

        if not subscriptions:
            message_text = "❌ У вас немає активного доступу."

            if isinstance(event, Message):
                await event.answer(message_text)
            elif isinstance(event, CallbackQuery):
                await event.message.answer(message_text)
            return None

        return await handler(event, data)


class IsAdminMiddleware(BaseMiddleware):
    """
    Middleware для проверки пользователя на наличие прав администратора.
    """

    async def __call__(
            self,
            handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        user_tg_id: int = event.from_user.id

        if user_tg_id == ADMIN_CHAT_ID:
            return await handler(event, data)

        return None
