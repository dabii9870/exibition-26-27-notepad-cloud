import sqlite3
from datetime import datetime

import config
from core.security import (
    hash_password,
    verify_password,
)


# ============================================================
# SMARTDESK ADMIN ACCOUNT
# ============================================================

ADMIN_USERNAME = "davereub"
ADMIN_PASSWORD = "98709870!@"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    connection = sqlite3.connect(
        str(config.DB_PATH),
        timeout=20
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# USERS TABLE
# ============================================================

def ensure_users_table():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                verified INTEGER DEFAULT 0,
                created_at TEXT
            )
            """
        )

        connection.commit()

        # ----------------------------------------------------
        # Check existing columns
        # ----------------------------------------------------

        cursor.execute(
            "PRAGMA table_info(users)"
        )

        columns = {
            row["name"]
            for row in cursor.fetchall()
        }

        # Older SmartDesk database migration
        if "role" not in columns:
            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN role TEXT DEFAULT 'user'
                """
            )

        if "verified" not in columns:
            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN verified INTEGER DEFAULT 0
                """
            )

        if "created_at" not in columns:
            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN created_at TEXT
                """
            )

            now = datetime.now().isoformat()

            cursor.execute(
                """
                UPDATE users
                SET created_at = ?
                WHERE created_at IS NULL
                """,
                (now,)
            )

        connection.commit()

    finally:
        connection.close()


# ============================================================
# CREATE / REPAIR ADMIN
# ============================================================

def ensure_admin_account(
    password=None,
    username=None
):
    """
    Create or repair the SmartDesk administrator.

    This accepts the older call pattern `ensure_admin_account(database)` from
    legacy startup code and still guarantees the required admin account exists
    and is verified.
    """

    ensure_users_table()

    if username is None:
        username = ADMIN_USERNAME

    # Backward compatibility: older code may pass the database module as the
    # first positional argument instead of a password string.
    if password is not None and not isinstance(password, str):
        password = ADMIN_PASSWORD

    if password is None:
        password = ADMIN_PASSWORD

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Force a single verified admin account: only davereub may be admin.
        cursor.execute(
            """
            UPDATE users
            SET role = 'user', verified = 0
            WHERE username != ? AND role = 'admin'
            """,
            (username,)
        )

        cursor.execute(
            """
            SELECT
                id,
                username,
                password_hash,
                role,
                verified
            FROM users
            WHERE username = ?
            """,
            (username,)
        )

        user = cursor.fetchone()

        password_hash = hash_password(password)

        # ----------------------------------------------------
        # ADMIN DOES NOT EXIST
        # ----------------------------------------------------

        if user is None:
            cursor.execute(
                """
                INSERT INTO users (
                    username,
                    password_hash,
                    role,
                    verified,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    username,
                    password_hash,
                    "admin",
                    1,
                    datetime.now().isoformat()
                )
            )

            connection.commit()
            return True

        # ----------------------------------------------------
        # ADMIN EXISTS
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE users
            SET
                password_hash = ?,
                role = 'admin',
                verified = 1,
                created_at = COALESCE(created_at, ?)
            WHERE username = ?
            """,
            (
                password_hash,
                datetime.now().isoformat(),
                username,
            )
        )

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

def create_admin_account(
    password=None,
    username=None
):
    return ensure_admin_account(
        password,
        username
    )


# ============================================================
# ADMIN CHECK
# ============================================================

def is_admin(username):
    if username is None:
        return False

    if hasattr(username, "keys"):
        try:
            username = username["username"]
        except Exception:
            username = None
    elif hasattr(username, "__getitem__") and not isinstance(username, str):
        try:
            username = username["username"]
        except Exception:
            try:
                username = username[1]
            except Exception:
                username = None

    if not username:
        return False

    ensure_users_table()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT role
            FROM users
            WHERE username = ?
            """,
            (username,)
        )

        user = cursor.fetchone()

        if user is None:
            return False

        return user["role"] == "admin"

    finally:
        connection.close()


# ============================================================
# VERIFIED CHECK
# ============================================================

def is_verified(username):
    if username is None:
        return False

    if hasattr(username, "keys"):
        try:
            username = username["username"]
        except Exception:
            username = None
    elif hasattr(username, "__getitem__") and not isinstance(username, str):
        try:
            username = username["username"]
        except Exception:
            try:
                username = username[1]
            except Exception:
                username = None

    if not username:
        return False

    ensure_users_table()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT verified
            FROM users
            WHERE username = ?
            """,
            (username,)
        )

        user = cursor.fetchone()

        if user is None:
            return False

        return bool(user["verified"])

    finally:
        connection.close()


# ============================================================
# ADMIN DETAILS
# ============================================================

def get_admin_username():
    return ADMIN_USERNAME


def get_admin_password():
    return ADMIN_PASSWORD


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":

    print("SmartDesk admin bootstrap test")

    ensure_admin_account()

    print(
        "Admin account:",
        ADMIN_USERNAME
    )

    print(
        "Admin status:",
        is_admin(ADMIN_USERNAME)
    )

    print(
        "Verified:",
        is_verified(ADMIN_USERNAME)
    )

    print("Test complete.")