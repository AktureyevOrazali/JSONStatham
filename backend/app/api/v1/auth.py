"""Auth API routes — Telegram login and token refresh."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import TelegramAuthData, TokenResponse
from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_or_create_user,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/telegram", response_model=TokenResponse)
async def auth_telegram(
    data: TelegramAuthData,
    db: AsyncSession = Depends(get_db),
):
    """
    Авторизация через Telegram.
    Принимает данные пользователя из бота или Web App initData.
    Создаёт или обновляет пользователя и возвращает JWT-токены.
    """
    user = await get_or_create_user(
        db=db,
        telegram_id=data.telegram_id,
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name,
    )

    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Обновить access token с использованием refresh token."""
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh token",
        )

    user_id = int(payload["sub"])

    from sqlalchemy import select
    from app.models.user import User

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )

    new_access = create_access_token(user.id, user.role.value)
    new_refresh = create_refresh_token(user.id)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
    )

