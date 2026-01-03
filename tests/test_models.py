"""Tests for models module."""

import pytest

from tradestation.models import (
    DownloadConfig,
    StorageFormat,
    get_all_symbols,
    get_symbols_by_category,
    DEFAULT_SYMBOLS,
)


class TestStorageFormat:
    """Tests for StorageFormat enum."""

    def test_values(self):
        assert StorageFormat.SINGLE.value == "single"
        assert StorageFormat.DAILY.value == "daily"
        assert StorageFormat.MONTHLY.value == "monthly"

    def test_from_string(self):
        assert StorageFormat.from_string("single") == StorageFormat.SINGLE
        assert StorageFormat.from_string("DAILY") == StorageFormat.DAILY
        assert StorageFormat.from_string("Monthly") == StorageFormat.MONTHLY

    def test_from_string_invalid(self):
        with pytest.raises(ValueError, match="Invalid storage format"):
            StorageFormat.from_string("invalid")


class TestDownloadConfig:
    """Tests for DownloadConfig dataclass."""

    def test_defaults(self):
        config = DownloadConfig(
            client_id="id",
            client_secret="secret",
            refresh_token="token",
        )
        assert config.data_dir == "./data"
        assert config.storage_format == StorageFormat.SINGLE
        assert config.interval == 1
        assert config.unit == "Minute"

    def test_storage_format_string_conversion(self):
        config = DownloadConfig(
            client_id="id",
            client_secret="secret",
            refresh_token="token",
            storage_format="monthly",
        )
        assert config.storage_format == StorageFormat.MONTHLY


class TestSymbols:
    """Tests for symbol utilities."""

    def test_get_all_symbols(self):
        symbols = get_all_symbols()
        assert len(symbols) > 50
        assert "@ES" in symbols
        assert "@NQ" in symbols

    def test_get_symbols_by_category(self):
        index_symbols = get_symbols_by_category("index")
        assert "@ES" in index_symbols
        assert "@NQ" in index_symbols

    def test_get_symbols_by_category_invalid(self):
        with pytest.raises(ValueError, match="Unknown category"):
            get_symbols_by_category("invalid_category")

    def test_default_symbols_categories(self):
        expected_categories = [
            "index", "micro_index", "energy", "micro_energy",
            "metals", "micro_metals", "treasuries", "grains",
            "softs", "meats", "currencies", "volatility", "crypto",
        ]
        assert set(DEFAULT_SYMBOLS.keys()) == set(expected_categories)
