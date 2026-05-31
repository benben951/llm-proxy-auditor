# LLM Proxy Auditor

Audit OpenAI-compatible LLM API gateways for model substitution, prompt tampering, response rewriting, privacy leakage, and agent-safety risks.

## Portfolio Snapshot

This project is a lightweight security and trust tool for people who route agent traffic through third-party OpenAI-compatible proxies.

- Portfolio angle: AI safety checks for agent infrastructure and enterprise LLM adoption
- Core evidence: deterministic probe design, structured scoring, Markdown trust reports, and regression tests
- Practical question: can this proxy be trusted enough for Codex, Claude Code, browser agents, or internal workflows?

## Why It Matters

An OpenAI-compatible proxy can theoretically:

- rewrite system or user prompts
- downgrade or substitute the actual model
- inject hidden instructions or promotional text
- rewrite model responses after generation
- mishandle structured outputs or tool-call protocols used by agents
- log sensitive data such as code, documents, or workflow context

`llm-proxy-auditor` sends deterministic probes and produces a trust-oriented report instead of leaving this as a vague feeling.

## Features

- OpenAI-compatible `/v1/chat/completions` audit
- canary token tests for prompt and response rewriting
- strict JSON and nonce integrity tests
- prompt-injection smoke tests
- fake-secret leakage and echo checks
- optional reference-provider comparison
- agent-readiness risk score
- Markdown and JSON output
- zero runtime dependencies in the core auditor

## Quick Start

```powershell
git clone https://github.com/benben951/llm-proxy-auditor.git
cd llm-proxy-auditor
python -m pip install -e ".[dev]"
```

List probes:

```powershell
python -m proxy_auditor list-probes
```

Run an audit:

```powershell
python -m proxy_auditor audit `
  --base-url "https://your-proxy.example.com/v1" `
  --api-key "$env:PROXY_API_KEY" `
  --model "gpt-4o-mini" `
  --out "trust_report.md"
```

## Output

The report includes:

- overall trust level
- probe-by-probe findings
- suspicious evidence snippets
- agent-safety recommendation
- raw request metadata without exposing secrets

Example:

```text
Overall: MEDIUM RISK
Agent safety: Not recommended for autonomous file/browser/tool agents.
Findings:
- Strict JSON integrity failed.
- Response contained unexpected wrapper text.
- Tool-call compatibility not tested in this MVP.
```

See [examples/trust_report_example.md](examples/trust_report_example.md) for a sample report.

## Limits

- It cannot prove a provider never logs traffic.
- It cannot perfectly identify the real underlying model.
- It does not replace legal, vendor, or enterprise security review.
- It should only be used with synthetic canaries and fake secrets, never real confidential data.

## Development

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## Resume Angle

Built a trust-audit tool for OpenAI-compatible LLM proxies that checks prompt integrity, structured-output stability, model-substitution risk, and agent readiness before those endpoints are connected to coding or browser agents.
