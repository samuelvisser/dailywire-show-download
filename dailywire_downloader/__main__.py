"""
Main CLI module for DailyWire Downloader.

This module provides a command-line interface for the package,
allowing users to run the downloader directly without using Docker.
"""

import os
import sys
import argparse
import logging

from dailywire_downloader import config, download, __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def parse_args():
    """
    Parse command-line arguments.
    
    Returns:
        Namespace containing the parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="DailyWire Downloader - Download shows from DailyWire"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"DailyWire Downloader v{__version__}"
    )
    
    parser.add_argument(
        "--config",
        help="Path to the configuration file",
        default=os.environ.get("CONFIG_FILE", "config/config.yml")
    )
    
    parser.add_argument(
        "--cookies",
        help="Path to the cookies file",
        default=os.environ.get("COOKIES_FILE", "config/cookies.txt")
    )
    
    return parser.parse_args()


def main():
    """
    Main entry point for the CLI.
    
    Returns:
        None
    """
    args = parse_args()
    
    # Set environment variables for cookies file
    os.environ["COOKIES_FILE"] = args.cookies
    
    # Run the download
    try:
        download.download_shows(args.config)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()