from __future__ import annotations

import json

from proxy_auditor.client import ChatResponse
from proxy_auditor.probes import (
    probe_basic_connectivity,
    probe_canary_rewrite,
    probe_fake_secret_echo,
    probe_hidden_instruction_smoke,
    probe_reference_similarity,
    probe_strict_json_nonce,
)


class FakeClient:
    model = "fake-model"

    def __init__(self, responder):
        self.responder = responder

    def chat(self, messages, temperature=0.0):
        del temperature
        content = self.responder(messages)
        return ChatResponse(True, 200, content, {"choices": [{"message": {"content": content}}]}, 7)


def test_basic_connectivity_passes_exact_pong():
    result = probe_basic_connectivity(FakeClient(lambda messages: "pong"))

    assert result.passed


def test_strict_json_nonce_passes_when_nonce_is_preserved():
    def responder(messages):
        nonce = messages[-1]["content"].split('"nonce":"', 1)[1].split('"', 1)[0]
        return json.dumps({"nonce": nonce, "ok": True}, separators=(",", ":"))

    result = probe_strict_json_nonce(FakeClient(responder))

    assert result.passed


def test_canary_rewrite_fails_on_wrapper_text():
    def responder(messages):
        token = messages[-1]["content"].split(": ", 1)[1]
        return f"Sure, here is the token: {token}"

    result = probe_canary_rewrite(FakeClient(responder))

    assert not result.passed
    assert "wrapper" in result.summary.lower()


def test_fake_secret_echo_fails_when_full_fake_key_is_echoed():
    def responder(messages):
        return messages[-1]["content"].split("fake key: ", 1)[1]

    result = probe_fake_secret_echo(FakeClient(responder))

    assert not result.passed
    assert result.severity == "high"


def test_hidden_instruction_smoke_fails_on_provider_text():
    result = probe_hidden_instruction_smoke(FakeClient(lambda messages: "clean via proxy provider"))

    assert not result.passed


def test_reference_similarity_passes_on_matching_integer():
    result = probe_reference_similarity(FakeClient(lambda messages: "323"), FakeClient(lambda messages: "323"))

    assert result.passed
