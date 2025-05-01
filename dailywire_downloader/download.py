"""
Download module for DailyWire Downloader.

This module handles downloading episodes from DailyWire.
"""

import os
import logging
import subprocess
import fcntl
import time
from typing import Dict, List, Any, Optional, Tuple

from dailywire_downloader import config

logger = logging.getLogger(__name__)

# Constants
DOWNLOAD_DIR = "/downloads"
TMP_DIR = "/tmp/yt-dlp-tmp"
ARCHIVE_FILE = os.path.join(DOWNLOAD_DIR, "downloaded.txt")
COOKIES_FILE = os.environ.get('COOKIES_FILE', '/config/cookies.txt')
LOCKFILE = "/tmp/download.lock"


def download_shows(config_file: str = None) -> None:
    """
    Download shows from DailyWire based on the configuration.
    
    Args:
        config_file: Path to the configuration file. If None, uses the CONFIG_FILE
                     environment variable or defaults to /config/config.yml.
    
    Returns:
        None
    """
    # Prevent overlapping runs using file locking
    if not _acquire_lock():
        logger.info("Another download process is still running; exiting.")
        return
    
    try:
        # Set umask to make all new dirs 777 and new files 666 by default
        os.umask(0)
        
        # Verify prerequisites
        if not _verify_prerequisites():
            return
        
        # Load configuration
        cfg = config.load_config(config_file)
        
        # Get date filter
        date_filter = _get_date_filter(cfg)
        
        # Get output template
        output_template = config.get_output_template(cfg)
        
        # Get audio settings
        audio_settings = config.get_audio_settings(cfg)
        audio_flags = _get_audio_flags(audio_settings)
        
        # Get NFO settings
        save_nfo = config.get_nfo_settings(cfg)
        nfo_flags = _get_nfo_flags(save_nfo)
        
        # Get retry settings
        retry_download_all = config.get_retry_settings(cfg)
        retry_flags = _get_retry_flags(retry_download_all)
        
        # Iterate through shows and download
        shows = config.get_shows(cfg)
        for show in shows:
            _download_show(show, output_template, date_filter, audio_flags, nfo_flags, retry_flags)
    
    finally:
        # Release the lock
        _release_lock()


def _acquire_lock() -> bool:
    """
    Acquire a lock to prevent overlapping runs.
    
    Returns:
        True if the lock was acquired, False otherwise.
    """
    try:
        # Open the lock file
        global lock_fd
        lock_fd = open(LOCKFILE, 'w')
        
        # Try to acquire an exclusive lock (non-blocking)
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        
        return True
    except IOError:
        # Another process already has the lock
        if 'lock_fd' in globals():
            lock_fd.close()
        return False


def _release_lock() -> None:
    """Release the lock."""
    if 'lock_fd' in globals():
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


def _verify_prerequisites() -> bool:
    """
    Verify that all prerequisites are met.
    
    Returns:
        True if all prerequisites are met, False otherwise.
    """
    # Create necessary directories
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(TMP_DIR, exist_ok=True)
    
    # Create archive file if it doesn't exist
    if not os.path.exists(ARCHIVE_FILE):
        open(ARCHIVE_FILE, 'a').close()
    
    # Check for cookies file
    if not os.path.isfile(COOKIES_FILE):
        logger.error(f"ERROR: Cookies file missing at {COOKIES_FILE}")
        return False
    
    return True


def _get_date_filter(cfg: Dict[str, Any]) -> List[str]:
    """
    Get the date filter arguments for yt-dlp.
    
    Args:
        cfg: Configuration dictionary
    
    Returns:
        List of date filter arguments
    """
    start_date = config.get_start_date(cfg)
    if not start_date:
        return []
    
    # Clean the date by removing hyphens
    clean_date = start_date.replace('-', '')
    
    # Return the date filter arguments
    return ["--dateafter", clean_date, "--break-match-filters", f"upload_date>={clean_date}"]


