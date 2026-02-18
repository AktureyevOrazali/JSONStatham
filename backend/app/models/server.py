"""Server model."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class ServerStatus(str, enum.Enum):
    PROVISIONING = "provisioning"
    CONFIGURING = "configuring"
    ACTIVE = "active"
    STOPPED = "stopped"
    ERROR = "error"


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("subscriptions.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), default="My OpenClaw Server")
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)  # hetzner / contabo / custom
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    ssh_port: Mapped[int] = mapped_column(Integer, default=22)
    status: Mapped[ServerStatus] = mapped_column(
        Enum(ServerStatus, name="server_status"),
        default=ServerStatus.PROVISIONING,
        server_default="provisioning",
    )
    openclaw_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    openclaw_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_health_check: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="servers")
    subscription = relationship("Subscription", back_populates="server")
    logs = relationship("ServerLog", back_populates="server", lazy="selectin")
    api_keys = relationship("ApiKey", back_populates="server", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Server id={self.id} ip={self.ip_address} status={self.status}>"
