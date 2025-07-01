# src/api/auth.py
import os
import time
import requests
from typing import Optional

AUTH_URL = "https://giris.epias.com.tr/cas/v1/tickets"
TOKEN_HEADER = "TGT"          # header name required by every data call
TTL_SECONDS = 2 * 60 * 60     # token validity (2 h)

class TGTManager:
    """Fetches and silently refreshes EPİAŞ CAS tokens."""
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self._token: Optional[str] = None
        self._expires_at: float = 0.0

    # ------------------------------------------------------------------ #
    def current(self, force_refresh: bool = False) -> str:
        if force_refresh or time.time() >= self._expires_at:
            self._token = self._request_new_token()
            self._expires_at = time.time() + TTL_SECONDS - 60  # refresh 1 min early
        return self._token

    # ------------------------------------------------------------------ #
    def _request_new_token(self) -> str:
        resp = requests.post(
            AUTH_URL,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/plain",
            },
            data=f"username={self.username}&password={self.password}",
            timeout=10,
        )
        resp.raise_for_status()          # will raise on 4xx/5xx
        token = resp.text.strip()
        if not token.startswith("TGT-"):
            raise ValueError("Unexpected token format returned by CAS")
        return token
