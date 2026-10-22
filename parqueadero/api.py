"""API web del parqueadero construida con FastAPI.

Expone el RF-03 (calculo por tiempo y tarifa) como endpoint HTTP.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from .calculo import ErrorDeCalculo, Tarifa, calcular_costo
from .tarifas import ErrorVehiculoDesconocido, TipoVehiculo, calcular_costo_por_tipo
from backend.main import AUTH_RESPONSES, AuthenticatedUser, init_db, require_roles


@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="API del Parqueadero",
    description="Cálculo de tarifa por tiempo y tipo de vehículo.",
    version="1.0.0",
    lifespan=lifespan,
)


class CalculoRequest(BaseModel):
    """Cuerpo de la petición para calcular una tarifa."""

    hora_entrada: datetime = Field(..., description="Hora de entrada del vehículo.")
    hora_salida: datetime = Field(..., description="Hora de salida del vehículo.")
    valor_hora: Decimal = Field(..., gt=0, description="Valor de la tarifa por hora.")
    minutos_minimos: int = Field(
        0, ge=0, description="Cobro mínimo en minutos (por defecto 0)."
    )


class CalculoResponse(BaseModel):
    """Respuesta con el desglose del cobro."""

    minutos_estadia: int
    minutos_cobrados: int
    horas_cobradas: int
    costo: Decimal


@app.get("/salud")
def salud() -> dict:
    """Endpoint sencillo de salud para verificar que la API está viva."""
    return {"estado": "ok"}


@app.post(
    "/calcular-tarifa",
    response_model=CalculoResponse,
    responses=AUTH_RESPONSES,
)
def calcular_tarifa(
    peticion: CalculoRequest,
    _user: AuthenticatedUser = Depends(require_roles("admin", "operador", "cliente")),
) -> CalculoResponse:
    """Calcula el costo del parqueadero por tiempo transcurrido."""
    try:
        resultado = calcular_costo(
            entrada=peticion.hora_entrada,
            salida=peticion.hora_salida,
            tarifa=Tarifa(
                valor_hora=peticion.valor_hora,
                minutos_minimos=peticion.minutos_minimos,
            ),
        )
    except ErrorDeCalculo as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return CalculoResponse(
        minutos_estadia=resultado.minutos_estadia,
        minutos_cobrados=resultado.minutos_cobrados,
        horas_cobradas=resultado.horas_cobradas,
        costo=resultado.costo,
    )


class CalculoVehiculoRequest(BaseModel):
    """Petición que identifica el vehículo por su tipo (RF-02)."""

    tipo_vehiculo: TipoVehiculo = Field(
        ..., description="Tipo de vehículo (carro, moto, camioneta, bus, camion)."
    )
    hora_entrada: datetime = Field(..., description="Hora de entrada del vehículo.")
    hora_salida: datetime = Field(..., description="Hora de salida del vehículo.")


@app.post(
    "/calcular-tarifa-vehiculo",
    response_model=CalculoResponse,
    responses=AUTH_RESPONSES,
)
def calcular_tarifa_vehiculo(
    peticion: CalculoVehiculoRequest,
    _user: AuthenticatedUser = Depends(require_roles("admin", "operador", "cliente")),
) -> CalculoResponse:
    """Calcula el costo usando la tarifa diferencial según el tipo de vehículo."""
    try:
        resultado = calcular_costo_por_tipo(
            entrada=peticion.hora_entrada,
            salida=peticion.hora_salida,
            tipo=peticion.tipo_vehiculo,
        )
    except ErrorVehiculoDesconocido as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ErrorDeCalculo as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return CalculoResponse(
        minutos_estadia=resultado.minutos_estadia,
        minutos_cobrados=resultado.minutos_cobrados,
        horas_cobradas=resultado.horas_cobradas,
        costo=resultado.costo,
    )


@app.get("/tarifas", responses=AUTH_RESPONSES)
def listar_tarifas(
    _user: AuthenticatedUser = Depends(require_roles("admin", "operador", "cliente")),
) -> list[dict]:
    """Lista las tarifas diferenciales por tipo de vehículo (RF-02)."""
    from .tarifas import CATALOGO_DEFECTO

    return [
        {
            "tipo_vehiculo": detalle.tipo.value,
            "descripcion": detalle.descripcion,
            "valor_hora": str(detalle.tarifa.valor_hora),
            "minutos_minimos": detalle.tarifa.minutos_minimos,
        }
        for detalle in (
            CATALOGO_DEFECTO.detalle_para(t) for t in CATALOGO_DEFECTO.tipos()
        )
    ]
