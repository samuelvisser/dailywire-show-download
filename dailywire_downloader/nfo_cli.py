"""
Command-line interface for NFO file creation.

This module provides a command-line interface for creating NFO files,
which is used by yt-dlp's --exec option.
"""

import sys
import logging
from dailywire_downloader.nfo import create_nfo_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the NFO CLI.
    
    Usage: python -m dailywire_downloader.nfo_cli <file_path> <tmp_dir>
    """
    # Check arguments
    if len(sys.argv) != 3:
        logger.error("Usage: python -m dailywire_downloader.nfo_cli <file_path> <tmp_dir>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    tmp_dir = sys.argv[2]
    
    # Create NFO file
    create_nfo_file(file_path, tmp_dir)


if __name__ == "__main__":
    main()