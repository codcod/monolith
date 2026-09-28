import logging

from stelo.base import config


def test_setup_app_passes_the_log_level(monkeypatch):
    monkeypatch.setattr(config.uvloop, "install", lambda: None)

    config.setup_app({"db": "x", "log_level": "DEBUG"})

    assert logging.getLogger().getEffectiveLevel() == logging.DEBUG
