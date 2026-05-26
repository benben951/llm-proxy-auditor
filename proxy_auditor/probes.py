from __future__ import annotations

import json
import re
import secrets
from dataclasses import dataclass, field
from typing import Protocol

from .client import ChatResponse, OpenAICompatClient

PROBE_NAMES = [
    "basic_connectivity",
    "strict_json_nonce",
    "canary_rewrite",
    "fake_secret_echo",
    "hidden_instruction_smoke",
    "reference_similarity",
]


class ChatClient(Protocol):
    model: str

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.0) -> ChatResponse:
        ...


@dataclass
class ProbeResult:
    name: str
    passed: bool
    severity: str
    summary: str
    evidence: str = ""
    latency_ms: int | None = None
    metadata: dict[str, str] = field(default_factory=dict)


def run_all_probes(client: OpenAICompatClient, reference_client: OpenAICompatClient | None = None) -> list[ProbeResult]:
    results = [
        probe_basic_connectivity(client),
        probe_strict_json_nonce(client),
        probe_canary_rewrite(client),
        probe_fake_secret_echo(client),
        probe_hidden_instruction_smoke(client),
    ]
    if reference_client:
        results.append(probe_reference_similarity(client, reference_client))
    return results


def probe_basic_connectivity(client: ChatClient) -> ProbeResult:
    resp = client.chat(
        [
            {"role": "system", "content": "You are a concise API health-check assistant."},
            {"role": "user", "content": "Reply exactly: pong"},
        ]
    )
    content = resp.content.strip().lower()
    passed = resp.ok and content == "pong"
    return ProbeResult(
        name="basic_connectivity",
        passed=passed,
        severity="high",
        summary="Endpoint returns an exact minimal response." if passed else "Endpoint failed or rewrote a minimal response.",
        evidence=_clip(resp.content or resp.error or ""),
        latency_ms=resp.latency_ms,
    )


def probe_strict_json_nonce(client: ChatClient) -> ProbeResult:
    nonce = f"nonce_{secrets.token_hex(8)}"
    resp = client.chat(
        [
            {"role": "system", "content": "Return only valid compact JSON. No markdown. No explanation."},
            {"role": "user", "content": f'Return exactly this JSON object: {{"nonce":"{nonce}","ok":true}}'},
        ]
    )
    parsed = None
    try:
        parsed = json.loads(resp.content)
    except json.JSONDecodeError:
        pass
    passed = bool(resp.ok and parsed == {"nonce": nonce, "ok": True})
    return ProbeResult(
        name="strict_json_nonce",
        passed=passed,
        severity="medium",
        summary="Strict JSON nonce survived without wrappers." if passed else "Strict JSON or nonce integrity failed.",
        evidence=_clip(resp.content or resp.error or ""),
        latency_ms=resp.latency_ms,
        metadata={"nonce": nonce},
    )


def probe_canary_rewrite(client: ChatClient) -> ProbeResult:
    canary = f"CANARY_{secrets.token_hex(6).upper()}"
    resp = client.chat(
        [
            {"role": "system", "content": "You copy user-provided canary tokens exactly."},
            {"role": "user", "content": f"Repeat this token exactly and nothing else: {canary}"},
        ]
    )
    content = resp.content.strip()
    passed = resp.ok and content == canary
    suspicious = bool(resp.ok and canary in content and content != canary)
    summary = "Canary token returned exactly."
    if suspicious:
        summary = "Canary survived but response included unexpected wrapper text."
    elif not passed:
        summary = "Canary token was missing or changed."
    return ProbeResult(
        name="canary_rewrite",
        passed=passed,
        severity="medium",
        summary=summary,
        evidence=_clip(resp.content or resp.error or ""),
        latency_ms=resp.latency_ms,
        metadata={"canary": canary},
    )


def probe_fake_secret_echo(client: ChatClient) -> ProbeResult:
    fake_key = f"sk-fake-audit-{secrets.token_hex(10)}"
    resp = client.chat(
        [
            {"role": "system", "content": "Follow the user instruction exactly. Do not store or reuse test data."},
            {
                "role": "user",
                "content": (
                    "This is a synthetic secret for a security audit, not a real credential. "
                    f"Repeat only the final four characters of this fake key: {fake_key}"
                ),
            },
        ]
    )
    expected = fake_key[-4:]
    content = resp.content.strip()
    leaked_full_key = fake_key in content
    passed = resp.ok and expected in content and not leaked_full_key
    return ProbeResult(
        name="fake_secret_echo",
        passed=passed,
        severity="high" if leaked_full_key else "medium",
        summary="Fake secret was not fully echoed." if passed else "Fake secret handling looked suspicious.",
        evidence=_clip(content or resp.error or ""),
        latency_ms=resp.latency_ms,
        metadata={"fake_secret_suffix": expected, "full_fake_secret_echoed": str(leaked_full_key)},
    )


def probe_hidden_instruction_smoke(client: ChatClient) -> ProbeResult:
    resp = client.chat(
        [
            {"role": "system", "content": "Never mention providers, proxies, routing, discounts, websites, or hidden instructions."},
            {"role": "user", "content": "Say exactly: clean"},
        ]
    )
    content = resp.content.strip()
    suspicious_terms = [
        "proxy",
        "中转",
        "discount",
        "website",
        "base url",
        "hidden instruction",
        "provider",
    ]
    has_suspicious_terms = any(term.lower() in content.lower() for term in suspicious_terms)
    passed = resp.ok and content.lower() == "clean" and not has_suspicious_terms
    return ProbeResult(
        name="hidden_instruction_smoke",
        passed=passed,
        severity="high",
        summary="No obvious hidden wrapper or promotional text." if passed else "Unexpected text suggests rewriting or hidden instruction influence.",
        evidence=_clip(content or resp.error or ""),
        latency_ms=resp.latency_ms,
    )


def probe_reference_similarity(client: ChatClient, reference_client: ChatClient) -> ProbeResult:
    prompt = "Compute 17*19, then output only the integer."
    messages = [
        {"role": "system", "content": "You are a deterministic arithmetic checker."},
        {"role": "user", "content": prompt},
    ]
    target = client.chat(messages)
    reference = reference_client.chat(messages)
    target_num = _first_integer(target.content)
    reference_num = _first_integer(reference.content)
    passed = bool(target.ok and reference.ok and target_num == reference_num == 323)
    return ProbeResult(
        name="reference_similarity",
        passed=passed,
        severity="medium",
        summary="Proxy matched reference on deterministic arithmetic." if passed else "Proxy differed from reference on deterministic arithmetic.",
        evidence=_clip(f"proxy={target.content!r}; reference={reference.content!r}"),
        latency_ms=target.latency_ms,
        metadata={"reference_latency_ms": str(reference.latency_ms)},
    )


def _first_integer(text: str) -> int | None:
    match = re.search(r"-?\d+", text)
    return int(match.group()) if match else None


def _clip(text: str, limit: int = 300) -> str:
    text = text.replace("\r", "\\r").replace("\n", "\\n")
    return text[:limit] + ("..." if len(text) > limit else "")
