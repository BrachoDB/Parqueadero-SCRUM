"""API web del parqueadero construida con FastAPI.

Expone el RF-03 (calculo por tiempo y tarifa) como endpoint HTTP.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .calculo import ErrorDeCalculo, Tarifa, calcular_costo

app = FastAPI(
    title="API del Parqueadero",
    description="Cálculo de tarifa por tiempo y tipo de vehículo.",
    version="1.0.0",
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


@app.post("/calcular-tarifa", response_model=CalculoResponse)
def calcular_tarifa(peticion: CalculoRequest) -> CalculoResponse:
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
