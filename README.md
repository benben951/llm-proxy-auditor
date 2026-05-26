# LLM Proxy Auditor

Audit OpenAI-compatible LLM API gateways for model substitution, prompt tampering, response rewriting, privacy leakage, and Agent-safety risks.

中文一句话：检测你的 AI 中转站有没有夹带私货，是否适合接入 Codex、Claude Code、browser agents、内部业务 Agent。

This project is for people who use third-party LLM proxy services and want a lightweight way to answer one practical question:

> Can I trust this proxy enough to connect it to my coding agent, browser agent, or business workflow?

## Why

An OpenAI-compatible proxy can theoretically:

- Rewrite your system or user prompts.
- Downgrade or substitute the model while keeping the advertised model name.
- Inject hidden instructions or promotional text.
- Rewrite model responses after generation.
- Log sensitive data, API keys, code snippets, business documents, or tool-call context.
- Break structured outputs, streaming, or tool-call protocols used by agents.

`llm-proxy-auditor` sends deterministic probes and produces a Markdown trust report.

## Features

- OpenAI-compatible `/v1/chat/completions` audit.
- Canary token tests for prompt/response rewriting.
- Strict JSON and nonce integrity tests.
- Prompt-injection smoke tests.
- Fake-secret leakage and echo checks.
- Optional reference-provider comparison.
- Agent-readiness risk score.
- Markdown and JSON output.
- Zero runtime dependencies in the core auditor.

## Quick Start

Install from source:

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

By default, the CLI exits non-zero when the risk is `HIGH` or `CRITICAL`. For exploratory checks:

```powershell
python -m proxy_auditor audit `
  --base-url "https://your-proxy.example.com/v1" `
  --api-key "$env:PROXY_API_KEY" `
  --model "gpt-4o-mini" `
  --fail-on never
```

Optional reference comparison:

```powershell
python -m proxy_auditor audit `
  --base-url "https://your-proxy.example.com/v1" `
  --api-key "$env:PROXY_API_KEY" `
  --model "gpt-4o-mini" `
  --reference-base-url "https://api.openai.com/v1" `
  --reference-api-key "$env:OPENAI_API_KEY" `
  --reference-model "gpt-4o-mini" `
  --out "trust_report.md"
```

## Output

The report includes:

- Overall trust level.
- Probe-by-probe result table.
- Suspicious evidence snippets.
- Agent-safety recommendation.
- Raw request metadata without exposing API keys.

Example:

```text
Overall: MEDIUM RISK
Agent safety: Not recommended for autonomous file/browser/tool agents.
Findings:
- Strict JSON integrity failed.
- Response contained unexpected wrapper text.
- Tool-call compatibility not tested in this MVP.
```

See [`examples/trust_report_example.md`](examples/trust_report_example.md) for a sample report.

## What It Can Detect

- Obvious prompt or response rewriting.
- Hidden wrappers, provider ads, or extra policy text.
- JSON/nonce corruption that breaks agent structured-output loops.
- Synthetic fake-secret mishandling.
- Simple reference mismatch against a trusted endpoint.

## What It Cannot Prove

- It cannot prove a provider never logs traffic.
- It cannot perfectly identify the real underlying model.
- It cannot replace legal, vendor, or enterprise security review.
- It should not be used with real secrets or private data.

## Safety

Do not send real secrets, customer data, private code, browser cookies, or company documents to untrusted proxies. This tool uses synthetic canaries and fake secrets only.

## Development

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## Roadmap

- Streaming protocol audit.
- Tool-call compatibility probes.
- Model fingerprint library.
- Cache contamination probes.
- HTML dashboard.
- GitHub Action for scheduled proxy checks.

## License

MIT