def _get_audio_flags(audio_settings: Dict[str, Any]) -> List[str]:
    """
    Get the audio flags for yt-dlp.
    
    Args:
        audio_settings: Audio settings dictionary
    
    Returns:
        List of audio flags
    """
    audio_only = audio_settings.get('audio_only', False)
    audio_format = audio_settings.get('audio_format', '')
    
    if not audio_only:
        return []
    
    flags = ["-x"]
    if audio_format:
        flags.extend(["--audio-format", audio_format])
    
    return flags


def _get_nfo_flags(save_nfo: bool) -> Tuple[List[str], List[str]]:
    """
    Get the NFO flags for yt-dlp.
    
    Args:
        save_nfo: Whether to save NFO files
    
    Returns:
        Tuple of (info_flags, exec_flags)
    """
    if not save_nfo:
        return [], []
    
    info_flags = ["--write-info-json", "--paths", f"infojson:{TMP_DIR}"]
    
    # Use our Python module for NFO creation
    exec_flags = ["--exec", f"python -m dailywire_downloader.nfo_cli %(filepath)q {TMP_DIR}"]
    
    return info_flags, exec_flags


def _get_retry_flags(retry_download_all: bool) -> List[str]:
    """
    Get the retry flags for yt-dlp.
    
    Args:
        retry_download_all: Whether to retry downloading all episodes
    
    Returns:
        List of retry flags
    """
    if retry_download_all:
        return ["--sleep-requests", "0.75"]
    else:
        return ["--break-on-existing"]


def _download_show(show: Dict[str, str], output_template: str, date_filter: List[str],
                  audio_flags: List[str], nfo_flags: Tuple[List[str], List[str]],
                  retry_flags: List[str]) -> None:
    """
    Download a single show.
    
    Args:
        show: Show dictionary with 'name' and 'url' keys
        output_template: Output template for yt-dlp
        date_filter: Date filter arguments
        audio_flags: Audio flags
        nfo_flags: NFO flags (info_flags, exec_flags)
        retry_flags: Retry flags
    
    Returns:
        None
    """
    show_name = show.get('name', '')
    show_url = show.get('url', '')
    
    if not show_name or not show_url:
        logger.error("Show missing name or URL")
        return
    
    logger.info(f"Downloading '{show_name}' from {show_url}")
    
    # Build the yt-dlp command
    cmd = [
        "yt-dlp",
        "--cookies", COOKIES_FILE,
        "--download-archive", ARCHIVE_FILE,
    ]
    
    # Add date filter
    cmd.extend(date_filter)
    
    # Add audio flags
    cmd.extend(audio_flags)
    
    # Add NFO flags
    info_flags, exec_flags = nfo_flags
    cmd.extend(info_flags)
    cmd.extend(exec_flags)
    
    # Add retry flags
    cmd.extend(retry_flags)
    
    # Add paths and other options
    cmd.extend([
        "--paths", f"temp:{TMP_DIR}",
        "--paths", f"home:{DOWNLOAD_DIR}",
        "--cache-dir", "/app/cache",
        "--no-part",
        "--windows-filenames",
        "--embed-metadata",
        "--parse-metadata", "description:(?s)(?P<meta_comment>.+)",
        "--parse-metadata", "title:(?P<meta_title>.+?)(?:\\s+\\[Member Exclusive\\])?$",
        "--parse-metadata", "title:(?:Ep\\.\\s+(?P<meta_movement>\\d+))?.*",
        "--parse-metadata", "title:(?:Ep\\.\\s+(?P<meta_track>\\d+))?.*",
        "--parse-metadata", "playlist_title:(?P<meta_album>.+)",
        "--parse-metadata", "playlist_title:(?P<meta_series>.+)",
        "--parse-metadata", "upload_date:(?P<meta_date>\\d{8})$",
        "--replace-in-metadata", "meta_date", "(.{4})(.{2})(.{2})", "\\1-\\2-\\3",
        "--parse-metadata", "upload_date:(?P<meta_year>.{4}).*",
        "--min-sleep-interval", "10",
        "--max-sleep-interval", "25",
        "--convert-thumbnails", "jpg",
        "--embed-thumbnail",
        "--match-title", "\\[Member Exclusive\\]",
        "-o", f"{show_name}/{output_template}",
        show_url
    ])
    
    # Run the command
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error downloading show '{show_name}': {e}")