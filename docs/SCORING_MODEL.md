# Scoring Model

## Goal

The scoring model estimates whether an OpenAI-compatible endpoint is appropriate for agentic workflows. It is not a legal, compliance, or vendor-security verdict.

## Severity Weights

| Severity | Weight | Meaning |
|---|---:|---|
| low | 1 | Weak signal or minor instability. |
| medium | 2 | May break structured or deterministic workflows. |
| high | 3 | Strong signal of rewriting, routing, or unsafe handling. |
| critical | 5 | Severe failure that should block agent use. |

## Risk Levels

| Level | Failed risk ratio | Guidance |
|---|---:|---|
| LOW | 0 | Reasonable for low-risk non-sensitive workloads. Still avoid real secrets. |
| MEDIUM | <= 25% | Use for low-risk tasks only. Do not connect autonomous agents or private data yet. |
| HIGH | <= 60% | Not recommended for coding, browser, or business agents. Investigate failures first. |
| CRITICAL | > 60% | Do not use for agentic workflows or sensitive data. |

## Why Failed Ratio Instead Of Raw Count

Different probe sets can include different severities. A single high-severity failure should matter more than several weak signals. The failed-risk ratio keeps the model simple while still giving more weight to severe failures.

## How To Explain A Result

When reviewing a report, read it in this order:

1. Overall risk level.
2. Agent recommendation.
3. Failed probes.
4. Evidence snippets.
5. Whether failures affect your actual use case.

For example, strict JSON failure is especially important for coding agents, API agents, and workflows that expect machine-readable outputs. It may matter less for one-off casual chat.

## CLI Reference

Show the scoring model from the CLI:

```powershell
python -m proxy_auditor explain-scoring
```

Use CI-style failure thresholds:

```powershell
python -m proxy_auditor audit `
  --base-url "https://proxy.example/v1" `
  --api-key "$env:PROXY_API_KEY" `
  --model "gpt-4o-mini" `
  --fail-on high
```
