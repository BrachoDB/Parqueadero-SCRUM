"""Interactively provision a Basic Auth user in the configured database."""

import argparse
import getpass
import sqlite3

from backend.main import DB_PATH, create_user, init_db
from backend.auth import ROLE_NAMES


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", required=True)
    parser.add_argument("--role", required=True, choices=sorted(ROLE_NAMES))
    args = parser.parse_args()

    password = getpass.getpass("Contraseña (mínimo 12 caracteres): ")
    confirmation = getpass.getpass("Confirma la contraseña: ")
    if password != confirmation:
        parser.error("Las contraseñas no coinciden.")

    init_db()
    with sqlite3.connect(DB_PATH) as db:
        user_id = create_user(db, args.username, password, args.role)
        db.commit()
    print(f"Usuario '{args.username}' creado con rol '{args.role}' (ID {user_id}).")


if __name__ == "__main__":
    main()
