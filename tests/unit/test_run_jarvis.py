import os
import logging

import pytest

from run_jarvis import configure_logging, load_config, check_prerequisites


def test_configure_logging(tmp_path, caplog):
    # calling twice should be idempotent
    configure_logging(debug=False)
    configure_logging(debug=True)
    # ensure at least one log message about logfile appears
    assert any("logs sendo enviados" in rec.getMessage() for rec in caplog.records)


def test_load_config_json(tmp_path):
    cfg = tmp_path / "cfg.json"
    cfg.write_text('{"TEST_KEY": "value"}', encoding="utf-8")
    # clear env if already set
    os.environ.pop("TEST_KEY", None)
    load_config(str(cfg))
    assert os.environ.get("TEST_KEY") == "value"


def test_load_config_missing(tmp_path, caplog):
    load_config(str(tmp_path / "nope.yaml"))
    assert any("não existe" in rec.getMessage() for rec in caplog.records)


def test_check_prerequisites_runs(caplog):
    # should not raise and may log warnings
    check_prerequisites()
    assert True  # just ensure no exception


def test_argparser_no_text(monkeypatch, caplog):
    # monkeypatch sys.argv to include --no-text
    monkeypatch.setattr("sys.argv", ["run_jarvis.py", "--no-text"])
    # capturing logging output without actually launching agent
    try:
        from run_jarvis import main
        # run main but patch JarvisAgent to avoid side effects
        class Dummy:
            def __init__(self, *args, **kwargs):
                pass
            def run(self):
                pass
        monkeypatch.setattr("run_jarvis.JarvisAgent", Dummy)
        main()
    except SystemExit:
        pass
    # ensure log included 'iniciando Jarvis' and no crash
    assert any("iniciando Jarvis" in r.getMessage() for r in caplog.records)
