"""Main menu keyboard."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu() -> InlineKeyboardMarkup:
    """Main menu inline keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text="📋 Тарифы", callback_data="menu:plans"),
            InlineKeyboardButton(text="📊 Статус сервера", callback_data="menu:status"),
        ],
        [
            InlineKeyboardButton(text="🔄 Перезапуск", callback_data="menu:restart"),
            InlineKeyboardButton(text="📜 Логи", callback_data="menu:logs"),
        ],
        [
            InlineKeyboardButton(text="👤 Профиль", callback_data="menu:profile"),
            InlineKeyboardButton(text="💬 Поддержка", callback_data="menu:support"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_to_menu() -> InlineKeyboardMarkup:
    """Single button to return to main menu."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Главное меню", callback_data="menu:main")]
        ]
    )
