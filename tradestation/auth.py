"""
TradeStation OAuth2 authentication handler.
"""

import logging
from datetime import datetime, timedelta

import requests

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""


class TradeStationAuth:
    """
    Handles TradeStation OAuth2 authentication with automatic token refresh.

    The access token is automatically refreshed when it expires or is about
    to expire (within 5 minutes of expiration).

    Example:
        auth = TradeStationAuth(client_id, client_secret, refresh_token)
        token = auth.get_access_token()  # Automatically refreshes if needed
    """

    TOKEN_URL = "https://signin.tradestation.com/oauth/token"
    REFRESH_BUFFER_MINUTES = 5

    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        """
        Initialize the authentication handler.

        Args:
            client_id: TradeStation API client ID
            client_secret: TradeStation API client secret
            refresh_token: OAuth2 refresh token for obtaining access tokens
        """
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._access_token: str | None = None
        self._token_expiry: datetime | None = None

    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.

        Returns:
            A valid access token string

        Raises:
            AuthenticationError: If token refresh fails
        """
        if not self._is_token_valid():
            self._refresh_access_token()
        return self._access_token

    def _is_token_valid(self) -> bool:
        """Check if the current token is valid and not near expiration."""
        if not self._access_token or not self._token_expiry:
            return False
        buffer = timedelta(minutes=self.REFRESH_BUFFER_MINUTES)
        return datetime.now() < (self._token_expiry - buffer)

    def _refresh_access_token(self) -> None:
        """
        Refresh the access token using the refresh token.

        Raises:
            AuthenticationError: If the refresh request fails
        """
        logger.info("Refreshing access token...")

        payload = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "refresh_token": self._refresh_token,
        }

        try:
            response = requests.post(self.TOKEN_URL, data=payload, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Token refresh failed: {e}") from e

        data = response.json()

        if "access_token" not in data:
            raise AuthenticationError(f"Invalid token response: {data}")

        self._access_token = data["access_token"]
        expires_in = data.get("expires_in", 1200)  # Default 20 minutes
        self._token_expiry = datetime.now() + timedelta(seconds=expires_in)

        logger.info("Token refreshed, expires in %ds", expires_in)

    def invalidate(self) -> None:
        """Invalidate the current token, forcing a refresh on next use."""
        self._access_token = None
        self._token_expiry = None
