"""RF-02: Tipos de vehículo y tarifa diferencial.

Define los tipos de vehículo del parqueadero y la tarifa diferencial que
le corresponde a cada uno (distinto valor por hora y cobro mínimo).

Este módulo **no reimplementa** el cálculo: reutiliza la lógica del RF-03
(:func:`parqueadero.calculo.calcular_costo`), aportando únicamente la
relación `tipo de vehículo -> tarifa`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

from .calculo import ErrorDeCalculo, ResultadoCalculo, Tarifa, calcular_costo


class ErrorVehiculoDesconocido(KeyError):
    """Se lanza cuando se pide la tarifa de un tipo de vehículo inexistente."""


class TipoVehiculo(str, Enum):
    """Tipos de vehículo soportados por el parqueadero."""

    CARRO = "carro"
    MOTO = "moto"
    CAMIONETA = "camioneta"
    BUS = "bus"
    CAMION = "camion"


@dataclass(frozen=True)
class TarifaVehiculo:
    """Tarifa diferencial asignada a un tipo de vehículo."""

    tipo: TipoVehiculo
    tarifa: Tarifa
    descripcion: str


class CatalogoTarifas:
    """Catálogo de tarifas por tipo de vehículo.

    Permite consultar la tarifa de un vehículo y modificarla (por ejemplo
    desde una base de datos o un archivo de configuración).
    """

    def __init__(self, tarifas: dict[TipoVehiculo, TarifaVehiculo] | None = None):
        self._tarifas: dict[TipoVehiculo, TarifaVehiculo] = dict(
            tarifas if tarifas is not None else TARIFAS_DEFECTO
        )

    def tarifa_para(self, tipo: TipoVehiculo | str) -> Tarifa:
        """Devuelve la :class:`Tarifa` (RF-03) asociada a un tipo de vehículo."""
        clave = _coerce_tipo(tipo)
        return self._tarifas[clave].tarifa

    def detalle_para(self, tipo: TipoVehiculo | str) -> TarifaVehiculo:
        """Devuelve el registro completo (:class:`TarifaVehiculo`) del vehículo."""
        clave = _coerce_tipo(tipo)
        return self._tarifas[clave]

    def registrar(self, detalle: TarifaVehiculo) -> None:
        """Agrega o reemplaza la tarifa de un tipo de vehículo."""
        self._tarifas[detalle.tipo] = detalle

    def tipos(self) -> list[TipoVehiculo]:
        """Lista los tipos de vehículo con tarifa configurada."""
        return list(self._tarifas)


def _coerce_tipo(tipo: TipoVehiculo | str) -> TipoVehiculo:
    """Convierte un string a :class:`TipoVehiculo`, validando que exista."""
    if isinstance(tipo, TipoVehiculo):
        return tipo
    try:
        return TipoVehiculo(str(tipo).strip().lower())
    except ValueError as exc:
        validos = ", ".join(t.value for t in TipoVehiculo)
        raise ErrorVehiculoDesconocido(
            f"Tipo de vehículo desconocido: {tipo!r}. Válidos: {validos}."
        ) from exc


def calcular_costo_por_tipo(
    entrada: datetime,
    salida: datetime,
    tipo: TipoVehiculo | str,
    catalogo: CatalogoTarifas | None = None,
) -> ResultadoCalculo:
    """Calcula el costo usando la tarifa diferencial del tipo de vehículo.

    Combina el RF-02 (tarifa según vehículo) con el RF-03 (cálculo por tiempo).
    """
    cat = catalogo if catalogo is not None else CATALOGO_DEFECTO
    tarifa = cat.tarifa_para(tipo)
    return calcular_costo(entrada, salida, tarifa)


# Tarifas por defecto del parqueadero (valores de ejemplo, configurables).
TARIFAS_DEFECTO: dict[TipoVehiculo, TarifaVehiculo] = {
    TipoVehiculo.CARRO: TarifaVehiculo(
        tipo=TipoVehiculo.CARRO,
        tarifa=Tarifa(valor_hora=Decimal("3000"), minutos_minimos=30),
        descripcion="Automóvil particular",
    ),
    TipoVehiculo.MOTO: TarifaVehiculo(
        tipo=TipoVehiculo.MOTO,
        tarifa=Tarifa(valor_hora=Decimal("2000"), minutos_minimos=30),
        descripcion="Motocicleta",
    ),
    TipoVehiculo.CAMIONETA: TarifaVehiculo(
        tipo=TipoVehiculo.CAMIONETA,
        tarifa=Tarifa(valor_hora=Decimal("3500"), minutos_minimos=30),
        descripcion="Camioneta / SUV",
    ),
    TipoVehiculo.BUS: TarifaVehiculo(
        tipo=TipoVehiculo.BUS,
        tarifa=Tarifa(valor_hora=Decimal("6000"), minutos_minimos=60),
        descripcion="Bus / colectivo",
    ),
    TipoVehiculo.CAMION: TarifaVehiculo(
        tipo=TipoVehiculo.CAMION,
        tarifa=Tarifa(valor_hora=Decimal("8000"), minutos_minimos=60),
        descripcion="Camión de carga",
    ),
}

# Catálogo global por defecto.
CATALOGO_DEFECTO = CatalogoTarifas(TARIFAS_DEFECTO)

__all__ = [
    "CATALOGO_DEFECTO",
    "CatalogoTarifas",
    "ErrorDeCalculo",
    "ErrorVehiculoDesconocido",
    "TARIFAS_DEFECTO",
    "TarifaVehiculo",
    "TipoVehiculo",
    "calcular_costo_por_tipo",
]
