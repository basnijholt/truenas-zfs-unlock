"""Tests for CLI functionality."""

from pathlib import Path
from unittest.mock import patch

from truenas_unlock import Dataset, filter_datasets, find_config


class TestFilterDatasets:
    """Tests for filter_datasets function."""

    def test_no_filter_returns_all(self) -> None:
        """No filter returns all datasets."""
        datasets = [
            Dataset(path="tank/photos", secret="pass1"),
            Dataset(path="tank/syncthing", secret="pass2"),
        ]
        result = filter_datasets(datasets, None)
        assert result == datasets

    def test_empty_filter_returns_all(self) -> None:
        """Empty filter list returns all datasets."""
        datasets = [
            Dataset(path="tank/photos", secret="pass1"),
            Dataset(path="tank/syncthing", secret="pass2"),
        ]
        result = filter_datasets(datasets, [])
        assert result == datasets

    def test_single_filter_exact_match(self) -> None:
        """Single filter matches exact path."""
        datasets = [
            Dataset(path="tank/photos", secret="pass1"),
            Dataset(path="tank/syncthing", secret="pass2"),
            Dataset(path="tank/frigate", secret="pass3"),
        ]
        result = filter_datasets(datasets, ["tank/photos"])
        assert len(result) == 1
        assert result[0].path == "tank/photos"

    def test_single_filter_partial_match(self) -> None:
        """Single filter matches partial path."""
        datasets = [
            Dataset(path="tank/photos", secret="pass1"),
            Dataset(path="tank/syncthing", secret="pass2"),
            Dataset(path="tank/frigate", secret="pass3"),
        ]
        result = filter_datasets(datasets, ["photos"])
        assert len(result) == 1
        assert result[0].path == "tank/photos"

    def test_multiple_filters(self) -> None:
        """Multiple filters match any."""
        datasets = [
            Dataset(path="tank/photos", secret="pass1"),
            Dataset(path="tank/syncthing", secret="pass2"),
            Dataset(path="tank/frigate", secret="pass3"),
        ]
        result = filter_datasets(datasets, ["photos", "frigate"])
        assert len(result) == 2  # noqa: PLR2004
        assert result[0].path == "tank/photos"
        assert result[1].path == "tank/frigate"

    def test_filter_no_match(self) -> None:
        """Filter with no matches returns empty."""
        datasets = [
            Dataset(path="tank/photos", secret="pass1"),
            Dataset(path="tank/syncthing", secret="pass2"),
        ]
        result = filter_datasets(datasets, ["nonexistent"])
        assert result == []

    def test_filter_pool_name(self) -> None:
        """Filter by pool name matches multiple."""
        datasets = [
            Dataset(path="tank/photos", secret="pass1"),
            Dataset(path="tank/syncthing", secret="pass2"),
            Dataset(path="other/data", secret="pass3"),
        ]
        result = filter_datasets(datasets, ["tank/"])
        assert len(result) == 2  # noqa: PLR2004
        assert all("tank/" in ds.path for ds in result)


class TestFindConfig:
    """Tests for find_config function."""

    def test_finds_config_yaml_in_cwd(self, tmp_path: Path, monkeypatch: object) -> None:
        """Find config.yaml in current directory."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "config.yaml"
        config_file.write_text("host: test")

        # Patch CONFIG_SEARCH_PATHS to use tmp_path
        with patch(
            "truenas_unlock.CONFIG_SEARCH_PATHS",
            [Path("config.yaml"), Path("config.yml")],
        ):
            result = find_config()
            assert result == Path("config.yaml")

    def test_finds_config_yml_in_cwd(self, tmp_path: Path, monkeypatch: object) -> None:
        """Find config.yml in current directory."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "config.yml"
        config_file.write_text("host: test")

        with patch(
            "truenas_unlock.CONFIG_SEARCH_PATHS",
            [Path("config.yaml"), Path("config.yml")],
        ):
            result = find_config()
            assert result == Path("config.yml")

    def test_finds_config_in_home_dir(self, tmp_path: Path) -> None:
        """Find config in ~/.config/truenas-unlock/."""
        config_dir = tmp_path / ".config" / "truenas-unlock"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("host: test")

        with patch(
            "truenas_unlock.CONFIG_SEARCH_PATHS",
            [Path("nonexistent.yaml"), config_file],
        ):
            result = find_config()
            assert result == config_file

    def test_returns_none_when_no_config(self, tmp_path: Path, monkeypatch: object) -> None:
        """Return None when no config file exists."""
        monkeypatch.chdir(tmp_path)

        with patch(
            "truenas_unlock.CONFIG_SEARCH_PATHS",
            [Path("config.yaml"), Path("config.yml")],
        ):
            result = find_config()
            assert result is None

    def test_prefers_first_match(self, tmp_path: Path, monkeypatch: object) -> None:
        """Return first matching config in search order."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "config.yaml").write_text("first")
        (tmp_path / "config.yml").write_text("second")

        with patch(
            "truenas_unlock.CONFIG_SEARCH_PATHS",
            [Path("config.yaml"), Path("config.yml")],
        ):
            result = find_config()
            assert result == Path("config.yaml")
