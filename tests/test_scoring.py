from proxy_auditor.probes import ProbeResult
from proxy_auditor.scoring import score_results


def test_score_low_when_all_probes_pass():
    summary = score_results(
        [
            ProbeResult("a", True, "high", "ok"),
            ProbeResult("b", True, "medium", "ok"),
        ]
    )

    assert summary.level == "LOW"
    assert summary.score == 0


def test_score_high_when_high_severity_fails():
    summary = score_results(
        [
            ProbeResult("a", False, "high", "bad"),
            ProbeResult("b", True, "medium", "ok"),
            ProbeResult("c", False, "medium", "bad"),
        ]
    )

    assert summary.level in {"HIGH", "CRITICAL"}
    assert summary.score == 5

