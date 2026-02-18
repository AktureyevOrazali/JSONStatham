"""Subscription handler — /subscribe, plan selection, payment."""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.keyboards.main_menu import get_back_to_menu
from app.keyboards.subscription import get_plans_keyboard, get_confirm_payment_keyboard
from app.services.api_client import api_client

router = Router()

PLAN_DETAILS = {
    "starter": {
        "name": "Starter",
        "emoji": "🟢",
        "price": "990 ₽/мес",
        "features": [
            "1 сервер",
            "1 Telegram-бот",
            "Базовая поддержка",
            "1 GB RAM VPS",
        ],
    },
    "pro": {
        "name": "Pro",
        "emoji": "🔵",
        "price": "1 990 ₽/мес",
        "features": [
            "1 сервер",
            "До 3 каналов (Telegram, WhatsApp и др.)",
            "Приоритетная поддержка",
            "2 GB RAM VPS",
            "Расширенная аналитика",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "emoji": "🟣",
        "price": "4 990 ₽/мес",
        "features": [
            "До 3 серверов",
            "Неограниченные каналы",
            "Выделенная поддержка 24/7",
            "4 GB RAM VPS",
            "Custom домен",
            "SLA 99.9%",
        ],
    },
}


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message):
    """Handle /subscribe — show available plans."""
    await message.answer(
        "📋 <b>Выберите тарифный план:</b>\n\n"
        "Каждый план включает персональный VPS с OpenClaw.",
        parse_mode="HTML",
        reply_markup=get_plans_keyboard(),
    )


@router.callback_query(F.data == "menu:plans")
async def callback_plans(callback: CallbackQuery):
    """Show plans via menu button."""
    await callback.message.edit_text(
        "📋 <b>Выберите тарифный план:</b>\n\n"
        "Каждый план включает персональный VPS с OpenClaw.",
        parse_mode="HTML",
        reply_markup=get_plans_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("plan:"))
async def callback_select_plan(callback: CallbackQuery):
    """User selected a plan — show details and confirm."""
    plan_slug = callback.data.split(":")[1]
    plan = PLAN_DETAILS.get(plan_slug)

    if not plan:
        await callback.answer("Неизвестный тариф", show_alert=True)
        return

    features_text = "\n".join(f"  ✅ {f}" for f in plan["features"])
    text = (
        f"{plan['emoji']} <b>{plan['name']}</b>\n"
        f"💰 Стоимость: <b>{plan['price']}</b>\n\n"
        f"<b>Включено:</b>\n{features_text}\n\n"
        f"Подтвердите оплату:"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_confirm_payment_keyboard(plan_slug),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:"))
async def callback_pay(callback: CallbackQuery):
    """User confirmed payment — create subscription via API."""
    plan_slug = callback.data.split(":")[1]

    try:
        sub = await api_client.create_subscription(callback.from_user.id, plan_slug)
        plan = PLAN_DETAILS.get(plan_slug, {})

        text = (
            f"✅ <b>Подписка создана!</b>\n\n"
            f"📋 План: <b>{plan.get('name', plan_slug)}</b>\n"
            f"📊 Статус: <b>ожидает оплаты</b>\n"
            f"🆔 ID подписки: <code>{sub.get('id', 'N/A')}</code>\n\n"
            f"💳 Ссылка на оплату будет отправлена отдельно.\n"
            f"<i>(MVP: интеграция с ЮKassa в разработке)</i>"
        )

        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при создании подписки:\n<code>{e}</code>",
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )
    await callback.answer()

