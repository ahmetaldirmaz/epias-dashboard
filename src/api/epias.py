# src/api/epias.py
import requests
from typing import Any, Dict
from .auth import TGTManager, TOKEN_HEADER

BASE = "https://seffaflik.epias.com.tr/electricity-service/v1"

class EpiasClient:
    def __init__(self, username: str, password: str):
        self.session = requests.Session()
        self.tgt_mgr = TGTManager(username, password)

    # -------------------------------------------------------------- #
    def get(self, path: str, **params) -> Dict[str, Any]:
        return self._request("GET", path, json=params)

    def post(self, path: str, **payload) -> Dict[str, Any]:
        return self._request("POST", path, json=payload)

    # -------------------------------------------------------------- #
    def _request(self, method: str, path: str, **kwargs):
        url = f"{BASE}{path}"
        headers = {
            TOKEN_HEADER: self.tgt_mgr.current(),
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Language": "en",
        }
        resp = self.session.request(method, url, headers=headers, timeout=30, **kwargs)

        # Handle expired token once, then propagate any remaining error
        if resp.status_code in (401, 406):
            headers[TOKEN_HEADER] = self.tgt_mgr.current(force_refresh=True)
            resp = self.session.request(method, url, headers=headers, timeout=30, **kwargs)

        resp.raise_for_status()
        return resp.json()          # 'items' is usually inside this
