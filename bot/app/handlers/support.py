"""Support handler — /support, ticket creation via FSM."""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.keyboards.main_menu import get_back_to_menu
from app.states.onboarding import SupportStates

router = Router()


@router.message(Command("support"))
async def cmd_support(message: Message, state: FSMContext):
    """Handle /support — start ticket creation."""
    await state.set_state(SupportStates.waiting_for_subject)
    await message.answer(
        "💬 <b>Создание тикета в поддержку</b>\n\n"
        "Введите тему обращения:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="support:cancel")]
            ]
        ),
    )


@router.callback_query(F.data == "menu:support")
async def callback_support(callback: CallbackQuery, state: FSMContext):
    """Support via menu."""
    await state.set_state(SupportStates.waiting_for_subject)
    await callback.message.edit_text(
        "💬 <b>Создание тикета в поддержку</b>\n\n"
        "Введите тему обращения:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="support:cancel")]
            ]
        ),
    )
    await callback.answer()


@router.message(SupportStates.waiting_for_subject)
async def process_subject(message: Message, state: FSMContext):
    """Process ticket subject."""
    await state.update_data(subject=message.text)
    await state.set_state(SupportStates.waiting_for_description)
    await message.answer(
        f"📝 Тема: <b>{message.text}</b>\n\n"
        "Теперь опишите вашу проблему подробнее:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="support:cancel")]
            ]
        ),
    )


@router.message(SupportStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    """Process ticket description and show confirmation."""
    data = await state.get_data()
    await state.update_data(description=message.text)
    await state.set_state(SupportStates.confirming_ticket)

    await message.answer(
        f"📋 <b>Подтвердите тикет:</b>\n\n"
        f"📝 Тема: <b>{data['subject']}</b>\n"
        f"📄 Описание: {message.text}\n\n"
        f"Отправить тикет?",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Отправить", callback_data="support:submit"),
                    InlineKeyboardButton(text="❌ Отмена", callback_data="support:cancel"),
                ]
            ]
        ),
    )


@router.callback_query(F.data == "support:submit", SupportStates.confirming_ticket)
async def callback_submit_ticket(callback: CallbackQuery, state: FSMContext):
    """Submit the support ticket."""
    data = await state.get_data()
    await state.clear()

    # TODO: Отправить тикет в backend API
    # ticket = await api_client.create_ticket(...)

    await callback.message.edit_text(
        "✅ <b>Тикет создан!</b>\n\n"
        f"📝 Тема: {data.get('subject', 'N/A')}\n"
        f"📄 Описание: {data.get('description', 'N/A')}\n\n"
        "Наша команда свяжется с вами в ближайшее время.\n"
        "<i>(MVP: тикеты пересылаются в админский бот)</i>",
        parse_mode="HTML",
        reply_markup=get_back_to_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "support:cancel")
async def callback_cancel_support(callback: CallbackQuery, state: FSMContext):
    """Cancel ticket creation."""
    await state.clear()
    await callback.message.edit_text(
        "❌ Создание тикета отменено.",
        parse_mode="HTML",
        reply_markup=get_back_to_menu(),
    )
    await callback.answer()

