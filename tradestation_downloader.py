#!/usr/bin/env python3
"""
TradeStation Historical Data Downloader
========================================

Entry point for downloading historical futures data from TradeStation API.

Usage:
    python tradestation_downloader.py                        # Download all symbols
    python tradestation_downloader.py -s "@ES" "@NQ"        # Download specific symbols
    python tradestation_downloader.py --full                 # Full download
    python tradestation_downloader.py --list-symbols         # List available symbols

For more options, run: python tradestation_downloader.py --help

Note: On Windows, quote symbols with @ prefix to avoid shell interpretation.
"""

from tradestation.cli import main_download

if __name__ == "__main__":
    main_download()
