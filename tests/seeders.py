"""Test-only authentication fixtures; never imported by the production app."""

import base64

from backend.auth import hash_password

TEST_USERS = {
    "test-admin": ("Test-Admin-Passphrase-2026", "admin"),
    "test-operator": ("Test-Operator-Passphrase-2026", "operador"),
    "test-client": ("Test-Client-Passphrase-2026", "cliente"),
    "test-other-client": ("Test-Other-Client-Passphrase-2026", "cliente"),
}


def basic_auth_headers(username):
    password = TEST_USERS[username][0]
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def seed_test_users(db):
    """Create the standard role fixtures in a test database."""
    for username, (password, role) in TEST_USERS.items():
        salt, password_hash = hash_password(password)
        db.execute(
            """
            INSERT INTO auth_users (username, password_salt, password_hash, role)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                password_salt = excluded.password_salt,
                password_hash = excluded.password_hash,
                role = excluded.role,
                active = 1
            """,
            (username, salt, password_hash, role),
        )
    db.commit()
