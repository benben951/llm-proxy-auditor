# Case Study: LLM Proxy Trust Audit

## Problem

OpenAI-compatible proxy gateways are convenient, but they introduce a trust boundary between the user and the model. A proxy can claim compatibility while still rewriting prompts, wrapping responses, substituting models, breaking structured outputs, or mishandling sensitive workflow context.

That risk becomes sharper when the endpoint is connected to coding agents, browser agents, document agents, or internal business workflows. In those settings, small response modifications can break tool protocols or leak private context.

## Product Framing

`llm-proxy-auditor` is a lightweight CLI that answers one practical question:

> Is this endpoint safe enough to connect to autonomous or semi-autonomous agents?

It does not try to prove a provider is perfectly safe. Instead, it creates repeatable evidence through synthetic probes and generates a trust report that a developer can review before routing real agent traffic.

## What It Tests

- Basic endpoint compatibility.
- Exact-response integrity.
- Strict JSON and nonce preservation.
- Canary-token rewriting.
- Synthetic secret handling.
- Hidden-instruction or promotional text smoke tests.
- Optional comparison against a reference endpoint.

## Why This Is Portfolio-Relevant

This project demonstrates AI evaluation work that is closer to production risk than a generic chatbot demo:

- It defines a threat model around agent infrastructure.
- It turns vague trust concerns into deterministic probes.
- It produces Markdown and JSON artifacts for review and CI.
- It includes regression tests around scoring, report generation, and CLI behavior.
- It keeps safety boundaries explicit: synthetic canaries only, never real secrets.

## Engineering Decisions

### Deterministic Probes First

The tool uses simple prompts such as exact-string replies, strict JSON, and canary tokens. These are intentionally boring. Boring probes are easier to reason about, easier to reproduce, and easier to explain to a reviewer.

### Agent-Safety Scoring

The score is not a generic security score. It is an agent-readiness score. A proxy that fails structured JSON or injects wrapper text may be fine for casual chat, but risky for coding agents and browser agents that depend on strict outputs.

### Reports Over Console Logs

The CLI writes Markdown and JSON reports so the output can be archived, compared, attached to issues, or used in CI gates.

## Example Interview Explanation

> I built a CLI to audit OpenAI-compatible LLM proxies before connecting them to coding or browser agents. The tool sends deterministic probes for prompt integrity, JSON nonce preservation, canary rewriting, fake-secret handling, and hidden-instruction smoke tests. It then produces a risk score and Markdown/JSON trust reports. The project is less about proving a provider is safe forever, and more about turning proxy trust into repeatable evidence before agent traffic touches private code or business data.

## Next Iterations

- Add tool-call protocol probes.
- Add streaming-response integrity checks.
- Add model-card and provider metadata capture.
- Add baseline comparison across multiple trusted providers.
- Add a GitHub Actions template for recurring endpoint checks.
