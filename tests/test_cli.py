"""Tests for CLI functionality."""

from truenas_unlock import Dataset, filter_datasets


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
        assert len(result) == 2
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
        assert len(result) == 2
        assert all("tank/" in ds.path for ds in result)
