"""HTTP client for communicating with the Backend API."""

import httpx

from bot.app.config import bot_settings


class ApiClient:
    """Async HTTP client that wraps communication with the platform backend."""

    def __init__(self):
        self.base_url = bot_settings.api_url
        self._tokens: dict[int, str] = {}  # telegram_id → access_token cache

    async def _get_headers(self, telegram_id: int) -> dict:
        """Get auth headers; authenticate if needed."""
        token = self._tokens.get(telegram_id)
        if not token:
            token = await self.authenticate(telegram_id)
        return {"Authorization": f"Bearer {token}"}

    async def authenticate(
        self,
        telegram_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
    ) -> str:
        """Authenticate user via backend and cache the token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/telegram",
                json={
                    "telegram_id": telegram_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username,
                },
            )
            response.raise_for_status()
            data = response.json()
            self._tokens[telegram_id] = data["access_token"]
            return data["access_token"]

    async def get_me(self, telegram_id: int) -> dict:
        """Get current user profile."""
        headers = await self._get_headers(telegram_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/users/me", headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def get_plans(self) -> list[dict]:
        """Get available subscription plans."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/subscriptions/plans")
            resp.raise_for_status()
            return resp.json()

    async def create_subscription(self, telegram_id: int, plan: str) -> dict:
        """Create a new subscription."""
        headers = await self._get_headers(telegram_id)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/subscriptions",
                headers=headers,
                json={"plan": plan},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_current_subscription(self, telegram_id: int) -> dict | None:
        """Get user's active subscription."""
        headers = await self._get_headers(telegram_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/subscriptions/current",
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_server(self, telegram_id: int) -> dict | None:
        """Get user's server info."""
        headers = await self._get_headers(telegram_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/servers/my", headers=headers)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()

    async def get_server_status(self, telegram_id: int) -> dict | None:
        """Get server status and metrics."""
        headers = await self._get_headers(telegram_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/servers/my/status", headers=headers)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()

    async def restart_server(self, telegram_id: int) -> dict:
        """Restart the user's server."""
        headers = await self._get_headers(telegram_id)
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/servers/my/restart", headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def get_server_logs(self, telegram_id: int, lines: int = 50) -> dict:
        """Get server logs."""
        headers = await self._get_headers(telegram_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/servers/my/logs",
                headers=headers,
                params={"lines": lines},
            )
            resp.raise_for_status()
            return resp.json()


# Singleton instance
api_client = ApiClient()
