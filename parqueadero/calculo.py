"""RF-03: Cálculo de la tarifa del parqueadero por tiempo transcurrido.

Este módulo contiene la lógica pura (sin dependencias de la web) que resuelve
el requisito RF-03 "Cálculo por tiempo y tarifa".

Reglas de negocio implementadas:
* El cobro se hace **por hora iniciada**: cualquier fracción de hora que haya
  comenzado se cobra completa (redondeo hacia arriba).
  Ej: 90 minutos => se cobran 2 horas.
* Existe un **cobro mínimo configurable** en minutos. Si la estadia real es
  menor que el minimo, se cobra el minimo.
* Todos los calculos se hacen con ``Decimal`` para evitar errores de punto
  flotante con el dinero.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

DOS_DECIMALES = Decimal("0.01")


class ErrorDeCalculo(ValueError):
    """Se lanza cuando los datos violan una regla de negocio del calculo."""


@dataclass(frozen=True)
class Tarifa:
    """Tarifa por hora con cobro minimo opcional (expresado en minutos)."""

    valor_hora: Decimal
    minutos_minimos: int = 0

    def __post_init__(self) -> None:
        if self.valor_hora < 0:
            raise ErrorDeCalculo("El valor de la hora no puede ser negativo.")
        if self.minutos_minimos < 0:
            raise ErrorDeCalculo("Los minutos minimos no pueden ser negativos.")


@dataclass(frozen=True)
class ResultadoCalculo:
    """Desglose del cobro: tiempo estadia, tiempo cobrado y costo final."""

    minutos_estadia: int
    minutos_cobrados: int
    horas_cobradas: int
    costo: Decimal


def _minutos_redondeados_hacia_arriba(entrada: datetime, salida: datetime) -> int:
    """Minutos de estadia, redondeando hacia arriba cualquier fraccion."""
    if salida < entrada:
        raise ErrorDeCalculo(
            "La hora de salida no puede ser anterior a la hora de entrada."
        )
    segundos = (salida - entrada).total_seconds()
    return math.ceil(segundos / 60)


def calcular_costo(
    entrada: datetime, salida: datetime, tarifa: Tarifa
) -> ResultadoCalculo:
    """Calcula el costo del parqueadero para una estadia dada.

    Params
    ------
    entrada : hora de entrada del vehiculo.
    salida  : hora de salida del vehiculo.
    tarifa  : tarifa por hora y cobro minimo aplicable.

    Devuelve un :class:`ResultadoCalculo` con el desglose del cobro.
    """
    minutos_estadia = _minutos_redondeados_hacia_arriba(entrada, salida)
    minutos_cobrados = max(minutos_estadia, tarifa.minutos_minimos)
    horas_cobradas = math.ceil(minutos_cobrados / 60)
    costo = (Decimal(horas_cobradas) * tarifa.valor_hora).quantize(
        DOS_DECIMALES, rounding=ROUND_HALF_UP
    )
    return ResultadoCalculo(
        minutos_estadia=minutos_estadia,
        minutos_cobrados=minutos_cobrados,
        horas_cobradas=horas_cobradas,
        costo=costo,
    )
