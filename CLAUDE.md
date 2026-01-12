# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradeStation Historical Data Downloader - A Python library and CLI for downloading 1-minute historical futures data from TradeStation's API and storing it in Parquet format.

**Key Features:**
- OAuth2 authentication with automatic token refresh
- Incremental updates (only download new data)
- Multiple storage formats (single file, daily/monthly Hive-style partitions)
- Rate limiting with exponential backoff

## Project Structure

```
tradestation/
├── __init__.py       # Package exports and version
├── models.py         # StorageFormat enum, DownloadConfig, DEFAULT_SYMBOLS
├── auth.py           # TradeStationAuth - OAuth2 handling
├── auth_setup.py     # Interactive OAuth2 setup wizard
├── storage.py        # StorageBackend ABC + SingleFile/Daily/Monthly implementations
├── downloader.py     # TradeStationDownloader - core download logic
├── config.py         # Configuration loading from YAML
└── cli.py            # Command-line interface

tradestation_downloader.py  # Entry point wrapper
setup_auth.py               # Entry point wrapper
```

## Commands

```bash
# Install (using uv - recommended)
pip install uv
uv sync

# Or standard pip install
pip install -e .

# OAuth2 setup (interactive)
tradestation-auth

# Download data
tradestation-download                         # Incremental update
tradestation-download -s "@ES" "@NQ" "@CL"   # Specific symbols (quote @ on Windows)
tradestation-download --full                  # Full download
tradestation-download --storage-format daily  # Daily partitions
tradestation-download --compression snappy    # Use snappy compression
tradestation-download --list-symbols          # List all symbols
tradestation-download --list-categories       # List symbol categories
tradestation-download --category index        # Download category
```

## Architecture

**Design Patterns:**
- **Strategy Pattern**: `StorageBackend` ABC with `SingleFileStorage`, `DailyPartitionedStorage`, `MonthlyPartitionedStorage` implementations
- **Factory Pattern**: `create_storage()` creates appropriate backend based on `StorageFormat` enum
- **Dependency Injection**: `TradeStationDownloader` receives storage backend, allowing easy testing

**Data Flow:**
```
TradeStation API → TradeStationAuth (OAuth2) → TradeStationDownloader → StorageBackend → Parquet Files
```

## Storage Formats

| Format | Structure | Use Case |
|--------|-----------|----------|
| `single` | `data/ES_1min.parquet` | Simple, small datasets |
| `daily` | `data/ES/year=2024/month=01/day=15/ES.parquet` | Large datasets, date-range queries |
| `monthly` | `data/ES/year_month=2024-01/data-0.parquet` | Balance of simplicity and partitioning |

## Compression

| Algorithm | Description |
|-----------|-------------|
| `zstd` | Best compression ratio, good speed (default) |
| `snappy` | Fast, moderate compression |
| `gzip` | Good compression, slower |
| `lz4` | Fastest, lower compression |
| `none` | No compression |

## Configuration

`config.yaml` contains API credentials and settings. See `config.yaml.template` for structure.

```yaml
tradestation:
  client_id: "..."
  client_secret: "..."
  refresh_token: "..."

storage_format: "single"  # or "daily", "monthly"
compression: "zstd"       # or "snappy", "gzip", "lz4", "none"
data_dir: "./data"
start_date: "2007-01-01"
```

## Key Classes

- `StorageFormat` (Enum): SINGLE, DAILY, MONTHLY
- `Compression` (Enum): ZSTD, SNAPPY, GZIP, LZ4, NONE
- `DownloadConfig` (dataclass): All configuration parameters
- `TradeStationAuth`: OAuth2 token management
- `StorageBackend` (ABC): Abstract storage interface
- `TradeStationDownloader`: Main download orchestrator
