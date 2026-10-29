"""Async client for the Wazuh manager REST API.

Auth flow: POST /security/user/authenticate with HTTP Basic auth returns a JWT.
Every other request sends it as "Authorization: Bearer <token>". Tokens expire
(900s by default), so on a 401 we log in again and retry once.
"""

import logging
from typing import Any

import httpx

from wazuh_mcp.config import Settings

logger = logging.getLogger(__name__)


class WazuhAPIError(Exception):
    """The Wazuh API answered with an error."""


class WazuhAPIClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.verify_ssl:
            logger.warning("TLS verification is DISABLED for the Wazuh API. Use only in a lab.")
        self._user = settings.api_user
        self._password = settings.api_password
        self._token: str | None = None
        self._http = httpx.AsyncClient(
            base_url=settings.api_url,
            verify=settings.verify_ssl,
            timeout=30.0,
        )

    async def _authenticate(self) -> None:
        response = await self._http.post(
            "/security/user/authenticate",
            auth=(self._user, self._password.get_secret_value()),
        )
        if response.status_code != 200:
            raise WazuhAPIError(f"Authentication failed (HTTP {response.status_code})")
        self._token = response.json()["data"]["token"]
        logger.info("Authenticated against the Wazuh API")

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """GET an API endpoint and return the "data" section of the response.

        Wazuh wraps results as:
            {"data": {"affected_items": [...], "total_affected_items": N, ...}, "error": 0}
        """
        if self._token is None:
            await self._authenticate()

        response = await self._http.get(path, params=params, headers=self._auth_header())
        if response.status_code == 401:  # token expired
            await self._authenticate()
            response = await self._http.get(path, params=params, headers=self._auth_header())

        if response.status_code != 200:
            detail = response.json().get("detail", response.text) if response.content else ""
            raise WazuhAPIError(f"GET {path} failed (HTTP {response.status_code}): {detail}")
        return response.json()["data"]

    def _auth_header(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}

    async def aclose(self) -> None:
        await self._http.aclose()
