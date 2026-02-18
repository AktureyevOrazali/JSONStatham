"""Bot configuration loaded from .env."""

from pathlib import Path
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    """Telegram Bot settings."""

    bot_token: str = ""
    api_base_url: str = "http://localhost:8000"
    api_prefix: str = "/api/v1"

    admin_telegram_ids: str = ""

    @property
    def admin_ids(self) -> list[int]:
        if not self.admin_telegram_ids:
            return []
        return [int(x.strip()) for x in self.admin_telegram_ids.split(",") if x.strip()]

    @property
    def api_url(self) -> str:
        return f"{self.api_base_url}{self.api_prefix}"

    model_config = {
        "env_file": str(Path(__file__).resolve().parent.parent.parent / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


bot_settings = BotSettings()
