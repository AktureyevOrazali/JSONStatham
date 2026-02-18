"""Subscription service — business logic for plans and subscriptions."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus


async def create_subscription(
    db: AsyncSession,
    user_id: int,
    plan: str,
) -> Subscription:
    """Create a new subscription in PENDING status (waiting for payment)."""
    subscription = Subscription(
        user_id=user_id,
        plan=SubscriptionPlan(plan),
        status=SubscriptionStatus.PENDING,
    )
    db.add(subscription)
    await db.flush()
    await db.refresh(subscription)
    return subscription


async def activate_subscription(
    db: AsyncSession,
    subscription_id: int,
    duration_days: int = 30,
) -> Subscription | None:
    """Activate a subscription after successful payment."""
    stmt = select(Subscription).where(Subscription.id == subscription_id)
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()

    if not subscription:
        return None

    now = datetime.now(timezone.utc)
    subscription.status = SubscriptionStatus.ACTIVE
    subscription.starts_at = now
    subscription.expires_at = now + timedelta(days=duration_days)
    await db.flush()
    await db.refresh(subscription)
    return subscription


async def get_active_subscription(
    db: AsyncSession,
    user_id: int,
) -> Subscription | None:
    """Get the user's current active subscription."""
    stmt = (
        select(Subscription)
        .where(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE,
        )
        .order_by(Subscription.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def cancel_subscription(
    db: AsyncSession,
    subscription_id: int,
) -> Subscription | None:
    """Cancel a subscription."""
    stmt = select(Subscription).where(Subscription.id == subscription_id)
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()

    if not subscription:
        return None

    subscription.status = SubscriptionStatus.CANCELLED
    subscription.auto_renew = False
    await db.flush()
    await db.refresh(subscription)
    return subscription
