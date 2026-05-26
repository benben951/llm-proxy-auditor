from pathlib import Path

from proxy_auditor.probes import ProbeResult
from proxy_auditor.report import write_markdown_report
from proxy_auditor.scoring import score_results


def test_write_markdown_report(tmp_path: Path):
    results = [ProbeResult("basic", True, "high", "ok", "pong", 123)]
    summary = score_results(results)
    out = tmp_path / "report.md"

    write_markdown_report(out, base_url="https://proxy.example/v1", model="test-model", results=results, summary=summary)

    text = out.read_text(encoding="utf-8")
    assert "LLM Proxy Trust Report" in text
    assert "basic" in text
    assert "LOW" in text

