from __future__ import annotations

import httpx


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=10)

    @staticmethod
    def _headers(token: str | None = None, extra_headers: dict[str, str] | None = None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        headers.update(extra_headers or {})
        return headers

    def get(
        self,
        path: str,
        token: str | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        headers = self._headers(token, extra_headers)
        response = self.client.get(f"{self.base_url}{path}", headers=headers)
        response.raise_for_status()
        return response.json()

    def post(
        self,
        path: str,
        payload: dict | None = None,
        token: str | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        headers = self._headers(token, extra_headers)
        response = self.client.post(f"{self.base_url}{path}", json=payload or {}, headers=headers)
        response.raise_for_status()
        return response.json()

    def put(
        self,
        path: str,
        payload: dict | None = None,
        token: str | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        headers = self._headers(token, extra_headers)
        response = self.client.put(f"{self.base_url}{path}", json=payload or {}, headers=headers)
        response.raise_for_status()
        return response.json()

    def close(self):
        self.client.close()
