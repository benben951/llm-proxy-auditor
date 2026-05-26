from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class ChatResponse:
    ok: bool
    status_code: int | None
    content: str
    raw: dict[str, Any] | None
    latency_ms: int
    error: str | None = None


class OpenAICompatClient:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.0) -> ChatResponse:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "llm-proxy-auditor/0.1",
            },
            method="POST",
        )
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw_text = resp.read().decode("utf-8", errors="replace")
                latency_ms = int((time.perf_counter() - start) * 1000)
                raw = json.loads(raw_text)
                content = _extract_content(raw)
                return ChatResponse(True, resp.status, content, raw, latency_ms)
        except urllib.error.HTTPError as exc:
            latency_ms = int((time.perf_counter() - start) * 1000)
            error_body = exc.read().decode("utf-8", errors="replace")
            return ChatResponse(False, exc.code, "", None, latency_ms, error_body)
        except Exception as exc:  # noqa: BLE001 - CLI tool should report any transport issue.
            latency_ms = int((time.perf_counter() - start) * 1000)
            return ChatResponse(False, None, "", None, latency_ms, repr(exc))


def _extract_content(raw: dict[str, Any]) -> str:
    try:
        return str(raw["choices"][0]["message"].get("content") or "")
    except (KeyError, IndexError, TypeError):
        return ""

