"""Password hashing and principal types for the parking API."""

from dataclasses import dataclass
import hashlib
import hmac
import secrets

PASSWORD_HASH_ITERATIONS = 600_000
PASSWORD_HASH_NAME = "sha256"
ROLE_NAMES = frozenset({"admin", "operador", "cliente"})
DUMMY_SALT = bytes.fromhex("8f5d3b72e40c1a699a72ec6d6156e477")
DUMMY_PASSWORD_HASH = hashlib.pbkdf2_hmac(
    PASSWORD_HASH_NAME,
    b"invalid-user-password",
    DUMMY_SALT,
    PASSWORD_HASH_ITERATIONS,
)


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    username: str
    role: str


def hash_password(password: str) -> tuple[str, str]:
    """Return a random salt and a PBKDF2-SHA256 password hash as hex strings."""
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        PASSWORD_HASH_NAME,
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    return salt.hex(), password_hash.hex()


def verify_password(password: str, salt_hex: str, password_hash_hex: str) -> bool:
    """Verify a password using a constant-time comparison."""
    try:
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(password_hash_hex)
    except ValueError:
        return False

    actual_hash = hashlib.pbkdf2_hmac(
        PASSWORD_HASH_NAME,
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    return hmac.compare_digest(actual_hash, expected_hash)
