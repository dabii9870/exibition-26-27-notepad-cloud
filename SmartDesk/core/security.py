"""
SmartDesk Security System

Provides password hashing and encryption helpers.

Passwords are never stored as plain text.
"""

import base64
import hashlib
import hmac
import os
import secrets


HASH_ITERATIONS = 310_000
SALT_SIZE = 32


# ============================================================
# PASSWORD SECURITY
# ============================================================

def generate_password_hash(password):
    """
    Generate a secure PBKDF2 password hash.

    Returns a string containing:
        algorithm
        iterations
        salt
        hash
    """

    if not isinstance(password, str):
        raise TypeError(
            "Password must be a string."
        )

    if len(password) < 4:
        raise ValueError(
            "Password must contain at least 4 characters."
        )

    salt = os.urandom(SALT_SIZE)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        HASH_ITERATIONS
    )

    return (
        f"pbkdf2_sha256$"
        f"{HASH_ITERATIONS}$"
        f"{base64.b64encode(salt).decode()}$"
        f"{base64.b64encode(password_hash).decode()}"
    )


def verify_password(password, stored_hash):
    """Verify a password against a stored hash."""

    try:
        parts = stored_hash.split("$")

        if len(parts) != 4:
            return False

        algorithm = parts[0]
        iterations = int(parts[1])
        salt = base64.b64decode(parts[2])
        expected_hash = base64.b64decode(parts[3])

        if algorithm != "pbkdf2_sha256":
            return False

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations
        )

        return hmac.compare_digest(
            actual_hash,
            expected_hash
        )

    except Exception:
        return False


# ============================================================
# RANDOM TOKENS
# ============================================================

def generate_token(length=32):
    """Generate a cryptographically secure token."""

    return secrets.token_urlsafe(length)


def generate_session_token():
    """Generate a session token."""

    return secrets.token_urlsafe(48)


# ============================================================
# FILE HASHING
# ============================================================

def hash_bytes(data):
    """Create a SHA-256 hash of bytes."""

    return hashlib.sha256(
        data
    ).hexdigest()


def hash_text(text):
    """Create a SHA-256 hash of text."""

    return hash_bytes(
        text.encode("utf-8")
    )


# ============================================================
# SIMPLE DATA ENCRYPTION HELPER
# ============================================================

def derive_key(password, salt):
    """
    Derive a cryptographic key from a password.

    This helper is intended for the Private Vault system.
    """

    if isinstance(salt, str):
        salt = salt.encode("utf-8")

    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        HASH_ITERATIONS,
        dklen=32
    )


def xor_encrypt(data, key):
    """
    Lightweight byte transformation helper.

    This is NOT intended to replace authenticated encryption.
    The production Vault should use an authenticated encryption
    library such as AES-GCM or Fernet.
    """

    if isinstance(data, str):
        data = data.encode("utf-8")

    output = bytearray()

    for index, byte in enumerate(data):
        output.append(
            byte ^ key[index % len(key)]
        )

    return bytes(output)


def xor_decrypt(data, key):
    """Reverse xor_encrypt()."""

    return xor_encrypt(
        data,
        key
    )


# ============================================================
# SECURE RANDOM SALT
# ============================================================

def generate_salt():
    """Generate a secure random salt."""

    return base64.b64encode(
        os.urandom(SALT_SIZE)
    ).decode("utf-8")