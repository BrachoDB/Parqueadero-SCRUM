"""Pruebas unitarias del RF-02: tipos de vehículo y tarifa diferencial."""

from datetime import datetime
from decimal import Decimal

import pytest

from parqueadero.tarifas import (
    CATALOGO_DEFECTO,
    CatalogoTarifas,
    ErrorVehiculoDesconocido,
    TARIFAS_DEFECTO,
    TarifaVehiculo,
    TipoVehiculo,
    calcular_costo_por_tipo,
)
from parqueadero.calculo import Tarifa


def _hora(h: int, m: int) -> datetime:
    return datetime(2024, 1, 1, h, m)


class TestTipoVehiculo:
    def test_valores_del_enum(self):
        assert TipoVehiculo.CARRO.value == "carro"
        assert TipoVehiculo.MOTO.value == "moto"
        assert TipoVehiculo.CAMIONETA.value == "camioneta"
        assert TipoVehiculo.BUS.value == "bus"
        assert TipoVehiculo.CAMION.value == "camion"


class TestCatalogoTarifas:
    def test_tarifa_para_carro(self):
        tarifa = CATALOGO_DEFECTO.tarifa_para(TipoVehiculo.CARRO)
        assert tarifa.valor_hora == Decimal("3000")

    def test_tarifa_para_moto_es_menor_que_carro(self):
        moto = CATALOGO_DEFECTO.tarifa_para("moto").valor_hora
        carro = CATALOGO_DEFECTO.tarifa_para("carro").valor_hora
        assert moto < carro

    def test_acepta_string_en_minusculas_y_con_espacios(self):
        tarifa = CATALOGO_DEFECTO.tarifa_para("  CARRO ")
        assert tarifa.valor_hora == Decimal("3000")

    def test_detalle_para_incluye_descripcion(self):
        detalle = CATALOGO_DEFECTO.detalle_para(TipoVehiculo.CAMION)
        assert detalle.tipo == TipoVehiculo.CAMION
        assert isinstance(detalle, TarifaVehiculo)
        assert detalle.descripcion

    def test_todos_los_tipos_tienen_tarifa(self):
        assert set(CATALOGO_DEFECTO.tipos()) == set(TipoVehiculo)

    def test_vehiculo_desconocido_es_error(self):
        with pytest.raises(ErrorVehiculoDesconocido):
            CATALOGO_DEFECTO.tarifa_para("patineta")

    def test_catalogo_personalizado(self):
        catalogo = CatalogoTarifas(
            {
                TipoVehiculo.CARRO: TarifaVehiculo(
                    tipo=TipoVehiculo.CARRO,
                    tarifa=Tarifa(valor_hora=Decimal("5000")),
                    descripcion="Carro particular (custom)",
                )
            }
        )
        assert catalogo.tarifa_para("carro").valor_hora == Decimal("5000")


class TestCalculoPorTipo:
    def test_combina_tipo_y_tiempo(self):
        # Carro: 3000/h, 90 minutos => 2 horas => 6000.
        r = calcular_costo_por_tipo(_hora(8, 0), _hora(9, 30), TipoVehiculo.CARRO)
        assert r.horas_cobradas == 2
        assert r.costo == Decimal("6000.00")

    def test_tarifa_diferencial_entre_tipos(self):
        # Misma estadia (2 h): el camion debe costar mas que la moto.
        moto = calcular_costo_por_tipo(_hora(8, 0), _hora(10, 0), "moto")
        camion = calcular_costo_por_tipo(_hora(8, 0), _hora(10, 0), "camion")
        assert camion.costo > moto.costo

    def test_minimo_diferencial_por_tipo(self):
        # Bus tiene minimo 60 min: estadia de 10 min cobra 1 hora = 6000.
        r = calcular_costo_por_tipo(_hora(8, 0), _hora(8, 10), TipoVehiculo.BUS)
        assert r.minutos_cobrados == 60
        assert r.costo == Decimal("6000.00")

    def test_usa_catalogo_personalizado_si_se_pasa(self):
        catalogo = CatalogoTarifas(
            {
                TipoVehiculo.MOTO: TarifaVehiculo(
                    tipo=TipoVehiculo.MOTO,
                    tarifa=Tarifa(valor_hora=Decimal("1000")),
                    descripcion="Moto custom",
                )
            }
        )
        r = calcular_costo_por_tipo(
            _hora(8, 0), _hora(9, 0), "moto", catalogo=catalogo
        )
        assert r.costo == Decimal("1000.00")

    def test_tarifas_defecto_coinciden_con_catalogo(self):
        assert TARIFAS_DEFECTO is CATALOGO_DEFECTO._tarifas or dict(TARIFAS_DEFECTO) == dict(
            CATALOGO_DEFECTO._tarifas
        )
