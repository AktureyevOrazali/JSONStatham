"""Application settings loaded from .env file."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Platform configuration — loaded from .env at the project root."""

    # ── Database ──
    database_url: str = "postgresql+asyncpg://openclaw:openclaw_secret@localhost:5432/openclaw_platform"
    database_url_sync: str = "postgresql://openclaw:openclaw_secret@localhost:5432/openclaw_platform"

    # ── Redis ──
    redis_url: str = "redis://localhost:6379/0"

    # ── JWT ──
    jwt_secret_key: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── Telegram ──
    bot_token: str = ""
    admin_bot_token: str = ""
    admin_telegram_ids: str = ""  # comma-separated

    @property
    def admin_ids(self) -> list[int]:
        if not self.admin_telegram_ids:
            return []
        return [int(x.strip()) for x in self.admin_telegram_ids.split(",") if x.strip()]

    # ── API ──
    api_base_url: str = "http://localhost:8000"
    api_prefix: str = "/api/v1"

    # ── YooKassa ──
    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""
    yookassa_return_url: str = ""

    # ── Encryption ──
    encryption_key: str = ""

    # ── App ──
    debug: bool = True
    app_name: str = "OpenClaw Platform"

    model_config = {
        "env_file": str(Path(__file__).resolve().parent.parent.parent / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
