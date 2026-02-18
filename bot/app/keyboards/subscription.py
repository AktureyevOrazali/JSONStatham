"""Subscription plan selection keyboard."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_plans_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with subscription plan options."""
    buttons = [
        [
            InlineKeyboardButton(
                text="🟢 Starter — 990 ₽/мес",
                callback_data="plan:starter",
            )
        ],
        [
            InlineKeyboardButton(
                text="🔵 Pro — 1 990 ₽/мес",
                callback_data="plan:pro",
            )
        ],
        [
            InlineKeyboardButton(
                text="🟣 Enterprise — 4 990 ₽/мес",
                callback_data="plan:enterprise",
            )
        ],
        [
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data="menu:main",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_payment_keyboard(plan: str) -> InlineKeyboardMarkup:
    """Confirmation keyboard before creating a payment."""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Оплатить",
                callback_data=f"pay:{plan}",
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="menu:plans",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
