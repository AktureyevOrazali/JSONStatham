"""Payment webhook handler."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentWebhook
from app.services.subscription_service import activate_subscription

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/payment")
async def payment_webhook(
    data: PaymentWebhook,
    db: AsyncSession = Depends(get_db),
):
    """
    Webhook от платёжной системы (ЮKassa / Робокасса).
    При успешной оплате активирует подписку.
    """
    # Find payment by external_id
    stmt = select(Payment).where(Payment.external_id == data.payment_id)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платёж не найден",
        )

    if data.event == "payment.succeeded":
        payment.status = PaymentStatus.COMPLETED
        # Activate the subscription
        await activate_subscription(db, payment.subscription_id)
    elif data.event == "payment.canceled":
        payment.status = PaymentStatus.FAILED
    else:
        # Unknown event — just log
        pass

    await db.flush()
    return {"status": "ok"}

