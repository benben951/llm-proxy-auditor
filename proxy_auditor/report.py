from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .probes import ProbeResult
from .scoring import RiskSummary


def write_markdown_report(path: Path, *, base_url: str, model: str, results: list[ProbeResult], summary: RiskSummary) -> None:
    lines = [
        "# LLM Proxy Trust Report",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Target base URL: `{_redact_url(base_url)}`",
        f"- Target model: `{model}`",
        f"- Overall risk: **{summary.level}** ({summary.score}/{summary.max_score})",
        f"- Agent recommendation: {summary.agent_recommendation}",
        "",
        "## Probe Results",
        "",
        "| Probe | Result | Severity | Latency | Summary | Evidence |",
        "|---|---:|---|---:|---|---|",
    ]
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        latency = "" if result.latency_ms is None else f"{result.latency_ms}ms"
        lines.append(
            "| {name} | {status} | {severity} | {latency} | {summary} | `{evidence}` |".format(
                name=result.name,
                status=status,
                severity=result.severity,
                latency=latency,
                summary=_escape_table(result.summary),
                evidence=_escape_table(result.evidence),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A failed exact-response probe can indicate response rewriting, hidden wrappers, or model non-determinism.",
            "- A failed JSON nonce probe can break agent workflows that depend on structured outputs.",
            "- A fake-secret echo failure does not prove logging, but it is a warning sign for secret-handling behavior.",
            "- This tool uses synthetic probes only. It cannot prove a provider never logs or modifies traffic.",
            "",
            "## Recommended Next Steps",
            "",
            "- Do not send private code, cookies, API keys, customer data, or company documents to untrusted proxies.",
            "- Use low spending limits and separate API keys for proxy testing.",
            "- Prefer official APIs or trusted enterprise gateways for autonomous agents.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json_report(path: Path, *, base_url: str, model: str, results: list[ProbeResult], summary: RiskSummary) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": _redact_url(base_url),
        "model": model,
        "risk": summary.__dict__,
        "results": [
            {
                "name": r.name,
                "passed": r.passed,
                "severity": r.severity,
                "summary": r.summary,
                "evidence": r.evidence,
                "latency_ms": r.latency_ms,
                "metadata": r.metadata,
            }
            for r in results
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _escape_table(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", "\\n")


def _redact_url(url: str) -> str:
    return url.rstrip("/")

