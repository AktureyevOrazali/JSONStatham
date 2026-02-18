"""Telegram Bot entry point — dispatcher, routers, polling."""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.app.config import bot_settings
from bot.app.handlers import start, subscription, server, support
from bot.app.middlewares.auth import AuthMiddleware


async def main():
    """Initialize and start the bot."""
    # ── Logging ──
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
    logger = logging.getLogger(__name__)

    if not bot_settings.bot_token:
        logger.error("BOT_TOKEN не задан! Проверьте .env файл.")
        sys.exit(1)

    # ── Bot & Dispatcher ──
    bot = Bot(
        token=bot_settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = MemoryStorage()  # TODO: RedisStorage для продакшена
    dp = Dispatcher(storage=storage)

    # ── Middleware ──
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # ── Routers ──
    dp.include_router(start.router)
    dp.include_router(subscription.router)
    dp.include_router(server.router)
    dp.include_router(support.router)

    # ── Start polling ──
    logger.info("🤖 OpenClaw Bot запущен!")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
