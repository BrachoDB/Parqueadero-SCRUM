"""Pruebas unitarias del módulo de cálculo (RF-03)."""

from datetime import datetime
from decimal import Decimal

import pytest

from parqueadero.calculo import ErrorDeCalculo, Tarifa, calcular_costo

TARIFA = Tarifa(valor_hora=Decimal("3000"))


def _hora(h: int, m: int) -> datetime:
    return datetime(2024, 1, 1, h, m)


class TestCalculoPorHoraIniciada:
    def test_hora_exacta_cobra_una_hora(self):
        r = calcular_costo(_hora(8, 0), _hora(9, 0), TARIFA)
        assert r.horas_cobradas == 1
        assert r.costo == Decimal("3000.00")

    def test_minutos_redondean_hacia_arriba(self):
        # 90 minutos => 2 horas completas (hora iniciada).
        r = calcular_costo(_hora(8, 0), _hora(9, 30), TARIFA)
        assert r.minutos_estadia == 90
        assert r.horas_cobradas == 2
        assert r.costo == Decimal("6000.00")

    def test_un_minuto_de_mas_cobra_hora_completa(self):
        r = calcular_costo(_hora(8, 0), _hora(9, 1), TARIFA)
        assert r.horas_cobradas == 2

    def test_estadia_cero_cobra_cero(self):
        r = calcular_costo(_hora(8, 0), _hora(8, 0), TARIFA)
        assert r.horas_cobradas == 0
        assert r.costo == Decimal("0.00")

    def test_costo_con_dos_decimales(self):
        tarifa = Tarifa(valor_hora=Decimal("2500.5"))
        r = calcular_costo(_hora(8, 0), _hora(9, 0), tarifa)
        assert r.costo == Decimal("2500.50")


class TestCobroMinimo:
    def test_minimo_forza_hora_completa(self):
        # Estadia de 10 minutos pero el minimo es 60 => se cobra 1 hora.
        tarifa = Tarifa(valor_hora=Decimal("3000"), minutos_minimos=60)
        r = calcular_costo(_hora(8, 0), _hora(8, 10), tarifa)
        assert r.minutos_cobrados == 60
        assert r.horas_cobradas == 1
        assert r.costo == Decimal("3000.00")

    def test_estadia_supera_minimo(self):
        tarifa = Tarifa(valor_hora=Decimal("3000"), minutos_minimos=60)
        r = calcular_costo(_hora(8, 0), _hora(10, 0), tarifa)
        assert r.horas_cobradas == 2
        assert r.costo == Decimal("6000.00")


class TestValidaciones:
    def test_salida_antes_de_entrada_es_error(self):
        with pytest.raises(ErrorDeCalculo):
            calcular_costo(_hora(9, 0), _hora(8, 0), TARIFA)

    def test_valor_hora_negativo_es_error(self):
        with pytest.raises(ErrorDeCalculo):
            Tarifa(valor_hora=Decimal("-1000"))

    def test_minutos_minimos_negativos_son_error(self):
        with pytest.raises(ErrorDeCalculo):
            Tarifa(valor_hora=Decimal("3000"), minutos_minimos=-5)
