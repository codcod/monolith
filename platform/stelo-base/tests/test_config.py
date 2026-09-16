import logging

from stelo.base.config import read_config, setup_logging


def test_read_config_parses_toml(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text('[inbox]\ndb = "x"\nlog_level = "DEBUG"\n')

    config = read_config(str(config_file))

    assert config == {"inbox": {"db": "x", "log_level": "DEBUG"}}


def test_setup_logging_accepts_level_name():
    setup_logging({"log_level": "DEBUG"})

    assert logging.getLogger().getEffectiveLevel() == logging.DEBUG
