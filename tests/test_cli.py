from proxy_auditor.cli import _should_fail, main


def test_list_probes(capsys):
    code = main(["list-probes"])

    assert code == 0
    assert "basic_connectivity" in capsys.readouterr().out


def test_should_fail_respects_threshold():
    assert _should_fail("HIGH", "high")
    assert _should_fail("CRITICAL", "high")
    assert not _should_fail("MEDIUM", "high")
    assert not _should_fail("CRITICAL", "never")
