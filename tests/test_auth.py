import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend import main
from backend.auth import verify_password
from tests.seeders import TEST_USERS, seed_test_users


@pytest.fixture(scope="module")
def secured_client(tmp_path_factory):
    original_db_path = main.DB_PATH
    main.DB_PATH = str(tmp_path_factory.mktemp("auth-db") / "parqueadero.db")
    try:
        main.init_db()
        with sqlite3.connect(main.DB_PATH) as db:
            seed_test_users(db)
            client_id = db.execute(
                "SELECT id FROM auth_users WHERE username = 'test-client'"
            ).fetchone()[0]
            other_client_id = db.execute(
                "SELECT id FROM auth_users WHERE username = 'test-other-client'"
            ).fetchone()[0]
            timestamp = (datetime.now() - timedelta(minutes=45)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            db.executemany(
                """
                INSERT INTO vehiculos_registro
                    (placa, tipo_vehiculo_id, hora_entrada, tarifa_aplicada,
                     estado, cliente_id)
                VALUES (?, 2, ?, 4000, 'ACTIVO', ?)
                """,
                [
                    ("OWN123", timestamp, client_id),
                    ("OTH456", timestamp, other_client_id),
                ],
            )
        with TestClient(main.app) as client:
            yield client
    finally:
        main.DB_PATH = original_db_path


def auth_for(username):
    password, _role = TEST_USERS[username]
    return username, password


def test_private_endpoint_requires_valid_basic_auth(secured_client):
    missing = secured_client.get("/api/v1/tarifas")
    assert missing.status_code == 401
    assert missing.headers["www-authenticate"] == "Basic"

    invalid = secured_client.get(
        "/api/v1/tarifas",
        auth=("test-admin", "wrong-password"),
    )
    assert invalid.status_code == 401
    assert invalid.headers["www-authenticate"] == "Basic"

    malformed = secured_client.get(
        "/api/v1/tarifas",
        headers={"Authorization": "Basic !!!"},
    )
    assert malformed.status_code == 401


def test_health_remains_public(secured_client):
    response = secured_client.get("/health")
    assert response.status_code == 200


def test_user_provisioning_stores_salted_hash_and_rejects_invalid_roles(secured_client):
    password = "Another-Strong-Passphrase-2026"
    with sqlite3.connect(main.DB_PATH) as db:
        user_id = main.create_user(db, "new-operator", password, "operador")
        user = db.execute(
            "SELECT password_salt, password_hash, role FROM auth_users WHERE id = ?",
            (user_id,),
        ).fetchone()
        assert user[2] == "operador"
        assert user[1] != password
        assert verify_password(password, user[0], user[1])

        with pytest.raises(ValueError, match="rol"):
            main.create_user(db, "invalid-role", password, "superuser")


def test_legacy_database_migrates_customer_ownership_column(tmp_path):
    original_db_path = main.DB_PATH
    original_schema_path = main.SCHEMA_PATH
    main.DB_PATH = str(tmp_path / "legacy.db")
    main.SCHEMA_PATH = str(tmp_path / "legacy-schema.sql")
    try:
        schema = Path(original_schema_path).read_text(encoding="utf-8")
        schema = schema.replace(
            "    cliente_id          INTEGER       REFERENCES auth_users(id),\n",
            "",
        )
        Path(main.SCHEMA_PATH).write_text(schema, encoding="utf-8")
        main.init_db()

        with sqlite3.connect(main.DB_PATH) as db:
            columns = {
                row[1] for row in db.execute("PRAGMA table_info(vehiculos_registro)")
            }
        assert "cliente_id" in columns
    finally:
        main.DB_PATH = original_db_path
        main.SCHEMA_PATH = original_schema_path


def test_role_matrix_rejects_forbidden_operations(secured_client):
    denied_entry = secured_client.post(
        "/api/v1/vehiculos/entrada",
        auth=auth_for("test-client"),
        json={"placa": "DEN123", "tipo_vehiculo_id": 1},
    )
    assert denied_entry.status_code == 403

    denied_report = secured_client.get(
        "/api/v1/reportes/arqueo",
        auth=auth_for("test-operator"),
    )
    assert denied_report.status_code == 403

    denied_rates = secured_client.get(
        "/api/v1/tarifas",
        auth=auth_for("test-client"),
    )
    assert denied_rates.status_code == 403


def test_client_reads_only_owned_vehicle_data(secured_client):
    history = secured_client.get(
        "/api/v1/clientes/me/vehiculos",
        auth=auth_for("test-client"),
    )
    assert history.status_code == 200
    assert [row["placa"] for row in history.json()["vehiculos"]] == ["OWN123"]

    active = secured_client.get(
        "/api/v1/vehiculos/activos",
        auth=auth_for("test-client"),
    )
    assert active.status_code == 200
    assert [row["placa"] for row in active.json()["vehiculos"]] == ["OWN123"]

    own_tariff = secured_client.get(
        "/api/v1/vehiculos/OWN123/tarifa",
        auth=auth_for("test-client"),
    )
    assert own_tariff.status_code == 200

    other_tariff = secured_client.get(
        "/api/v1/vehiculos/OTH456/tarifa",
        auth=auth_for("test-client"),
    )
    assert other_tariff.status_code == 404


def test_operator_entry_assigns_authenticated_operator_and_customer(secured_client):
    with sqlite3.connect(main.DB_PATH) as db:
        operator_id = db.execute(
            "SELECT id FROM auth_users WHERE username = 'test-operator'"
        ).fetchone()[0]
        client_id = db.execute(
            "SELECT id FROM auth_users WHERE username = 'test-client'"
        ).fetchone()[0]

    response = secured_client.post(
        "/api/v1/vehiculos/entrada",
        auth=auth_for("test-operator"),
        json={
            "placa": "NEW789",
            "tipo_vehiculo_id": 1,
            "operador_id": 999999,
            "cliente_id": client_id,
        },
    )
    assert response.status_code == 201, response.text

    with sqlite3.connect(main.DB_PATH) as db:
        registered = db.execute(
            "SELECT operador_id, cliente_id FROM vehiculos_registro WHERE placa = 'NEW789'"
        ).fetchone()
    assert registered == (operator_id, client_id)


def test_admin_has_global_read_and_write_access(secured_client):
    response = secured_client.get(
        "/api/v1/reportes/arqueo",
        auth=auth_for("test-admin"),
    )
    assert response.status_code == 200

    created = secured_client.post(
        "/api/v1/vehiculos/entrada",
        auth=auth_for("test-admin"),
        json={"placa": "ADM456", "tipo_vehiculo_id": 1},
    )
    assert created.status_code == 201


def test_calculation_api_requires_basic_auth(secured_client):
    from parqueadero.api import app as calculation_app

    with TestClient(calculation_app) as client:
        unauthorized = client.get("/tarifas")
        assert unauthorized.status_code == 401
        authorized = client.get("/tarifas", auth=auth_for("test-client"))
        assert authorized.status_code == 200
