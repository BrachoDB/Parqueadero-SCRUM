"""
╔══════════════════════════════════════════════════════════════╗
║   TESTS DE RENDIMIENTO - Dev 2                              ║
║   Validación SLA: Respuesta ≤ 2 segundos (RF-01)            ║
╚══════════════════════════════════════════════════════════════╝
"""

import pytest
import time
import sqlite3
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient
from main import app, init_db, _warm_up_cache, DB_PATH

# ─────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Inicializa la BD de prueba antes de todos los tests."""
    init_db()
    _warm_up_cache()
    yield
    # Cleanup: eliminar todos los registros insertados por los tests
    test_placas = [
        'TST%',    # placa_prueba fixture
        'TSTREN01', 'TSTCNC01',  # tests de rendimiento
        'ABC123', 'DUP456', 'XYZ789', 'ABC12D'  # tests funcionales
    ]
    with sqlite3.connect(DB_PATH) as conn:
        for patron in test_placas:
            conn.execute(
                "DELETE FROM vehiculos_registro WHERE placa LIKE ?", (patron,)
            )
        conn.commit()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def placa_prueba():
    return f"TST{datetime.now().strftime('%H%M%S')[0:3]}01"


# ─────────────────────────────────────────────────────────────
# DEV 2: TESTS DE RENDIMIENTO SLA ≤ 2000ms
# ─────────────────────────────────────────────────────────────
class TestRendimientoSLA:
    """Verifica que TODOS los endpoints respondan en ≤ 2 segundos."""

    SLA_MS = 2000  # Límite estricto RF-01 Rendimiento

    def test_registro_entrada_tiempo_respuesta(self, client, placa_prueba):
        """RF-01 Rendimiento: Registro de entrada debe completarse en ≤ 2s."""
        t_start = time.perf_counter()
        response = client.post("/api/v1/vehiculos/entrada", json={
            "placa": placa_prueba,
            "tipo_vehiculo_id": 1
        })
        t_ms = (time.perf_counter() - t_start) * 1000

        assert response.status_code == 201, f"Error: {response.json()}"
        assert t_ms <= self.SLA_MS, (
            f"❌ SLA VIOLADO: registro_entrada tardó {t_ms:.1f}ms > {self.SLA_MS}ms"
        )
        print(f"\n  ✅ registro_entrada: {t_ms:.1f}ms ≤ {self.SLA_MS}ms")

    def test_consulta_tarifa_tiempo_respuesta(self, client):
        """RF-01 Rendimiento: Consulta de tarifa debe completarse en ≤ 2s."""
        # Asegurar que existe al menos un registro activo
        placa = "TSTREN01"
        client.post("/api/v1/vehiculos/entrada", json={
            "placa": placa, "tipo_vehiculo_id": 2
        })

        t_start = time.perf_counter()
        response = client.get(f"/api/v1/vehiculos/{placa}/tarifa")
        t_ms = (time.perf_counter() - t_start) * 1000

        assert response.status_code == 200, f"Error: {response.json()}"
        data = response.json()
        assert data["cumple_sla"] is True, (
            f"❌ API reporta SLA violado: {data['tiempo_respuesta_ms']}ms"
        )
        assert t_ms <= self.SLA_MS, (
            f"❌ SLA VIOLADO cliente: {t_ms:.1f}ms > {self.SLA_MS}ms"
        )
        print(f"\n  ✅ consulta_tarifa: {t_ms:.1f}ms ≤ {self.SLA_MS}ms")

    def test_vehiculos_activos_tiempo_respuesta(self, client):
        """Listado de vehículos activos debe responder en ≤ 2s."""
        t_start = time.perf_counter()
        response = client.get("/api/v1/vehiculos/activos")
        t_ms = (time.perf_counter() - t_start) * 1000

        assert response.status_code == 200
        assert t_ms <= self.SLA_MS, f"❌ SLA VIOLADO: {t_ms:.1f}ms"
        print(f"\n  ✅ vehiculos_activos: {t_ms:.1f}ms ≤ {self.SLA_MS}ms")

    def test_tarifas_cache_tiempo_respuesta(self, client):
        """RF-02: Consulta de tarifas desde caché debe ser < 100ms."""
        t_start = time.perf_counter()
        response = client.get("/api/v1/tarifas")
        t_ms = (time.perf_counter() - t_start) * 1000

        assert response.status_code == 200
        assert t_ms < 100, f"❌ Caché lenta: {t_ms:.1f}ms (esperado < 100ms)"
        print(f"\n  ✅ consulta_tarifas_cache: {t_ms:.1f}ms < 100ms")

    def test_arqueo_caja_tiempo_respuesta(self, client):
        """RF-04: Arqueo de caja debe responder en ≤ 2s."""
        t_start = time.perf_counter()
        response = client.get("/api/v1/reportes/arqueo")
        t_ms = (time.perf_counter() - t_start) * 1000

        assert response.status_code == 200
        assert t_ms <= self.SLA_MS, f"❌ SLA VIOLADO: {t_ms:.1f}ms"
        print(f"\n  ✅ arqueo_caja: {t_ms:.1f}ms ≤ {self.SLA_MS}ms")

    def test_sla_bajo_carga_concurrente(self, client):
        """
        Dev 2: Prueba de carga - 10 consultas concurrentes deben completarse en ≤ 2s.
        Simula múltiples operadores consultando tarifas simultáneamente.
        """
        import concurrent.futures

        placa = "TSTCNC01"
        client.post("/api/v1/vehiculos/entrada", json={
            "placa": placa, "tipo_vehiculo_id": 3
        })

        def consultar():
            t = time.perf_counter()
            r = client.get(f"/api/v1/vehiculos/{placa}/tarifa")
            return (time.perf_counter() - t) * 1000, r.status_code

        t_total_inicio = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            resultados = list(executor.map(lambda _: consultar(), range(10)))
        _t_total_ms = (time.perf_counter() - t_total_inicio) * 1000  # noqa: F841

        tiempos = [r[0] for r in resultados]
        max_tiempo = max(tiempos)
        avg_tiempo = sum(tiempos) / len(tiempos)

        assert all(r[1] == 200 for r in resultados), "Algunas consultas fallaron"
        assert max_tiempo <= self.SLA_MS, (
            f"❌ SLA VIOLADO bajo carga: máximo {max_tiempo:.1f}ms"
        )
        print(f"\n  ✅ Carga concurrente (10 req): avg={avg_tiempo:.1f}ms, max={max_tiempo:.1f}ms")


