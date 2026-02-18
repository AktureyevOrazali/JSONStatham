"""Auth middleware — auto-registers user on first contact with the bot."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from app.services.api_client import api_client


class AuthMiddleware(BaseMiddleware):
    """
    Middleware that ensures the user is registered in the backend
    before any handler processes the update.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Extract user from the event
        user = None
        if isinstance(event, Message) and event.from_user:
            user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            user = event.from_user

        if user:
            try:
                # Authenticate / register the user in the backend
                await api_client.authenticate(
                    telegram_id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                )
            except Exception as e:
                # If backend is unavailable, still let the handler run
                # but log the error
                import logging
                logging.getLogger(__name__).warning(
                    f"Backend auth failed for user {user.id}: {e}"
                )

        return await handler(event, data)

