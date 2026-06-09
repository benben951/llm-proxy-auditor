# v0.1 Release Notes

LLM Proxy Auditor v0.1 provides a lightweight trust-audit workflow for OpenAI-compatible LLM endpoints and proxies.

## Highlights

- Deterministic probe list for proxy and agent-safety checks.
- Scoring explanation for trust-level and agent-readiness decisions.
- Markdown trust report example.
- Synthetic canary and fake-secret discipline.
- CLI entry points for listing probes, explaining scoring, and running audits.
- CI-backed tests.

## Good First Review Path

1. Run `python -m proxy_auditor list-probes`.
2. Run `python -m proxy_auditor explain-scoring`.
3. Read `examples/trust_report_example.md`.
4. Run `python -m pytest -q`.

## Boundary

The auditor cannot prove provider logging behavior or replace enterprise security review. It is a practical probe layer for safer agent endpoint selection.
