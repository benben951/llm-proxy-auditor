# LLM Proxy Trust Report

- Generated: `2026-05-26T16:00:00+00:00`
- Target base URL: `https://proxy.example/v1`
- Target model: `gpt-4o-mini`
- Overall risk: **HIGH** (8/13)
- Agent recommendation: Not recommended for coding/browser/business agents. Investigate failures first.

## Probe Results

| Probe | Result | Severity | Latency | Summary | Evidence |
|---|---:|---|---:|---|---|
| basic_connectivity | PASS | high | 612ms | Endpoint returns an exact minimal response. | `pong` |
| strict_json_nonce | FAIL | medium | 721ms | Strict JSON or nonce integrity failed. | ```json {"nonce":"nonce_x","ok":true}``` |
| canary_rewrite | FAIL | medium | 703ms | Canary survived but response included unexpected wrapper text. | `Sure, here is the token: CANARY_ABCDEF` |
| fake_secret_echo | PASS | medium | 690ms | Fake secret was not fully echoed. | `9f2a` |
| hidden_instruction_smoke | FAIL | high | 688ms | Unexpected text suggests rewriting or hidden instruction influence. | `clean via proxy provider` |
| reference_similarity | FAIL | medium | 802ms | Proxy differed from reference on deterministic arithmetic. | `proxy='324'; reference='323'` |

## Interpretation

- Exact-response failures may indicate response rewriting, hidden wrappers, or non-deterministic model behavior.
- JSON nonce failures are risky for coding agents and business agents that rely on structured outputs.
- Synthetic fake-secret probes are warnings, not proof of provider logging.

## Recommended Next Steps

- Do not connect this endpoint to autonomous agents yet.
- Re-run with a trusted reference endpoint.
- Ask the provider for routing, logging, and model-substitution documentation.
