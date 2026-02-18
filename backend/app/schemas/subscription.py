"""Pydantic schemas for Subscription."""

from datetime import datetime

from pydantic import BaseModel


class PlanInfo(BaseModel):
    """Subscription plan details for display."""
    name: str
    slug: str  # starter / pro / enterprise
    price_monthly: float
    description: str
    features: list[str]


class SubscriptionCreate(BaseModel):
    plan: str  # starter / pro / enterprise


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan: str
    status: str
    starts_at: datetime | None = None
    expires_at: datetime | None = None
    auto_renew: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Static plan definitions ──

PLANS: list[PlanInfo] = [
    PlanInfo(
        name="Starter",
        slug="starter",
        price_monthly=990.0,
        description="Для начала работы с OpenClaw",
        features=[
            "1 сервер",
            "1 Telegram-бот",
            "Базовая поддержка",
            "1 GB RAM VPS",
        ],
    ),
    PlanInfo(
        name="Pro",
        slug="pro",
        price_monthly=1990.0,
        description="Для продвинутых пользователей",
        features=[
            "1 сервер",
            "До 3 каналов (Telegram, WhatsApp и др.)",
            "Приоритетная поддержка",
            "2 GB RAM VPS",
            "Расширенная аналитика",
        ],
    ),
    PlanInfo(
        name="Enterprise",
        slug="enterprise",
        price_monthly=4990.0,
        description="Для бизнеса и команд",
        features=[
            "До 3 серверов",
            "Неограниченные каналы",
            "Выделенная поддержка 24/7",
            "4 GB RAM VPS",
            "Custom домен",
            "SLA 99.9%",
        ],
    ),
]
