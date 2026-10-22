# ============================================================
# SmartDesk - Configuration
# ============================================================

from pathlib import Path


# ============================================================
# MAIN DIRECTORIES
# ============================================================

# Folder containing this config.py file
APP_DIR = Path(__file__).resolve().parent

# Main data directory
DATA_DIR = APP_DIR / "data"

# Projects created by SmartDesk
PROJECTS_DIR = DATA_DIR / "projects"

# Files saved by SmartDesk
FILES_DIR = DATA_DIR / "files"

# User assets
ASSETS_DIR = DATA_DIR / "assets"

# Logs
LOGS_DIR = DATA_DIR / "logs"

# Vault and saved private content
VAULT_DIR = DATA_DIR / "vault"

# Backup storage
BACKUPS_DIR = DATA_DIR / "backups"

# Temporary working files
TEMP_DIR = DATA_DIR / "temp"

# Cloud sync cache
CLOUD_DIR = DATA_DIR / "cloud"

# Database
DB_PATH = DATA_DIR / "smartdesk.db"


# ============================================================
# CREATE DIRECTORIES
# ============================================================


def create_directories():
    """Ensure SmartDesk's on-disk folders exist."""
    for path in (
        DATA_DIR,
        PROJECTS_DIR,
        FILES_DIR,
        ASSETS_DIR,
        LOGS_DIR,
        VAULT_DIR,
        BACKUPS_DIR,
        TEMP_DIR,
        CLOUD_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
    return {
        "data": DATA_DIR,
        "projects": PROJECTS_DIR,
        "files": FILES_DIR,
        "assets": ASSETS_DIR,
        "logs": LOGS_DIR,
        "vault": VAULT_DIR,
        "backups": BACKUPS_DIR,
        "temp": TEMP_DIR,
        "cloud": CLOUD_DIR,
    }


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "SmartDesk"
APP_VERSION = "1.0.0"

DEBUG = True

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
MIN_WINDOW_WIDTH = 1100
MIN_WINDOW_HEIGHT = 700

ICON_PATH = APP_DIR / "assets" / "icon.png"
LOGO_PATH = APP_DIR / "assets" / "logo.png"


# ============================================================
# DATABASE
# ============================================================

DATABASE_TIMEOUT = 30


# ============================================================
# SECURITY
# ============================================================

SESSION_TIMEOUT = 60 * 60


# ============================================================
# DEFAULT ADMIN
# ============================================================

DEFAULT_ADMIN_USERNAME = "davereub"
DEFAULT_ADMIN_PASSWORD = "98709870!@"


# ============================================================
# FOCUS SETTINGS
# ============================================================

DEFAULT_FOCUS_MINUTES = 25
DEFAULT_SHORT_BREAK_MINUTES = 5
DEFAULT_LONG_BREAK_MINUTES = 15


# ============================================================
# SETTINGS / THEMES
# ============================================================

DEFAULT_THEME = "dark"
THEMES = {
    "dark": "dark",
    "light": "light",
}
AUTOSAVE_ENABLED = True


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================
# These aliases prevent older SmartDesk files from breaking
# if they use different names for the same directories.

ROOT_DIR = APP_DIR
BASE_DIR = APP_DIR

PROJECT_DIR = PROJECTS_DIR
PROJECTS_PATH = PROJECTS_DIR

FILES_PATH = FILES_DIR
ASSETS_PATH = ASSETS_DIR

DATABASE_PATH = DB_PATH

# Legacy names some screens expect to exist.
BACKUP_DIR = BACKUPS_DIR
CLOUD_PATH = CLOUD_DIR


# ============================================================
# END
# ============================================================