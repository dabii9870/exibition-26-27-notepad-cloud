import hashlib
import secrets
import base64
import hmac


# ============================================================
# PASSWORD SETTINGS
# ============================================================

PASSWORD_ITERATIONS = 200_000


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    """
    Create a secure PBKDF2 password hash.
    """

    if password is None:
        password = ""

    password = str(password)

    salt = secrets.token_bytes(32)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS
    )

    return (
        f"{PASSWORD_ITERATIONS}$"
        f"{base64.b64encode(salt).decode('ascii')}$"
        f"{base64.b64encode(password_hash).decode('ascii')}"
    )


def generate_password_hash(password):
    """
    Compatibility function used by SmartDesk login.py.

    This intentionally points to the same password hashing
    system as hash_password().
    """

    return hash_password(password)


def verify_password(password, stored_hash):
    """
    Verify a password against a stored PBKDF2 hash.
    """

    if password is None:
        return False

    if not stored_hash:
        return False

    try:
        parts = stored_hash.split("$")

        if len(parts) != 3:
            return False

        iterations = int(parts[0])

        salt = base64.b64decode(
            parts[1]
        )

        expected_hash = base64.b64decode(
            parts[2]
        )

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            str(password).encode("utf-8"),
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
# COMPATIBILITY ALIAS
# ============================================================

def check_password(password, stored_hash):
    """
    Compatibility alias for password checking.
    """

    return verify_password(
        password,
        stored_hash
    )


# ============================================================
# GENERAL HASHING
# ============================================================

def hash_text(text):
    """
    SHA-256 hash for ordinary text.
    """

    if text is None:
        text = ""

    return hashlib.sha256(
        str(text).encode("utf-8")
    ).hexdigest()


def hash_bytes(data):
    """
    SHA-256 hash for bytes.
    """

    if data is None:
        data = b""

    return hashlib.sha256(
        data
    ).hexdigest()


# ============================================================
# TOKENS
# ============================================================

def generate_token(length=32):
    """
    Generate a secure random token.
    """

    return secrets.token_urlsafe(
        length
    )


def create_token(length=32):
    """
    Compatibility alias.
    """

    return generate_token(
        length
    )


# ============================================================
# SALT
# ============================================================

def generate_salt(length=32):
    """
    Generate a random salt.
    """

    return secrets.token_bytes(
        length
    )


# ============================================================
# KEY DERIVATION
# ============================================================

def derive_key(
    password,
    salt,
    iterations=200_000
):
    """
    Derive a 32-byte key from a password.
    """

    if isinstance(salt, str):
        salt = salt.encode("utf-8")

    return hashlib.pbkdf2_hmac(
        "sha256",
        str(password).encode("utf-8"),
        salt,
        iterations,
        dklen=32
    )


# ============================================================
# XOR ENCRYPTION
# ============================================================

def xor_encrypt(data, key):
    """
    Simple symmetric encryption used by existing SmartDesk
    compatibility features.
    """

    if isinstance(data, str):
        data = data.encode("utf-8")

    if isinstance(key, str):
        key = key.encode("utf-8")

    if not key:
        raise ValueError(
            "Encryption key cannot be empty."
        )

    result = bytearray()

    for index, byte in enumerate(data):
        result.append(
            byte ^ key[index % len(key)]
        )

    return bytes(result)


def xor_decrypt(data, key):
    """
    XOR decryption.
    """

    return xor_encrypt(
        data,
        key
    )


# ============================================================
# TEXT ENCRYPTION
# ============================================================

def encrypt_text(text, password):
    """
    Encrypt text using a password-derived key.
    """

    salt = generate_salt(16)

    key = derive_key(
        password,
        salt
    )

    encrypted = xor_encrypt(
        text,
        key
    )

    salt_encoded = base64.b64encode(
        salt
    ).decode("ascii")

    data_encoded = base64.b64encode(
        encrypted
    ).decode("ascii")

    return salt_encoded + ":" + data_encoded


def decrypt_text(encrypted_text, password):
    """
    Decrypt text created by encrypt_text().
    """

    salt_encoded, data_encoded = (
        encrypted_text.split(":", 1)
    )

    salt = base64.b64decode(
        salt_encoded
    )

    encrypted = base64.b64decode(
        data_encoded
    )

    key = derive_key(
        password,
        salt
    )

    decrypted = xor_decrypt(
        encrypted,
        key
    )

    return decrypted.decode(
        "utf-8"
    )


# ============================================================
# PASSWORD VALIDATION
# ============================================================

def password_is_valid(password):
    """
    Basic password validation.
    """

    if password is None:
        return False

    return len(str(password)) >= 6


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_password = "SmartDeskTest123!"

    print("Testing SmartDesk security...")

    hashed = generate_password_hash(
        test_password
    )

    print(
        "Hash created:",
        bool(hashed)
    )

    print(
        "Correct password:",
        verify_password(
            test_password,
            hashed
        )
    )

    print(
        "Wrong password:",
        verify_password(
            "wrong-password",
            hashed
        )
    )

    print("Security test complete.")