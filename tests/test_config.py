"""Tests for configuration parsing."""

from pathlib import Path
from textwrap import dedent

import pytest

from truenas_zfs_unlock import Config, Dataset


def test_dataset_path() -> None:
    """Test Dataset path parsing."""
    ds = Dataset(path="tank/photos", passphrase_file=Path("/tmp/key"))
    assert ds.pool == "tank"
    assert ds.name == "photos"
    assert ds.path == "tank/photos"


def test_dataset_nested_path() -> None:
    """Test Dataset with nested path."""
    ds = Dataset(path="tank/data/photos", passphrase_file=Path("/tmp/key"))
    assert ds.pool == "tank"
    assert ds.name == "data/photos"


def test_config_from_yaml(tmp_path: Path) -> None:
    """Test Config loading from YAML."""
    config_file = tmp_path / "config.yaml"
    key_file = tmp_path / "api-key"
    ds_key = tmp_path / "ds-key"

    key_file.write_text("test-api-key")
    ds_key.write_text("test-passphrase")

    config_file.write_text(
        dedent(f"""\
        host: 192.168.1.1:443
        api_key_file: {key_file}
        skip_cert_verify: true
        datasets:
          tank/photos: {ds_key}
          tank/docs: {ds_key}
        """)
    )

    config = Config.from_yaml(config_file)

    assert config.host == "192.168.1.1:443"
    assert config.skip_cert_verify is True
    assert config.get_api_key() == "test-api-key"
    assert len(config.datasets) == 2
    assert config.datasets[0].path == "tank/photos"
    assert config.datasets[0].get_passphrase() == "test-passphrase"


def test_config_missing_api_key(tmp_path: Path) -> None:
    """Test error when API key file doesn't exist."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        dedent("""\
        host: 192.168.1.1:443
        api_key_file: /nonexistent/path
        datasets:
          tank/photos: /tmp/key
        """)
    )

    config = Config.from_yaml(config_file)

    with pytest.raises(FileNotFoundError):
        config.get_api_key()
