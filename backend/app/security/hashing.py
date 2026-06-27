from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from typing import Final

ALGORITHM: Final = "pbkdf2_sha256"
ITERATIONS: Final = 260_000
SALT_BYTES: Final = 16


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty.")

    salt = os.urandom(SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS,
    )
    return f"{ALGORITHM}${ITERATIONS}${_b64encode(salt)}${_b64encode(derived)}"


def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False

    parts = stored_hash.split("$")
    if len(parts) != 4 or parts[0] != ALGORITHM:
        return secrets.compare_digest(password, stored_hash)

    try:
        iterations = int(parts[1])
        salt = _b64decode(parts[2])
        expected = _b64decode(parts[3])
    except Exception:
        return False

    computed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(computed, expected)