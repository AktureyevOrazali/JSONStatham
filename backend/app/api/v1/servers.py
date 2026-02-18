"""Servers API routes — server status, restart, logs (MVP stubs)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.server import Server
from app.models.user import User
from app.schemas.server import ServerActionResult, ServerResponse, ServerStatus

router = APIRouter(prefix="/servers", tags=["Servers"])


async def _get_user_server(db: AsyncSession, user_id: int) -> Server:
    """Get the user's server or raise 404."""
    stmt = select(Server).where(Server.user_id == user_id).limit(1)
    result = await db.execute(stmt)
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сервер не найден. Возможно, ваша подписка ещё не активирована.",
        )
    return server


@router.get("/my", response_model=ServerResponse)
async def get_my_server(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Информация о сервере пользователя."""
    server = await _get_user_server(db, current_user.id)
    return server


@router.get("/my/status", response_model=ServerStatus)
async def get_my_server_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Метрики сервера (CPU, RAM, Disk). MVP: заглушка."""
    server = await _get_user_server(db, current_user.id)

    # TODO: SSH-интеграция — реальные метрики через Paramiko
    return ServerStatus(
        is_online=server.status.value == "active",
        uptime="N/A (будет доступно после подключения SSH)",
        cpu_percent=None,
        ram_used_mb=None,
        ram_total_mb=None,
        disk_used_gb=None,
        disk_total_gb=None,
        openclaw_status=server.status.value,
    )


@router.post("/my/restart", response_model=ServerActionResult)
async def restart_my_server(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Перезапустить OpenClaw на сервере. MVP: заглушка."""
    server = await _get_user_server(db, current_user.id)

    # TODO: SSH → systemctl restart openclaw
    return ServerActionResult(
        success=True,
        message="Команда на перезапуск отправлена (MVP: заглушка)",
        action="restart",
    )


@router.post("/my/stop", response_model=ServerActionResult)
async def stop_my_server(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Остановить OpenClaw. MVP: заглушка."""
    server = await _get_user_server(db, current_user.id)

    # TODO: SSH → systemctl stop openclaw
    return ServerActionResult(
        success=True,
        message="Команда на остановку отправлена (MVP: заглушка)",
        action="stop",
    )


@router.get("/my/logs")
async def get_my_server_logs(
    lines: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Последние логи OpenClaw. MVP: заглушка."""
    server = await _get_user_server(db, current_user.id)

    # TODO: SSH → journalctl -u openclaw -n {lines}
    return {
        "server_id": server.id,
        "lines": lines,
        "logs": "Логи будут доступны после подключения SSH-интеграции (MVP)",
    }

