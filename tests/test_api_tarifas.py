"""Pruebas de integración de los endpoints del RF-02 en FastAPI."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from parqueadero.api import app
from backend import main as main_module
from tests.seeders import basic_auth_headers, seed_test_users


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    original_db_path = main_module.DB_PATH
    main_module.DB_PATH = str(tmp_path_factory.mktemp("tariff-api-db") / "parqueadero.db")
    try:
        main_module.init_db()
        with sqlite3.connect(main_module.DB_PATH) as db:
            seed_test_users(db)
        with TestClient(app, headers=basic_auth_headers("test-admin")) as test_client:
            yield test_client
    finally:
        main_module.DB_PATH = original_db_path


def test_calcular_tarifa_por_tipo_carro(client):
    respuesta = client.post(
        "/calcular-tarifa-vehiculo",
        json={
            "tipo_vehiculo": "carro",
            "hora_entrada": "2024-01-01T08:00:00",
            "hora_salida": "2024-01-01T09:30:00",
        },
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["horas_cobradas"] == 2
    assert datos["costo"] == "6000.00"


def test_tarifa_diferencial_moto_mas_barata_que_carro(client):
    cuerpo_moto = {
        "tipo_vehiculo": "moto",
        "hora_entrada": "2024-01-01T08:00:00",
        "hora_salida": "2024-01-01T10:00:00",
    }
    cuerpo_carro = dict(cuerpo_moto, tipo_vehiculo="carro")
    costo_moto = client.post("/calcular-tarifa-vehiculo", json=cuerpo_moto).json()["costo"]
    costo_carro = client.post("/calcular-tarifa-vehiculo", json=cuerpo_carro).json()["costo"]
    assert float(costo_moto) < float(costo_carro)


def test_tipo_vehiculo_invalido_devuelve_422(client):
    respuesta = client.post(
        "/calcular-tarifa-vehiculo",
        json={
            "tipo_vehiculo": "patineta",
            "hora_entrada": "2024-01-01T08:00:00",
            "hora_salida": "2024-01-01T09:00:00",
        },
    )
    assert respuesta.status_code == 422


def test_salida_antes_de_entrada_devuelve_422(client):
    respuesta = client.post(
        "/calcular-tarifa-vehiculo",
        json={
            "tipo_vehiculo": "carro",
            "hora_entrada": "2024-01-01T09:00:00",
            "hora_salida": "2024-01-01T08:00:00",
        },
    )
    assert respuesta.status_code == 422


def test_listar_tarifas_incluye_todos_los_tipos(client):
    respuesta = client.get("/tarifas")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    tipos = {item["tipo_vehiculo"] for item in datos}
    assert tipos == {"carro", "moto", "camioneta", "bus", "camion"}
    # Cada tarifa debe traer valor y mínimo.
    for item in datos:
        assert "valor_hora" in item
        assert "minutos_minimos" in item
