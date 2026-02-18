"""Pydantic schemas for User."""

from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TelegramAuthData(BaseModel):
    """Data received from Telegram initData or bot."""
    telegram_id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    auth_date: int | None = None
    hash: str | None = None  # For initData validation


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
