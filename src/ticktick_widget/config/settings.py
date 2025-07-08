"""
Configuration settings for TickTick Widget.
"""

import os
from pathlib import Path
from typing import Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# File paths
TASKS_JSON_PATH = DATA_DIR / "allActiveTasks.json"

# API Configuration
API_REFRESH_INTERVAL = 300  # 5 minutes in seconds
API_TIMEOUT = 30  # seconds

# GUI Configuration
WIDGET_WIDTH = 400
WIDGET_HEIGHT = 600
WIDGET_TITLE = "TickTick Tasks"

# Widget behavior
ALWAYS_ON_TOP = True
START_MINIMIZED = False
SHOW_SYSTEM_TRAY = True

# Notification settings
ENABLE_NOTIFICATIONS = True
NOTIFICATION_LEAD_TIME = 15  # minutes before due time

def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable with optional default."""
    return os.getenv(key, default)

def get_data_file_path(filename: str) -> Path:
    """Get path to a file in the data directory."""
    return DATA_DIR / filename

def get_asset_path(filename: str) -> Path:
    """Get path to a file in the assets directory."""
    return ASSETS_DIR / filename 