import sqlite3
from datetime import datetime

import config
from core.security import generate_password_hash


ADMIN_USERNAME = "davereub"
ADMIN_PASSWORD = "98709870!@"


def get_database_connection():
    """Open the SmartDesk database."""
    return sqlite3.connect(config.DATABASE_PATH)


def ensure_users_table(connection):
    """
    Make sure the users table has all fields required by SmartDesk.

    This also handles older SmartDesk databases that were created
    before the admin system was added.
    """

    cursor = connection.cursor()

    # Create the table if it doesn't exist.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            verified INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()

    # ---------------------------------------------------------
    # Check existing columns
    # ---------------------------------------------------------

    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()

    column_names = {
        column[1]
        for column in columns
    }

    # ---------------------------------------------------------
    # Add missing role column
    # ---------------------------------------------------------

    if "role" not in column_names:
        cursor.execute(
            """
            ALTER TABLE users
            ADD COLUMN role TEXT NOT NULL DEFAULT 'user'
            """
        )

    # ---------------------------------------------------------
    # Add missing verified column
    # ---------------------------------------------------------

    if "verified" not in column_names:
        cursor.execute(
            """
            ALTER TABLE users
            ADD COLUMN verified INTEGER NOT NULL DEFAULT 0
            """
        )

    # ---------------------------------------------------------
    # Add missing created_at column
    # ---------------------------------------------------------

    if "created_at" not in column_names:
        now = datetime.now().isoformat()

        cursor.execute(
            """
            ALTER TABLE users
            ADD COLUMN created_at TEXT NOT NULL DEFAULT ?
            """,
            (now,)
        )

    connection.commit()

    # ---------------------------------------------------------
    # Repair existing NULL values
    # ---------------------------------------------------------

    now = datetime.now().isoformat()

    try:
        cursor.execute(
            """
            UPDATE users
            SET created_at = ?
            WHERE created_at IS NULL
            """,
            (now,)
        )
    except sqlite3.OperationalError:
        pass

    connection.commit()


def create_admin_account():
    """
    Create or repair the default SmartDesk administrator.

    Username:
        davereub

    Password:
        98709870!@

    The account is automatically marked as:
        role = admin
        verified = 1
    """

    connection = get_database_connection()

    try:
        ensure_users_table(connection)

        cursor = connection.cursor()

        # -----------------------------------------------------
        # Check if admin already exists
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            """,
            (ADMIN_USERNAME,)
        )

        existing_user = cursor.fetchone()

        # -----------------------------------------------------
        # Existing admin
        # -----------------------------------------------------

        if existing_user:

            cursor.execute(
                """
                UPDATE users
                SET role = ?,
                    verified = 1
                WHERE username = ?
                """,
                (
                    "admin",
                    ADMIN_USERNAME
                )
            )

            # Repair missing created_at if necessary.
            now = datetime.now().isoformat()

            try:
                cursor.execute(
                    """
                    UPDATE users
                    SET created_at = ?
                    WHERE username = ?
                    AND (created_at IS NULL OR created_at = '')
                    """,
                    (
                        now,
                        ADMIN_USERNAME
                    )
                )
            except sqlite3.OperationalError:
                pass

        # -----------------------------------------------------
        # Create admin
        # -----------------------------------------------------

        else:

            password_hash = generate_password_hash(
                ADMIN_PASSWORD
            )

            created_at = datetime.now().isoformat()

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
                    ADMIN_USERNAME,
                    password_hash,
                    "admin",
                    1,
                    created_at
                )
            )

        connection.commit()

    finally:
        connection.close()


if __name__ == "__main__":
    create_admin_account()
    print("SmartDesk admin account is ready.")