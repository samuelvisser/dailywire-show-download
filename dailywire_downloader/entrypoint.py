"""
Entrypoint module for DailyWire Downloader.

This module provides the main entry point for the application,
which sets up the cron job and runs the initial download.
"""

import os
import sys
import logging
import subprocess
from datetime import datetime

from dailywire_downloader import config, download

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# Constants
CONFIG_FILE = os.environ.get('CONFIG_FILE', '/config/config.yml')
CRON_TMPL = "/etc/cron.d/dailywire.cron.template"
CRON_FILE = "/etc/cron.d/dailywire.cron"


def setup_cron():
    """
    Set up the cron job based on the schedule in the configuration.
    
    Returns:
        None
    """
    # Sanity check
    if not os.path.isfile(CONFIG_FILE):
        logger.error(f"ERROR: Config file not found at {CONFIG_FILE}")
        sys.exit(1)
    
    # Load configuration
    cfg = config.load_config(CONFIG_FILE)
    
    # Get schedule
    schedule = config.get_schedule(cfg)
    if not schedule:
        logger.error("ERROR: 'schedule' key missing or empty in config.yml")
        sys.exit(1)
    
    # Replace placeholder in template
    try:
        with open(CRON_TMPL, 'r') as f:
            template = f.read()
        
        cron_content = template.replace('{{schedule}}', schedule)
        
        with open(CRON_FILE, 'w') as f:
            f.write(cron_content)
            f.write('\n')
        
        # Set permissions
        os.chmod(CRON_FILE, 0o644)
        
        # Install cron job
        subprocess.run(['crontab', CRON_FILE], check=True)
        
        logger.info(f"Cron job installed with schedule: {schedule}")
    
    except (OSError, subprocess.CalledProcessError) as e:
        logger.error(f"Error setting up cron job: {e}")
        sys.exit(1)


def run_initial_download():
    """
    Run an initial download on startup.
    
    Returns:
        None
    """
    logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Initial download on startup")
    download.download_shows(CONFIG_FILE)


def main():
    """
    Main entry point for the application.
    
    Returns:
        None
    """
    # Set up cron job
    setup_cron()
    
    # Run initial download
    run_initial_download()
    
    # Start tailing the cron log in the background
    subprocess.Popen(['tail', '-f', '/var/log/cron.log'])
    
    # Hand off to CMD (i.e. cron -f)
    os.execvp(sys.argv[1], sys.argv[1:])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python -m dailywire_downloader.entrypoint <command> [args...]")
        sys.exit(1)
    
    main()