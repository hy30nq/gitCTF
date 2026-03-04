"""Git-based CTF v2.0 — GitHub API client.

All CTF data lives on GitHub. This module is the sole interface to read/write
that data: Issues, Notifications, Labels, file contents, etc.
Uses httpx for modern HTTP with proper error handling.
"""

from __future__ import annotations

import base64
import getpass
import json
import sys
from typing import Any

import httpx

API_URL = "https://api.github.com"
TIMEOUT = 30.0


def _get_github_path(url: str) -> str:
    """Extract 'owner/repo' from a GitHub URL."""
    if url.startswith("https://github.com/"):
        parts = url[19:].split("/")
    elif url.startswith("git@github.com:"):
        parts = url[15:].split("/")
    else:
        print(f"[!] Cannot parse GitHub URL: {url}")
        sys.exit(1)
    owner = parts[0]
    repo = parts[1].removesuffix(".git")
    return f"{owner}/{repo}"


def decode_content(response: dict) -> str:
    if response.get("encoding") == "base64":
        return base64.b64decode(response["content"]).decode("utf-8", errors="replace")
    print(f"[!] Unknown encoding: {response.get('encoding')}")
    sys.exit(1)


get_github_path = _get_github_path


class GitHub:
    """Lightweight GitHub API client. No server, just direct API calls."""

    def __init__(self, username: str, token: str | None = None) -> None:
        headers: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"
        else:
            print(f"GitHub ID: {username}")
            password = getpass.getpass("Password: ")
            # httpx doesn't support .auth on client the same way; use basic auth
            self._auth = (username, password)
            headers = {"Accept": "application/vnd.github.v3+json"}

        self._token = token
        self._username = username
        if token:
            self._client = httpx.Client(
                base_url=API_URL, headers=headers, timeout=TIMEOUT
            )
        else:
            self._client = httpx.Client(
                base_url=API_URL, headers=headers, timeout=TIMEOUT,
                auth=(username, password),
            )

    def _result(self, r: httpx.Response, expected: int) -> dict | list | None:
        if r.status_code == expected:
            return r.json()
        print(f"[!] GitHub API {r.status_code}: {r.text[:200]}")
        return None

    def get(self, query: str, expected: int = 200) -> Any:
        return self._result(self._client.get(query), expected)

    def post(self, query: str, data: str, expected: int = 201) -> Any:
        return self._result(
            self._client.post(query, content=data,
                              headers={"Content-Type": "application/json"}),
            expected,
        )

    def patch(self, query: str, data: str | None) -> bool:
        r = self._client.patch(
            query,
            content=data or "",
            headers={"Content-Type": "application/json"},
        )
        return r.status_code in (200, 205)

    def put(self, query: str, data: str | None = None) -> bool:
        r = self._client.put(
            query,
            content=data or "",
            headers={"Content-Type": "application/json"},
        )
        return r.status_code in (200, 205)

    def poll(self, query: str) -> tuple[list, int]:
        """Poll notifications endpoint, respecting X-Poll-Interval."""
        r = self._client.get(query)
        interval = int(r.headers.get("X-Poll-Interval", "60"))
        if r.status_code == 200:
            return r.json(), interval
        return [], interval
