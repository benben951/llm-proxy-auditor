# Agent Safety Playbook

## Before Connecting A Proxy To Agents

Run `llm-proxy-auditor` before routing coding agents, browser agents, or document agents through a third-party proxy.

Minimum checks:

- Run all default probes.
- Save Markdown and JSON reports.
- Use fake secrets only.
- Compare against a trusted reference endpoint when possible.
- Re-run after provider, model, or base URL changes.

## Suggested Decision Policy

| Result | Decision |
|---|---|
| LOW | Allow low-risk experiments. Do not send real secrets. |
| MEDIUM | Chat-only or toy tasks. No autonomous file/browser/tool agents. |
| HIGH | Block agent usage until failures are explained. |
| CRITICAL | Do not use the endpoint for sensitive or agentic workflows. |

## What Counts As Sensitive

- Source code from private repositories.
- Browser cookies or session tokens.
- API keys and cloud credentials.
- Customer data.
- Internal documents.
- Financial, legal, health, or education records.
- Agent memory and long-running workflow context.

## CI Gate Example

Use a non-production API key and synthetic probes:

```powershell
python -m proxy_auditor audit `
  --base-url "$env:PROXY_BASE_URL" `
  --api-key "$env:PROXY_API_KEY" `
  --model "$env:PROXY_MODEL" `
  --out "artifacts/trust_report.md" `
  --json-out "artifacts/trust_report.json" `
  --fail-on high
```

## Important Limitations

- Passing probes does not prove the provider never logs traffic.
- Failing probes do not prove malicious behavior.
- The tool is a practical trust screen, not a replacement for vendor review.
- Never test with real credentials or confidential data.
