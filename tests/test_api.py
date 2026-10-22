"""Pruebas de integración del endpoint de FastAPI (RF-03)."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from parqueadero.api import app
from backend import main as main_module
from tests.seeders import basic_auth_headers, seed_test_users


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    original_db_path = main_module.DB_PATH
    main_module.DB_PATH = str(tmp_path_factory.mktemp("calculation-db") / "parqueadero.db")
    try:
        main_module.init_db()
        with sqlite3.connect(main_module.DB_PATH) as db:
            seed_test_users(db)
        with TestClient(
            app, headers=basic_auth_headers("test-admin")
        ) as test_client:
            yield test_client
    finally:
        main_module.DB_PATH = original_db_path


def test_salud(client):
    respuesta = client.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}


def test_calcular_tarifa_hora_iniciada(client):
    respuesta = client.post(
        "/calcular-tarifa",
        json={
            "hora_entrada": "2024-01-01T08:00:00",
            "hora_salida": "2024-01-01T09:30:00",
            "valor_hora": "3000",
        },
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["horas_cobradas"] == 2
    assert datos["costo"] == "6000.00"


def test_calcular_tarifa_con_minimo(client):
    respuesta = client.post(
        "/calcular-tarifa",
        json={
            "hora_entrada": "2024-01-01T08:00:00",
            "hora_salida": "2024-01-01T08:10:00",
            "valor_hora": "3000",
            "minutos_minimos": 60,
        },
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["minutos_cobrados"] == 60
    assert datos["costo"] == "3000.00"


def test_salida_antes_de_entrada_devuelve_422(client):
    respuesta = client.post(
        "/calcular-tarifa",
        json={
            "hora_entrada": "2024-01-01T09:00:00",
            "hora_salida": "2024-01-01T08:00:00",
            "valor_hora": "3000",
        },
    )
    assert respuesta.status_code == 422


def test_valor_hora_cero_devuelve_422(client):
    respuesta = client.post(
        "/calcular-tarifa",
        json={
            "hora_entrada": "2024-01-01T08:00:00",
            "hora_salida": "2024-01-01T09:00:00",
            "valor_hora": "0",
        },
    )
    assert respuesta.status_code == 422
