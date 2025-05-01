"""
Configuration module for DailyWire Downloader.

This module handles loading and parsing the configuration file.
"""

import os
import yaml
from typing import Dict, List, Any, Optional


def load_config(config_file: str = None) -> Dict[str, Any]:
    """
    Load the configuration from the specified file.
    
    Args:
        config_file: Path to the configuration file. If None, uses the CONFIG_FILE
                     environment variable or defaults to /config/config.yml.
    
    Returns:
        Dict containing the configuration.
    
    Raises:
        FileNotFoundError: If the configuration file doesn't exist.
        ValueError: If the configuration file is invalid.
    """
    if config_file is None:
        config_file = os.environ.get('CONFIG_FILE', '/config/config.yml')
    
    if not os.path.isfile(config_file):
        raise FileNotFoundError(f"Config file not found at {config_file}")
    
    with open(config_file, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
    
    # Validate required fields
    if 'schedule' not in config:
        raise ValueError("'schedule' key missing in config.yml")
    
    if 'output' not in config:
        raise ValueError("'output' key missing in config.yml")
    
    if 'shows' not in config or not config['shows']:
        raise ValueError("No shows defined in config.yml")
    
    for show in config.get('shows', []):
        if not show.get('name') or not show.get('url'):
            raise ValueError("Each show needs 'name' and 'url'")
    
    return config


def get_schedule(config: Dict[str, Any]) -> str:
    """Get the schedule from the configuration."""
    return config.get('schedule', '')


def get_start_date(config: Dict[str, Any]) -> Optional[str]:
    """Get the start date from the configuration."""
    return config.get('start_date', '').strip()


def get_output_template(config: Dict[str, Any]) -> str:
    """Get the output template from the configuration."""
    return config.get('output', '')


def get_shows(config: Dict[str, Any]) -> List[Dict[str, str]]:
    """Get the list of shows from the configuration."""
    return config.get('shows', [])


def get_audio_settings(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get the audio settings from the configuration."""
    return {
        'audio_only': config.get('audio_only', False),
        'audio_format': config.get('audio_format', '')
    }


def get_nfo_settings(config: Dict[str, Any]) -> bool:
    """Get the NFO file settings from the configuration."""
    return config.get('save_nfo_file', False)


def get_retry_settings(config: Dict[str, Any]) -> bool:
    """Get the retry download settings from the configuration."""
    return config.get('retry_download_all', True)