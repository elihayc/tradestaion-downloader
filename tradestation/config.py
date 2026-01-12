"""
Configuration loading and validation.
"""

from pathlib import Path

import yaml

from .models import Compression, DownloadConfig, StorageFormat, get_all_symbols


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""


def load_config(config_path: str = "config.yaml") -> DownloadConfig:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        DownloadConfig instance

    Raises:
        ConfigurationError: If the config file is missing or invalid
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise ConfigurationError(
            f"Configuration file not found: {config_path}\n"
            "Please create a config.yaml file with your TradeStation API credentials.\n"
            "See config.yaml.template for an example."
        )

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in {config_path}: {e}") from e

    return _parse_config(data)


def _parse_config(data: dict) -> DownloadConfig:
    """Parse configuration dictionary into DownloadConfig."""
    # Validate required fields
    if "tradestation" not in data:
        raise ConfigurationError("Missing 'tradestation' section in config")

    ts_config = data["tradestation"]
    required_fields = ["client_id", "client_secret", "refresh_token"]
    missing = [f for f in required_fields if f not in ts_config]
    if missing:
        raise ConfigurationError(f"Missing required fields in tradestation config: {missing}")

    # Get symbols
    symbols = data.get("symbols", get_all_symbols())
    if not symbols:
        symbols = get_all_symbols()

    # Parse storage format
    storage_format_str = data.get("storage_format", "single")
    try:
        storage_format = StorageFormat.from_string(storage_format_str)
    except ValueError as e:
        raise ConfigurationError(str(e)) from e

    # Parse compression
    compression_str = data.get("compression", "zstd")
    try:
        compression = Compression.from_string(compression_str)
    except ValueError as e:
        raise ConfigurationError(str(e)) from e

    return DownloadConfig(
        client_id=ts_config["client_id"],
        client_secret=ts_config["client_secret"],
        refresh_token=ts_config["refresh_token"],
        data_dir=data.get("data_dir", "./data"),
        start_date=data.get("start_date", "2007-01-01"),
        symbols=symbols,
        interval=data.get("interval", 1),
        unit=data.get("unit", "Minute"),
        max_bars_per_request=data.get("max_bars_per_request", 57600),
        rate_limit_delay=data.get("rate_limit_delay", 0.5),
        max_retries=data.get("max_retries", 3),
        storage_format=storage_format,
        compression=compression,
    )


def create_template_config(output_path: str = "config.yaml.template") -> None:
    """Create a template configuration file."""
    template = """# TradeStation Historical Data Downloader Configuration
# =====================================================
# Copy this file to config.yaml and fill in your credentials

# TradeStation API Credentials
# Get these from: https://developer.tradestation.com/
tradestation:
  client_id: "YOUR_CLIENT_ID"
  client_secret: "YOUR_CLIENT_SECRET"
  refresh_token: "YOUR_REFRESH_TOKEN"

# Data Settings
data_dir: "./data"           # Where to save downloaded data
start_date: "2007-01-01"     # How far back to download
interval: 1                   # Bar interval
unit: "Minute"               # Bar unit: Minute, Daily, Weekly

# Storage Format
# "single"  - One parquet file per symbol (e.g., ES_1min.parquet)
# "daily"   - Hive-style partitioned by day (e.g., ES/year=2024/month=01/day=15/ES.parquet)
# "monthly" - Hive-style partitioned by month (e.g., ES/year_month=2024-01/data-0.parquet)
storage_format: "single"

# Compression Algorithm
# "zstd"   - Best compression ratio, good speed (recommended)
# "snappy" - Fast, moderate compression
# "gzip"   - Good compression, slower
# "lz4"    - Fastest, lower compression
# "none"   - No compression
compression: "zstd"

# Rate Limiting (be careful not to exceed API limits)
rate_limit_delay: 0.5        # Seconds between API requests
max_retries: 3               # Retries on failed requests

# Symbols to Download
# Comment out this section to use all default US futures
# Or specify exactly which symbols you want:
# symbols:
#   - "@ES"     # E-Mini S&P 500
#   - "@NQ"     # E-Mini Nasdaq 100
#   - "@CL"     # Crude Oil
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template)
