"""
NFO file creation module for DailyWire Downloader.

This module handles creating NFO files for downloaded episodes.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def create_nfo_file(file_path: str, tmp_dir: str) -> None:
    """
    Create an NFO file for a downloaded episode.
    
    Args:
        file_path: Path to the downloaded file
        tmp_dir: Path to the temporary directory containing the info.json file
    
    Returns:
        None
    """
    # Extract base name and file name
    base_name = os.path.splitext(file_path)[0]
    file_name = os.path.basename(base_name)
    nfo_file = f"{base_name}.nfo"
    
    # Extract the show name from the base_name
    # The format is expected to be /downloads/show-name/episode-name
    path_parts = base_name.split(os.path.sep)
    if len(path_parts) < 2:
        logger.error(f"Invalid file path format: {base_name}")
        return
    
    show_name = path_parts[-2]
    
    # Construct the JSON file path with the show name directory
    json_file = os.path.join(tmp_dir, show_name, f"{file_name}.info.json")
    
    # Skip if NFO file already exists
    if os.path.exists(nfo_file):
        logger.info(f"NFO file already exists: {nfo_file}")
        return
    
    # Debug information
    logger.info(f"Creating NFO file for: {base_name}")
    logger.info(f"Show name: {show_name}")
    logger.info(f"Temporary directory: {tmp_dir}")
    logger.info(f"JSON file path: {json_file}")
    
    # Check if json file exists
    if not os.path.isfile(json_file):
        logger.error(f"Error: Json file not found at {json_file}")
        return
    
    # Extract metadata from JSON
    metadata = _extract_metadata_from_json(json_file)
    if not metadata:
        return
    
    # Create NFO file
    _write_nfo_file(nfo_file, metadata)
    
    # Remove the info.json file after creating the NFO file
    try:
        os.remove(json_file)
        logger.info(f"Removed info.json file for {os.path.basename(base_name)}")
    except OSError as e:
        logger.error(f"Error removing info.json file: {e}")


def _extract_metadata_from_json(json_file: str) -> Optional[Dict[str, Any]]:
    """
    Extract metadata from the info.json file.
    
    Args:
        json_file: Path to the info.json file
    
    Returns:
        Dictionary containing the extracted metadata, or None if extraction failed
    """
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Extract title and remove "[Member Exclusive]" suffix if present
        title = data.get('title', '')
        if title.endswith(' [Member Exclusive]'):
            title = title[:-19]  # Remove the suffix
        
        # Extract other metadata
        description = data.get('description', 'No description available')
        episode_number = data.get('meta_movement') or data.get('meta_track') or ''
        episode_date = data.get('meta_date', '')
        
        return {
            'title': title,
            'description': description,
            'episode_number': episode_number,
            'episode_date': episode_date
        }
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Error extracting metadata from JSON: {e}")
        return None


def _write_nfo_file(nfo_file: str, metadata: Dict[str, Any]) -> None:
    """
    Write the NFO file with the extracted metadata.
    
    Args:
        nfo_file: Path to the NFO file to create
        metadata: Dictionary containing the metadata to include in the NFO file
    
    Returns:
        None
    """
    try:
        with open(nfo_file, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
            f.write('<episodedetails>\n')
            f.write(f'  <title><![CDATA[{metadata["title"]}]]></title>\n')
            f.write(f'  <plot><![CDATA[{metadata["description"]}]]></plot>\n')
            
            if metadata['episode_number']:
                f.write(f'  <episode>{metadata["episode_number"]}</episode>\n')
            
            if metadata['episode_date']:
                f.write(f'  <aired>{metadata["episode_date"]}</aired>\n')
            
            f.write('</episodedetails>\n')
        
        logger.info(f"Created NFO file: {nfo_file}")
    except OSError as e:
        logger.error(f"Error writing NFO file: {e}")