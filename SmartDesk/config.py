
from pathlib import Path


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "SmartDesk"
APP_VERSION = "1.0.0"
APP_AUTHOR = "SmartDesk Team"


# ============================================================
# WINDOW
# ============================================================

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750

MIN_WINDOW_WIDTH = 900
MIN_WINDOW_HEIGHT = 600


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
PROJECTS_DIR = DATA_DIR / "projects"
BACKUPS_DIR = DATA_DIR / "backups"
VAULT_DIR = DATA_DIR / "vault"
TEMP_DIR = DATA_DIR / "temp"

ASSETS_DIR = BASE_DIR / "assets"


# ============================================================
# DATABASE
# ============================================================

DATABASE_PATH = DATA_DIR / "smartdesk.db"


# ============================================================
# ASSETS
# ============================================================

LOGO_PATH = ASSETS_DIR / "logo.png"
ICON_PATH = ASSETS_DIR / "icon.png"


# ============================================================
# APPEARANCE
# ============================================================

DEFAULT_THEME = "dark"

THEMES = {
    "dark": {
        "background": "#0B1020",
        "surface": "#111827",
        "surface_light": "#1E293B",
        "primary": "#2563EB",
        "secondary": "#7C3AED",
        "accent": "#38BDF8",
        "text": "#F8FAFC",
        "text_secondary": "#94A3B8",
        "border": "#334155",
        "success": "#22C55E",
        "warning": "#F59E0B",
        "danger": "#EF4444",
    },

    "light": {
        "background": "#F8FAFC",
        "surface": "#FFFFFF",
        "surface_light": "#E2E8F0",
        "primary": "#2563EB",
        "secondary": "#7C3AED",
        "accent": "#0284C7",
        "text": "#0F172A",
        "text_secondary": "#64748B",
        "border": "#CBD5E1",
        "success": "#16A34A",
        "warning": "#D97706",
        "danger": "#DC2626",
    }
}


# ============================================================
# EDITOR
# ============================================================

DEFAULT_EDITOR_FONT = "Consolas"
DEFAULT_EDITOR_FONT_SIZE = 12

AUTOSAVE_ENABLED = True
AUTOSAVE_INTERVAL = 3000  # milliseconds


# ============================================================
# FOCUS TIMER
# ============================================================

DEFAULT_FOCUS_MINUTES = 25
DEFAULT_SHORT_BREAK_MINUTES = 5
DEFAULT_LONG_BREAK_MINUTES = 15


# ============================================================
# SECURITY
# ============================================================

VAULT_AUTO_LOCK_MINUTES = 10


# ============================================================
# FILE SETTINGS
# ============================================================

SUPPORTED_FILE_TYPES = {
    ".txt": "Text File",
    ".py": "Python File",
    ".md": "Markdown File",
    ".json": "JSON File",
    ".csv": "CSV File",
}


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

def create_directories():
    """Create SmartDesk directories if they don't exist."""

    directories = [
        DATA_DIR,
        PROJECTS_DIR,
        BACKUPS_DIR,
        VAULT_DIR,
        TEMP_DIR,
        ASSETS_DIR,
    ]

    for directory in directories:
        directory.mkdir(
            parents=True,
            exist_ok=True
        )


# Create folders when config.py is loaded.
create_directories()