# ─────────────────────────────────────────────────────────────
# DEV 1: TESTS FUNCIONALES RF-01
# ─────────────────────────────────────────────────────────────
class TestRegistroVehiculos:
    """Valida la lógica funcional del registro de vehículos (RF-01)."""

    def test_registro_entrada_exitoso(self, client):
        """RF-01: El sistema debe registrar placa + hora de entrada correctamente."""
        response = client.post("/api/v1/vehiculos/entrada", json={
            "placa": "ABC123",
            "tipo_vehiculo_id": 1,
            "operador_id": 1
        })
        assert response.status_code == 201
        data = response.json()
        assert data["placa"] == "ABC123"
        assert data["estado"] == "ACTIVO"
        assert "hora_entrada" in data
        assert data["hora_entrada"] is not None
        # Verificar que la hora se generó server-side en el momento correcto
        hora = datetime.strptime(data["hora_entrada"], "%Y-%m-%d %H:%M:%S")
        assert (datetime.now() - hora).total_seconds() < 5  # Menos de 5s de diferencia

    def test_placa_invalida_rechazada(self, client):
        """RF-01: Placa con formato incorrecto debe ser rechazada."""
        response = client.post("/api/v1/vehiculos/entrada", json={
            "placa": "INVALIDA",
            "tipo_vehiculo_id": 1
        })
        assert response.status_code == 422

    def test_vehiculo_duplicado_rechazado(self, client):
        """RF-01: No se puede registrar un vehículo que ya está dentro."""
        placa = "DUP456"
        client.post("/api/v1/vehiculos/entrada", json={"placa": placa, "tipo_vehiculo_id": 2})
        response = client.post("/api/v1/vehiculos/entrada", json={"placa": placa, "tipo_vehiculo_id": 2})
        assert response.status_code == 409

    def test_formato_placa_colombiana(self, client):
        """RF-01: Acepta formato de placa colombiana estándar."""
        for placa in ["XYZ789", "ABC12D"]:
            r = client.post("/api/v1/vehiculos/entrada", json={"placa": placa, "tipo_vehiculo_id": 1})
            assert r.status_code in (201, 409), f"Fallo para placa {placa}: {r.json()}"


# ─────────────────────────────────────────────────────────────
# TESTS RF-02: TARIFA DIFERENCIAL
# ─────────────────────────────────────────────────────────────
class TestTarifaDiferencial:
    def test_tarifas_retornan_tres_tipos(self, client):
        """RF-02: Debe haber tarifas diferenciales para Moto, Carro y Camión."""
        response = client.get("/api/v1/tarifas")
        assert response.status_code == 200
        tarifas = response.json()["tarifas"]
        nombres = {t["nombre"] for t in tarifas}
        assert "Moto" in nombres
        assert "Carro" in nombres
        assert "Camión" in nombres

    def test_tarifa_moto_menor_que_carro(self, client):
        """RF-02: Moto debe tener tarifa menor que Carro."""
        response = client.get("/api/v1/tarifas")
        tarifas = {t["nombre"]: t["tarifa_hora"] for t in response.json()["tarifas"]}
        assert tarifas["Moto"] < tarifas["Carro"], "Tarifa Moto debe ser < Carro"
        assert tarifas["Carro"] < tarifas["Camión"], "Tarifa Carro debe ser < Camión"
