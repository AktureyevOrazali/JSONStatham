"""Subscriptions API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.subscription import PLANS, PlanInfo, SubscriptionCreate, SubscriptionResponse
from app.services.subscription_service import (
    cancel_subscription,
    create_subscription,
    get_active_subscription,
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/plans", response_model=list[PlanInfo])
async def list_plans():
    """Список доступных тарифных планов."""
    return PLANS


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_new_subscription(
    data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать новую подписку (в статусе pending — ожидает оплаты)."""
    # Check plan exists
    valid_slugs = [p.slug for p in PLANS]
    if data.plan not in valid_slugs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неизвестный план: {data.plan}. Допустимые: {valid_slugs}",
        )

    # Check no active subscription
    existing = await get_active_subscription(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="У вас уже есть активная подписка",
        )

    subscription = await create_subscription(db, current_user.id, data.plan)
    return subscription


@router.get("/current", response_model=SubscriptionResponse | None)
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Текущая активная подписка (или null)."""
    sub = await get_active_subscription(db, current_user.id)
    return sub


@router.post("/current/cancel", response_model=SubscriptionResponse)
async def cancel_current_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Отменить текущую подписку."""
    sub = await get_active_subscription(db, current_user.id)
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активная подписка не найдена",
        )
    cancelled = await cancel_subscription(db, sub.id)
    return cancelled

