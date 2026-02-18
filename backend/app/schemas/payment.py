"""Pydantic schemas for Payment."""

from datetime import datetime

from pydantic import BaseModel


class PaymentCreate(BaseModel):
    subscription_id: int
    amount: float
    provider: str = "yookassa"


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    subscription_id: int
    amount: float
    currency: str
    provider: str
    external_id: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentWebhook(BaseModel):
    """Incoming webhook from payment provider."""
    event: str  # payment.succeeded / payment.canceled
    payment_id: str
    amount: float | None = None
    currency: str | None = None
    metadata: dict | None = None
