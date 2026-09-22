
import sqlite3
from datetime import datetime

from config import DATABASE_PATH


# ============================================================
# CONNECTION
# ============================================================

def get_connection():
    """Return a connection to the SmartDesk database."""

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():
    """Create all required database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT UNIQUE NOT NULL,
            language TEXT DEFAULT 'text',
            is_pinned INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # RECENT FILES
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recent_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            path TEXT UNIQUE NOT NULL,
            opened_at TEXT NOT NULL,

            FOREIGN KEY(project_id)
                REFERENCES projects(id)
                ON DELETE CASCADE
        )
    """)

    # --------------------------------------------------------
    # NOTES
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # QUIZ RESULTS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_name TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 0,
            completed_at TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # FOCUS SESSIONS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS focus_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            duration_minutes INTEGER NOT NULL,
            completed_at TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stat_name TEXT UNIQUE NOT NULL,
            stat_value INTEGER DEFAULT 0
        )
    """)

    # --------------------------------------------------------
    # SETTINGS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            setting_name TEXT PRIMARY KEY,
            setting_value TEXT
        )
    """)

    # --------------------------------------------------------
    # ACTIVITY
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# PROJECTS
# ============================================================

def save_project(
    name,
    path,
    language="text",
    pinned=False
):
    """Create or update a project."""

    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO projects (
            name,
            path,
            language,
            is_pinned,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(path)
        DO UPDATE SET
            name = excluded.name,
            language = excluded.language,
            is_pinned = excluded.is_pinned,
            updated_at = excluded.updated_at
    """, (
        name,
        path,
        language,
        int(pinned),
        now,
        now
    ))

    connection.commit()
    connection.close()


def get_projects():
    """Return all projects."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM projects
        ORDER BY updated_at DESC
    """)

    projects = cursor.fetchall()

    connection.close()

    return projects


def get_pinned_projects():
    """Return only pinned projects."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM projects
        WHERE is_pinned = 1
        ORDER BY updated_at DESC
    """)

    projects = cursor.fetchall()

    connection.close()

    return projects


def set_project_pinned(path, pinned):
    """Pin or unpin a project."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE projects
        SET is_pinned = ?
        WHERE path = ?
    """, (
        int(pinned),
        path
    ))

    connection.commit()
    connection.close()


# ============================================================
# RECENT FILES
# ============================================================

def add_recent_file(path, project_id=None):
    """Add a file to the recent-files list."""

    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO recent_files (
            project_id,
            path,
            opened_at
        )
        VALUES (?, ?, ?)

        ON CONFLICT(path)
        DO UPDATE SET
            opened_at = excluded.opened_at
    """, (
        project_id,
        path,
        now
    ))

    connection.commit()
    connection.close()


def get_recent_files(limit=10):
    """Return recently opened files."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM recent_files
        ORDER BY opened_at DESC
        LIMIT ?
    """, (limit,))

    files = cursor.fetchall()

    connection.close()

    return files


# ============================================================
# NOTES
# ============================================================

def save_note(title, content, note_id=None):
    """Create a new note or update an existing note."""

    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().isoformat()

    if note_id is None:

        cursor.execute("""
            INSERT INTO notes (
                title,
                content,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            title,
            content,
            now,
            now
        ))

        note_id = cursor.lastrowid

    else:

        cursor.execute("""
            UPDATE notes
            SET
                title = ?,
                content = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            title,
            content,
            now,
            note_id
        ))

    connection.commit()
    connection.close()

    return note_id


def get_notes():
    """Return all notes."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM notes
        ORDER BY updated_at DESC
    """)

    notes = cursor.fetchall()

    connection.close()

    return notes


# ============================================================
# SETTINGS
# ============================================================

def set_setting(name, value):
    """Save an application setting."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO settings (
            setting_name,
            setting_value
        )
        VALUES (?, ?)

        ON CONFLICT(setting_name)
        DO UPDATE SET
            setting_value = excluded.setting_value
    """, (
        name,
        str(value)
    ))

    connection.commit()
    connection.close()


def get_setting(name, default=None):
    """Get an application setting."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT setting_value
        FROM settings
        WHERE setting_name = ?
    """, (name,))

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return default

    return result["setting_value"]


# ============================================================
# STATISTICS
# ============================================================

def increment_stat(stat_name, amount=1):
    """Increase a statistic by a specified amount."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO statistics (
            stat_name,
            stat_value
        )
        VALUES (?, ?)

        ON CONFLICT(stat_name)
        DO UPDATE SET
            stat_value = stat_value + excluded.stat_value
    """, (
        stat_name,
        amount
    ))

    connection.commit()
    connection.close()


def get_stat(stat_name):
    """Return a statistic value."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT stat_value
        FROM statistics
        WHERE stat_name = ?
    """, (stat_name,))

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return 0

    return result["stat_value"]


# ============================================================
# ACTIVITY
# ============================================================

def log_activity(
    activity_type,
    description=""
):
    """Record an activity in SmartDesk."""

    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO activity (
            activity_type,
            description,
            created_at
        )
        VALUES (?, ?, ?)
    """, (
        activity_type,
        description,
        now
    ))

    connection.commit()
    connection.close()


def get_recent_activity(limit=20):
    """Return recent application activity."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM activity
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))

    activities = cursor.fetchall()

    connection.close()

    return activities


# ============================================================
# FOCUS SESSIONS
# ============================================================

def save_focus_session(duration_minutes):
    """Save a completed focus session."""

    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO focus_sessions (
            duration_minutes,
            completed_at
        )
        VALUES (?, ?)
    """, (
        duration_minutes,
        now
    ))

    connection.commit()
    connection.close()

    increment_stat(
        "focus_minutes",
        duration_minutes
    )