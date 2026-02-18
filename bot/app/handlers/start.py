"""Start handler — /start command and main menu navigation."""

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from bot.app.keyboards.main_menu import get_main_menu
from bot.app.services.api_client import api_client

router = Router()

WELCOME_TEXT = """
🦀 <b>Добро пожаловать в OpenClaw!</b>

OpenClaw — это платформа для управления AI-ботами.
Мы разворачиваем для вас персональный сервер и берём на себя всю техническую часть.

<b>Что вы получаете:</b>
• Персональный сервер с OpenClaw
• Управление через Telegram и личный кабинет
• Настройка AI-моделей, каналов и интеграций
• Техническая поддержка 24/7

Выберите действие из меню ниже 👇
"""

MENU_TEXT = """
🏠 <b>Главное меню</b>

Выберите действие:
"""


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command — welcome message + main menu."""
    await message.answer(
        WELCOME_TEXT,
        parse_mode="HTML",
        reply_markup=get_main_menu(),
    )


@router.callback_query(F.data == "menu:main")
async def callback_main_menu(callback: CallbackQuery):
    """Return to main menu."""
    await callback.message.edit_text(
        MENU_TEXT,
        parse_mode="HTML",
        reply_markup=get_main_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:profile")
async def callback_profile(callback: CallbackQuery):
    """Show user profile info."""
    try:
        user_data = await api_client.get_me(callback.from_user.id)
        sub = await api_client.get_current_subscription(callback.from_user.id)

        sub_text = "Нет активной подписки"
        if sub:
            sub_text = f"План: <b>{sub['plan']}</b> | Статус: <b>{sub['status']}</b>"
            if sub.get("expires_at"):
                sub_text += f"\nДействует до: {sub['expires_at'][:10]}"

        profile_text = f"""
👤 <b>Ваш профиль</b>

🆔 Telegram ID: <code>{user_data.get('telegram_id', 'N/A')}</code>
📛 Имя: {user_data.get('first_name', '')} {user_data.get('last_name', '')}
👤 Username: @{user_data.get('username', 'N/A')}
📧 Email: {user_data.get('email', 'Не указан')}
🎭 Роль: {user_data.get('role', 'client')}

📋 <b>Подписка:</b>
{sub_text}
"""
        from bot.app.keyboards.main_menu import get_back_to_menu
        await callback.message.edit_text(
            profile_text,
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )
    except Exception as e:
        from bot.app.keyboards.main_menu import get_back_to_menu
        await callback.message.edit_text(
            f"❌ Ошибка при получении профиля:\n<code>{e}</code>",
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )
    await callback.answer()
