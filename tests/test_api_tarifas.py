"""Pruebas de integración de los endpoints del RF-02 en FastAPI."""

from fastapi.testclient import TestClient

from parqueadero.api import app

client = TestClient(app)


def test_calcular_tarifa_por_tipo_carro():
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


def test_tarifa_diferencial_moto_mas_barata_que_carro():
    cuerpo_moto = {
        "tipo_vehiculo": "moto",
        "hora_entrada": "2024-01-01T08:00:00",
        "hora_salida": "2024-01-01T10:00:00",
    }
    cuerpo_carro = dict(cuerpo_moto, tipo_vehiculo="carro")
    costo_moto = client.post("/calcular-tarifa-vehiculo", json=cuerpo_moto).json()["costo"]
    costo_carro = client.post("/calcular-tarifa-vehiculo", json=cuerpo_carro).json()["costo"]
    assert float(costo_moto) < float(costo_carro)


def test_tipo_vehiculo_invalido_devuelve_422():
    respuesta = client.post(
        "/calcular-tarifa-vehiculo",
        json={
            "tipo_vehiculo": "patineta",
            "hora_entrada": "2024-01-01T08:00:00",
            "hora_salida": "2024-01-01T09:00:00",
        },
    )
    assert respuesta.status_code == 422


def test_salida_antes_de_entrada_devuelve_422():
    respuesta = client.post(
        "/calcular-tarifa-vehiculo",
        json={
            "tipo_vehiculo": "carro",
            "hora_entrada": "2024-01-01T09:00:00",
            "hora_salida": "2024-01-01T08:00:00",
        },
    )
    assert respuesta.status_code == 422


def test_listar_tarifas_incluye_todos_los_tipos():
    respuesta = client.get("/tarifas")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    tipos = {item["tipo_vehiculo"] for item in datos}
    assert tipos == {"carro", "moto", "camioneta", "bus", "camion"}
    # Cada tarifa debe traer valor y mínimo.
    for item in datos:
        assert "valor_hora" in item
        assert "minutos_minimos" in item
