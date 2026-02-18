"""Server handler — /status, /restart, /logs."""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.keyboards.main_menu import get_back_to_menu
from app.services.api_client import api_client

router = Router()


@router.message(Command("status"))
async def cmd_status(message: Message):
    """Handle /status — show server status."""
    await _show_server_status(message, message.from_user.id)


@router.callback_query(F.data == "menu:status")
async def callback_status(callback: CallbackQuery):
    """Show server status via menu button."""
    await _show_server_status_edit(callback)
    await callback.answer()


async def _show_server_status(message: Message, telegram_id: int):
    """Show server status as a new message."""
    try:
        server = await api_client.get_server(telegram_id)
        if not server:
            await message.answer(
                "❌ <b>Сервер не найден</b>\n\n"
                "Возможно, ваша подписка ещё не активирована.\n"
                "Используйте /subscribe для оформления подписки.",
                parse_mode="HTML",
                reply_markup=get_back_to_menu(),
            )
            return

        status_data = await api_client.get_server_status(telegram_id)
        text = _format_status(server, status_data)
        await message.answer(text, parse_mode="HTML", reply_markup=get_back_to_menu())

    except Exception as e:
        await message.answer(
            f"❌ Ошибка при получении статуса:\n<code>{e}</code>",
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )


async def _show_server_status_edit(callback: CallbackQuery):
    """Show server status by editing existing message."""
    try:
        server = await api_client.get_server(callback.from_user.id)
        if not server:
            await callback.message.edit_text(
                "❌ <b>Сервер не найден</b>\n\n"
                "Возможно, ваша подписка ещё не активирована.\n"
                "Используйте /subscribe для оформления подписки.",
                parse_mode="HTML",
                reply_markup=get_back_to_menu(),
            )
            return

        status_data = await api_client.get_server_status(callback.from_user.id)
        text = _format_status(server, status_data)
        await callback.message.edit_text(
            text, parse_mode="HTML", reply_markup=get_back_to_menu()
        )

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при получении статуса:\n<code>{e}</code>",
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )


def _format_status(server: dict, status_data: dict | None) -> str:
    """Format server status into a nice text message."""
    status_emoji = "🟢" if server.get("status") == "active" else "🔴"
    online = "Online" if status_data and status_data.get("is_online") else "Offline"

    text = (
        f"📊 <b>Статус сервера</b>\n\n"
        f"{status_emoji} Статус: <b>{online}</b>\n"
        f"🏷 Имя: {server.get('name', 'N/A')}\n"
        f"🌐 IP: <code>{server.get('ip_address', 'N/A')}</code>\n"
        f"📦 Версия OpenClaw: {server.get('openclaw_version', 'N/A')}\n"
    )

    if status_data:
        if status_data.get("uptime"):
            text += f"⏱ Uptime: {status_data['uptime']}\n"
        if status_data.get("cpu_percent") is not None:
            text += f"💻 CPU: {status_data['cpu_percent']}%\n"
        if status_data.get("ram_used_mb") is not None:
            text += (
                f"🧠 RAM: {status_data['ram_used_mb']:.0f} / "
                f"{status_data.get('ram_total_mb', 0):.0f} MB\n"
            )

    return text


# ── Restart ──

@router.message(Command("restart"))
async def cmd_restart(message: Message):
    """Handle /restart — restart OpenClaw."""
    try:
        result = await api_client.restart_server(message.from_user.id)
        emoji = "✅" if result.get("success") else "❌"
        await message.answer(
            f"{emoji} {result.get('message', 'Неизвестный результат')}",
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )
    except Exception as e:
        await message.answer(
            f"❌ Ошибка: <code>{e}</code>",
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )


@router.callback_query(F.data == "menu:restart")
async def callback_restart(callback: CallbackQuery):
    """Restart via menu."""
    try:
        result = await api_client.restart_server(callback.from_user.id)
        emoji = "✅" if result.get("success") else "❌"
        await callback.message.edit_text(
            f"{emoji} {result.get('message', 'Неизвестный результат')}",
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка: <code>{e}</code>",
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )
    await callback.answer()


# ── Logs ──

@router.message(Command("logs"))
async def cmd_logs(message: Message):
    """Handle /logs — show last OpenClaw logs."""
    try:
        data = await api_client.get_server_logs(message.from_user.id, lines=30)
        logs_text = data.get("logs", "Нет данных")
        await message.answer(
            f"📜 <b>Последние логи OpenClaw</b>\n\n"
            f"<pre>{logs_text[:3500]}</pre>",
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )
    except Exception as e:
        await message.answer(
            f"❌ Ошибка: <code>{e}</code>",
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )


@router.callback_query(F.data == "menu:logs")
async def callback_logs(callback: CallbackQuery):
    """Show logs via menu."""
    try:
        data = await api_client.get_server_logs(callback.from_user.id, lines=30)
        logs_text = data.get("logs", "Нет данных")
        await callback.message.edit_text(
            f"📜 <b>Последние логи OpenClaw</b>\n\n"
            f"<pre>{logs_text[:3500]}</pre>",
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка: <code>{e}</code>",
            parse_mode="HTML",
            reply_markup=get_back_to_menu(),
        )
    await callback.answer()

