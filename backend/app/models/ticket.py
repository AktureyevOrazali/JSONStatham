"""Ticket, ServerLog, and ApiKey models."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ── Ticket ──


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    server_id: Mapped[int | None] = mapped_column(
        ForeignKey("servers.id"), nullable=True
    )
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, name="ticket_status"),
        default=TicketStatus.OPEN,
        server_default="open",
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="tickets")

    def __repr__(self) -> str:
        return f"<Ticket id={self.id} status={self.status}>"


# ── Server Log ──


class ServerLog(Base):
    __tablename__ = "server_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # start / stop / restart / ...
    result: Mapped[str] = mapped_column(String(50), nullable=False)  # success / failure
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    server = relationship("Server", back_populates="logs")

    def __repr__(self) -> str:
        return f"<ServerLog id={self.id} action={self.action} result={self.result}>"


# ── API Key ──


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)  # openai / anthropic / ...
    key_masked: Mapped[str] = mapped_column(String(50), nullable=False)  # sk-...xxxx
    key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)  # AES-256
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    server = relationship("Server", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<ApiKey id={self.id} provider={self.provider}>"

