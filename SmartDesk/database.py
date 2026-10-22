import sqlite3
import time
import uuid
from datetime import datetime
from pathlib import Path

import config


# ============================================================
# DATABASE PATH
# ============================================================

if hasattr(config, "DB_PATH"):
    DB_PATH = Path(config.DB_PATH)

elif hasattr(config, "DATABASE_PATH"):
    DB_PATH = Path(config.DATABASE_PATH)

else:
    DB_PATH = (
        Path(__file__).resolve().parent
        / "data"
        / "smartdesk.db"
    )

DB_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONNECTION
# ============================================================

def get_connection():
    conn = sqlite3.connect(
        str(DB_PATH),
        timeout=15,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    try:
        conn.execute(
            "PRAGMA busy_timeout = 15000"
        )
    except Exception:
        pass

    try:
        conn.execute(
            "PRAGMA journal_mode = WAL"
        )
    except Exception:
        pass

    try:
        conn.execute(
            "PRAGMA synchronous = NORMAL"
        )
    except Exception:
        pass

    return conn


def close_connection(conn):
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass


def safe_commit(conn, attempts=5):

    for attempt in range(attempts):

        try:
            conn.commit()
            return

        except sqlite3.OperationalError as error:

            if "locked" not in str(error).lower():
                raise

            time.sleep(
                0.15 * (attempt + 1)
            )

    conn.commit()


# ============================================================
# DATABASE HELPERS
# ============================================================

def table_exists(conn, table_name):

    row = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = ?
        """,
        (table_name,)
    ).fetchone()

    return row is not None


def get_columns(conn, table_name):

    rows = conn.execute(
        f'PRAGMA table_info("{table_name}")'
    ).fetchall()

    return [
        row["name"]
        for row in rows
    ]


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():

    conn = get_connection()

    try:

        cursor = conn.cursor()

        # ====================================================
        # USERS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                verified INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)

        # ====================================================
        # PROJECTS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT UNIQUE NOT NULL,
                content TEXT DEFAULT '',
                language TEXT DEFAULT 'text',
                pinned INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # ====================================================
        # RECENT FILES
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recent_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                opened_at TEXT
            )
        """)

        # ====================================================
        # NOTES
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT DEFAULT '',
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # ====================================================
        # QUIZ RESULTS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER DEFAULT 0,
                total INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)

        # ====================================================
        # FOCUS SESSIONS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                minutes INTEGER DEFAULT 0,
                session_type TEXT DEFAULT 'focus',
                created_at TEXT
            )
        """)

        # ====================================================
        # SETTINGS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # ====================================================
        # ACTIVITY
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                details TEXT,
                created_at TEXT
            )
        """)

        # ====================================================
        # STATISTICS
        # ====================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value INTEGER DEFAULT 0
            )
        """)

        safe_commit(conn)

        # Repair older SmartDesk databases.
        repair_users_table(conn)
        repair_projects_table(conn)

        safe_commit(conn)

    finally:

        close_connection(conn)


# ============================================================
# REPAIR USERS TABLE
# ============================================================

def repair_users_table(conn):

    if not table_exists(
        conn,
        "users"
    ):
        return

    columns = get_columns(
        conn,
        "users"
    )

    if "role" not in columns:

        conn.execute("""
            ALTER TABLE users
            ADD COLUMN role TEXT DEFAULT 'user'
        """)

    if "verified" not in columns:

        conn.execute("""
            ALTER TABLE users
            ADD COLUMN verified INTEGER DEFAULT 0
        """)

    if "created_at" not in columns:

        conn.execute("""
            ALTER TABLE users
            ADD COLUMN created_at TEXT
        """)

        conn.execute("""
            UPDATE users
            SET created_at = ?
            WHERE created_at IS NULL
        """, (
            datetime.now().isoformat(),
        ))


# ============================================================
# REPAIR PROJECTS TABLE
# ============================================================

def repair_projects_table(conn):

    if not table_exists(
        conn,
        "projects"
    ):
        return

    columns = get_columns(
        conn,
        "projects"
    )

    # --------------------------------------------------------
    # Add missing columns.
    # --------------------------------------------------------

    if "content" not in columns:

        conn.execute("""
            ALTER TABLE projects
            ADD COLUMN content TEXT DEFAULT ''
        """)

    if "language" not in columns:

        conn.execute("""
            ALTER TABLE projects
            ADD COLUMN language TEXT DEFAULT 'text'
        """)

    if "pinned" not in columns:

        conn.execute("""
            ALTER TABLE projects
            ADD COLUMN pinned INTEGER DEFAULT 0
        """)

    if "created_at" not in columns:

        conn.execute("""
            ALTER TABLE projects
            ADD COLUMN created_at TEXT
        """)

    if "updated_at" not in columns:

        conn.execute("""
            ALTER TABLE projects
            ADD COLUMN updated_at TEXT
        """)

    # --------------------------------------------------------
    # Repair old projects with empty/NULL paths.
    # --------------------------------------------------------

    if "path" in columns:

        rows = conn.execute("""
            SELECT id
            FROM projects
            WHERE path IS NULL
               OR path = ''
        """).fetchall()

        for row in rows:

            internal_path = (
                "smartdesk://project/"
                + uuid.uuid4().hex
            )

            conn.execute("""
                UPDATE projects
                SET path = ?
                WHERE id = ?
            """, (
                internal_path,
                row["id"]
            ))

    # --------------------------------------------------------
    # Repair missing dates.
    # --------------------------------------------------------

    now = datetime.now().isoformat()

    conn.execute("""
        UPDATE projects
        SET created_at = ?
        WHERE created_at IS NULL
           OR created_at = ''
    """, (
        now,
    ))

    conn.execute("""
        UPDATE projects
        SET updated_at = ?
        WHERE updated_at IS NULL
           OR updated_at = ''
    """, (
        now,
    ))


# ============================================================
# INTERNAL SMARTDESK PROJECT PATH
# ============================================================

def create_internal_project_path():

    return (
        "smartdesk://project/"
        + uuid.uuid4().hex
    )


# ============================================================
# PROJECTS
# ============================================================

def save_project(
    name,
    path=None,
    content="",
    language="text",
    pinned=None
):

    conn = get_connection()

    try:

        # ----------------------------------------------------
        # NEVER allow NULL/empty path.
        # ----------------------------------------------------

        if path is None:
            path = create_internal_project_path()

        path = str(path).strip()

        if not path:
            path = create_internal_project_path()

        # ----------------------------------------------------
        # Clean values.
        # ----------------------------------------------------

        name = (
            str(name).strip()
            if name
            else "Untitled"
        )

        content = (
            content
            if content is not None
            else ""
        )

        language = (
            str(language)
            if language
            else "text"
        )

        now = datetime.now().isoformat()

        # ----------------------------------------------------
        # Find existing project.
        # ----------------------------------------------------

        existing = conn.execute("""
            SELECT id, pinned
            FROM projects
            WHERE path = ?
        """, (
            path,
        )).fetchone()

        # ----------------------------------------------------
        # UPDATE
        # ----------------------------------------------------

        if existing:

            if pinned is None:
                pinned = existing["pinned"]

            conn.execute("""
                UPDATE projects
                SET
                    name = ?,
                    content = ?,
                    language = ?,
                    pinned = ?,
                    updated_at = ?
                WHERE path = ?
            """, (
                name,
                content,
                language,
                int(bool(pinned)),
                now,
                path
            ))

            project_id = existing["id"]

        # ----------------------------------------------------
        # INSERT
        # ----------------------------------------------------

        else:

            if pinned is None:
                pinned = 0

            cursor = conn.execute("""
                INSERT INTO projects
                (
                    name,
                    path,
                    content,
                    language,
                    pinned,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                path,
                content,
                language,
                int(bool(pinned)),
                now,
                now
            ))

            project_id = cursor.lastrowid

        safe_commit(conn)

        return project_id

    except Exception:

        try:
            conn.rollback()
        except Exception:
            pass

        raise

    finally:

        close_connection(conn)


