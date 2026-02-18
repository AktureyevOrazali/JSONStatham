"""Pydantic schemas for Server."""

from datetime import datetime

from pydantic import BaseModel


class ServerResponse(BaseModel):
    id: int
    user_id: int
    subscription_id: int
    name: str
    provider: str | None = None
    ip_address: str | None = None
    status: str
    openclaw_version: str | None = None
    last_health_check: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ServerStatus(BaseModel):
    """Server status including metrics."""
    is_online: bool
    uptime: str | None = None
    cpu_percent: float | None = None
    ram_used_mb: float | None = None
    ram_total_mb: float | None = None
    disk_used_gb: float | None = None
    disk_total_gb: float | None = None
    openclaw_status: str | None = None  # running / stopped / error


class ServerActionResult(BaseModel):
    success: bool
    message: str
    action: str  # restart / stop / update