def get_project(
    project_id
):

    conn = get_connection()

    try:

        return conn.execute("""
            SELECT *
            FROM projects
            WHERE id = ?
        """, (
            project_id,
        )).fetchone()

    finally:

        close_connection(conn)


def get_project_by_path(
    path
):

    conn = get_connection()

    try:

        return conn.execute("""
            SELECT *
            FROM projects
            WHERE path = ?
        """, (
            path,
        )).fetchone()

    finally:

        close_connection(conn)


def get_projects():

    conn = get_connection()

    try:

        return conn.execute("""
            SELECT *
            FROM projects
            ORDER BY
                pinned DESC,
                updated_at DESC
        """).fetchall()

    finally:

        close_connection(conn)


def get_pinned_projects():

    conn = get_connection()

    try:

        return conn.execute("""
            SELECT *
            FROM projects
            WHERE pinned = 1
            ORDER BY updated_at DESC
        """).fetchall()

    finally:

        close_connection(conn)


def set_project_pinned(
    project_id,
    pinned=True
):

    conn = get_connection()

    try:

        conn.execute("""
            UPDATE projects
            SET
                pinned = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            1 if pinned else 0,
            datetime.now().isoformat(),
            project_id
        ))

        safe_commit(conn)

    finally:

        close_connection(conn)


def delete_project(
    project_id
):

    conn = get_connection()

    try:

        conn.execute("""
            DELETE FROM projects
            WHERE id = ?
        """, (
            project_id,
        ))

        safe_commit(conn)

    finally:

        close_connection(conn)


# ============================================================
# RECENT FILES
# ============================================================

def add_recent_file(
    path
):

    conn = get_connection()

    try:

        now = datetime.now().isoformat()

        existing = conn.execute("""
            SELECT id
            FROM recent_files
            WHERE path = ?
        """, (
            path,
        )).fetchone()

        if existing:

            conn.execute("""
                UPDATE recent_files
                SET opened_at = ?
                WHERE path = ?
            """, (
                now,
                path
            ))

        else:

            conn.execute("""
                INSERT INTO recent_files
                (
                    path,
                    opened_at
                )
                VALUES (?, ?)
            """, (
                path,
                now
            ))

        safe_commit(conn)

    finally:

        close_connection(conn)


def get_recent_files(
    limit=10
):

    conn = get_connection()

    try:

        return conn.execute("""
            SELECT *
            FROM recent_files
            ORDER BY opened_at DESC
            LIMIT ?
        """, (
            int(limit),
        )).fetchall()

    finally:

        close_connection(conn)


# ============================================================
# NOTES
# ============================================================

def save_note(
    title,
    content,
    note_id=None
):
    """
    Create or update a SmartDesk note.
    """

    conn = get_connection()

    try:

        now = datetime.now().isoformat()

        title = (
            str(title).strip()
            if title
            else "Untitled Note"
        )

        content = (
            content
            if content is not None
            else ""
        )

        # ----------------------------------------------------
        # UPDATE
        # ----------------------------------------------------

        if note_id is not None:

            conn.execute("""
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

            saved_id = note_id

        # ----------------------------------------------------
        # INSERT
        # ----------------------------------------------------

        else:

            cursor = conn.execute("""
                INSERT INTO notes
                (
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

            saved_id = cursor.lastrowid

        safe_commit(conn)

        return saved_id

    except Exception:

        try:
            conn.rollback()
        except Exception:
            pass

        raise

    finally:

        close_connection(conn)


def get_notes():

    """
    Return all notes.
    """

    conn = get_connection()

    try:

        return conn.execute("""
            SELECT *
            FROM notes
            ORDER BY
                updated_at DESC,
                id DESC
        """).fetchall()

    finally:

        close_connection(conn)


def get_note(
    note_id
):

    conn = get_connection()

    try:

        return conn.execute("""
            SELECT *
            FROM notes
            WHERE id = ?
        """, (
            note_id,
        )).fetchone()

    finally:

        close_connection(conn)


def delete_note(
    note_id
):

    conn = get_connection()

    try:

        conn.execute("""
            DELETE FROM notes
            WHERE id = ?
        """, (
            note_id,
        ))

        safe_commit(conn)

    finally:

        close_connection(conn)


def search_notes(
    search_text
):

    conn = get_connection()

    try:

        search_text = (
            str(search_text)
            if search_text
            else ""
        )

        search = f"%{search_text}%"

        return conn.execute("""
            SELECT *
            FROM notes
            WHERE title LIKE ?
               OR content LIKE ?
            ORDER BY updated_at DESC
        """, (
            search,
            search
        )).fetchall()

    finally:

        close_connection(conn)


# ============================================================
# SETTINGS
# ============================================================

def set_setting(
    key,
    value
):

    conn = get_connection()

    try:

        existing = conn.execute("""
            SELECT key
            FROM settings
            WHERE key = ?
        """, (
            key,
        )).fetchone()

        if existing:

            conn.execute("""
                UPDATE settings
                SET value = ?
                WHERE key = ?
            """, (
                str(value),
                key
            ))

        else:

            conn.execute("""
                INSERT INTO settings
                (
                    key,
                    value
                )
                VALUES (?, ?)
            """, (
                key,
                str(value)
            ))

        safe_commit(conn)

    finally:

        close_connection(conn)


def get_setting(
    key,
    default=None
):

    conn = get_connection()

    try:

        row = conn.execute("""
            SELECT value
            FROM settings
            WHERE key = ?
        """, (
            key,
        )).fetchone()

        if row is None:
            return default

        return row["value"]

    finally:

        close_connection(conn)


# ============================================================
# STATISTICS
# ============================================================

def increment_stat(
    key,
    amount=1
):

    conn = get_connection()

    try:

        row = conn.execute("""
            SELECT value
            FROM statistics
            WHERE key = ?
        """, (
            key,
        )).fetchone()

        if row:

            current = int(
                row["value"] or 0
            )

            conn.execute("""
                UPDATE statistics
                SET value = ?
                WHERE key = ?
            """, (
                current + int(amount),
                key
            ))

        else:

            conn.execute("""
                INSERT INTO statistics
                (
                    key,
                    value
                )
                VALUES (?, ?)
            """, (
                key,
                int(amount)
            ))

        safe_commit(conn)

        # Return the new value.
        row = conn.execute("""
            SELECT value
            FROM statistics
            WHERE key = ?
        """, (
            key,
        )).fetchone()

        return (
            int(row["value"])
            if row
            else int(amount)
        )

    finally:

        close_connection(conn)


def get_stat(
    key,
    default=0
):

    conn = get_connection()

    try:

        row = conn.execute("""
            SELECT value
            FROM statistics
            WHERE key = ?
        """, (
            key,
        )).fetchone()

        if row is None:
            return default

        try:
            return int(row["value"])
        except Exception:
            return default

    finally:

        close_connection(conn)


# ============================================================
# ACTIVITY
# ============================================================

def log_activity(
    action,
    details=""
):

    conn = get_connection()

    try:

        conn.execute("""
            INSERT INTO activity
            (
                action,
                details,
                created_at
            )
            VALUES (?, ?, ?)
        """, (
            action,
            details,
            datetime.now().isoformat()
        ))

        safe_commit(conn)

    finally:

        close_connection(conn)


def get_recent_activity(
    limit=10
):

    conn = get_connection()

    try:

        return conn.execute("""
            SELECT *
            FROM activity
            ORDER BY created_at DESC
            LIMIT ?
        """, (
            int(limit),
        )).fetchall()

    finally:

        close_connection(conn)


# ============================================================
# FOCUS
# ============================================================

def save_focus_session(
    minutes,
    session_type="focus"
):

    conn = get_connection()

    try:

        minutes = int(minutes)

        conn.execute("""
            INSERT INTO focus_sessions
            (
                minutes,
                session_type,
                created_at
            )
            VALUES (?, ?, ?)
        """, (
            minutes,
            session_type,
            datetime.now().isoformat()
        ))

        # Update total focus minutes.
        row = conn.execute("""
            SELECT value
            FROM statistics
            WHERE key = 'focus_minutes'
        """).fetchone()

        if row:

            current = int(
                row["value"] or 0
            )

            conn.execute("""
                UPDATE statistics
                SET value = ?
                WHERE key = 'focus_minutes'
            """, (
                current + minutes,
            ))

        else:

            conn.execute("""
                INSERT INTO statistics
                (
                    key,
                    value
                )
                VALUES (?, ?)
            """, (
                "focus_minutes",
                minutes
            ))

        safe_commit(conn)

    finally:

        close_connection(conn)


def get_focus_sessions(
    limit=20
):

    conn = get_connection()

    try:

        return conn.execute("""
            SELECT *
            FROM focus_sessions
            ORDER BY created_at DESC
            LIMIT ?
        """, (
            int(limit),
        )).fetchall()

    finally:

        close_connection(conn)


# ============================================================
# QUIZ
# ============================================================

def save_quiz_result(
    score,
    total
):

    conn = get_connection()

    try:

        score = int(score)
        total = int(total)

        conn.execute("""
            INSERT INTO quiz_results
            (
                score,
                total,
                created_at
            )
            VALUES (?, ?, ?)
        """, (
            score,
            total,
            datetime.now().isoformat()
        ))

        # ----------------------------------------------------
        # Count quiz attempts.
        # ----------------------------------------------------

        row = conn.execute("""
            SELECT value
            FROM statistics
            WHERE key = 'quiz_attempts'
        """).fetchone()

        if row:

            current = int(
                row["value"] or 0
            )

            conn.execute("""
                UPDATE statistics
                SET value = ?
                WHERE key = 'quiz_attempts'
            """, (
                current + 1,
            ))

        else:

            conn.execute("""
                INSERT INTO statistics
                (
                    key,
                    value
                )
                VALUES (?, ?)
            """, (
                "quiz_attempts",
                1
            ))

        safe_commit(conn)

    finally:

        close_connection(conn)


def get_quiz_results(
    limit=20
):

    conn = get_connection()

    try:

        return conn.execute("""
            SELECT *
            FROM quiz_results
            ORDER BY created_at DESC
            LIMIT ?
        """, (
            int(limit),
        )).fetchall()

    finally:

        close_connection(conn)


# ============================================================
# USERS
# ============================================================

def get_user(
    username
):

    conn = get_connection()

    try:

        return conn.execute("""
            SELECT *
            FROM users
            WHERE username = ?
        """, (
            username,
        )).fetchone()

    finally:

        close_connection(conn)


def create_user(
    username,
    password_hash,
    role="user",
    verified=0
):

    conn = get_connection()

    try:

        cursor = conn.execute("""
            INSERT INTO users
            (
                username,
                password_hash,
                role,
                verified,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            username,
            password_hash,
            role,
            int(verified),
            datetime.now().isoformat()
        ))

        safe_commit(conn)

        return cursor.lastrowid

    finally:

        close_connection(conn)


def update_user(
    username,
    password_hash=None,
    role=None,
    verified=None
):

    conn = get_connection()

    try:

        if password_hash is not None:

            conn.execute("""
                UPDATE users
                SET password_hash = ?
                WHERE username = ?
            """, (
                password_hash,
                username
            ))

        if role is not None:

            conn.execute("""
                UPDATE users
                SET role = ?
                WHERE username = ?
            """, (
                role,
                username
            ))

        if verified is not None:

            conn.execute("""
                UPDATE users
                SET verified = ?
                WHERE username = ?
            """, (
                int(verified),
                username
            ))

        safe_commit(conn)

        return True

    finally:

        close_connection(conn)


def get_all_users():

    conn = get_connection()

    try:

        return conn.execute("""
            SELECT
                id,
                username,
                role,
                verified,
                created_at
            FROM users
            ORDER BY id
        """).fetchall()

    finally:

        close_connection(conn)


# ============================================================
# DATABASE STARTUP
# ============================================================

try:

    initialize_database()

except Exception as error:

    print(
        "SmartDesk database initialization warning:",
        error
    )