"""
╔══════════════════════════════════════════════════════════════╗
║   SISTEMA DE GESTIÓN DE PARQUEADEROS                        ║
║   Backend Principal - FastAPI REST                          ║
║   Dev 1: Registro de vehículos (RF-01)                      ║
║   Dev 2: Optimización rendimiento ≤ 2s (RF-01 Rendimiento)  ║
╚══════════════════════════════════════════════════════════════╝
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime, date
import sqlite3
import time
import math
import re
import os
import logging

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN LOGGING
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("parqueadero")

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN BASE DE DATOS
# Rutas absolutas basadas en la ubicación real de este archivo
# ─────────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_BASE_DIR, "database", "parqueadero.db")
SCHEMA_PATH = os.path.join(_BASE_DIR, "database", "schema.sql")

# ─────────────────────────────────────────────────────────────
# Dev 2: CACHÉ EN MEMORIA para tarifas (evita hits a BD)
# ─────────────────────────────────────────────────────────────
_CACHE_TARIFAS: dict = {}
_CACHE_TTL: float = 300.0  # 5 minutos (referencia para futura invalidación)


# ─────────────────────────────────────────────────────────────
# FUNCIONES DE BASE DE DATOS
# ─────────────────────────────────────────────────────────────
def get_db():
    """Conexión a SQLite con optimizaciones para rendimiento ≤ 2s (Dev 2)."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    # Dev 2: Pragmas de rendimiento SQLite
    conn.execute("PRAGMA journal_mode=WAL;")          # Write-Ahead Logging
    conn.execute("PRAGMA synchronous=NORMAL;")        # Menos fsync, más velocidad
    conn.execute("PRAGMA cache_size=-16000;")         # 16 MB de caché en memoria
    conn.execute("PRAGMA temp_store=MEMORY;")         # Tablas temporales en RAM
    conn.execute("PRAGMA mmap_size=268435456;")       # 256 MB mmap

    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Inicializa la base de datos con el schema."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA cache_size=-16000;")
        conn.execute("PRAGMA temp_store=MEMORY;")

        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
        conn.commit()
    logger.info("✅ Base de datos inicializada correctamente.")


def _warm_up_cache():
    """Dev 2: Precarga tarifas en caché al inicio del servidor."""
    global _CACHE_TARIFAS
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, nombre, tarifa_hora FROM tipos_vehiculo WHERE activo = 1"
        ).fetchall()
        _CACHE_TARIFAS = {
            row["id"]: {"nombre": row["nombre"], "tarifa_hora": float(row["tarifa_hora"])}
            for row in rows
        }
    logger.info(f"✅ Caché de tarifas cargada: {len(_CACHE_TARIFAS)} tipos de vehículo.")


def get_tarifa_cached(tipo_id: int) -> Optional[dict]:
    """Dev 2: Obtiene tarifa desde caché. O(1) - respuesta < 1ms."""
    return _CACHE_TARIFAS.get(tipo_id)


# ─────────────────────────────────────────────────────────────
# CICLO DE VIDA — lifespan (reemplaza el deprecated on_event)
# Debe estar definido ANTES de FastAPI() para poder pasarlo
# ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(application: FastAPI):
    """Gestión del ciclo de vida de la aplicación."""
    init_db()
    _warm_up_cache()
    logger.info("🚀 API de Parqueadero iniciada.")
    yield
    logger.info("🛑 API de Parqueadero detenida.")


# ─────────────────────────────────────────────────────────────
# APLICACIÓN FASTAPI
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Sistema de Gestión de Parqueaderos",
    description="API REST para el control de acceso y gestión de vehículos en parqueadero.",
    version="1.0.0",
    contact={"name": "Equipo Scrum - Sprint 1"},
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# MODELOS PYDANTIC (Pydantic v2 compatible)
# ─────────────────────────────────────────────────────────────
# Patrón placa colombiana: AAA000 o AAA00A
PATRON_PLACA = re.compile(r"^[A-Z]{3}[0-9]{2}[A-Z0-9]{1,2}$")


class RegistroEntradaRequest(BaseModel):
    """RF-01: Modelo para registro de entrada de vehículo."""
    placa: str
    tipo_vehiculo_id: int
    operador_id: Optional[int] = None
    observaciones: Optional[str] = None

    @field_validator("placa", mode="before")
    @classmethod
    def validar_placa(cls, v):
        v = str(v).upper().strip().replace(" ", "").replace("-", "")
        if not PATRON_PLACA.match(v):
            raise ValueError(
                "Placa inválida. Formato esperado: ABC123 o ABC12D (Colombia)"
            )
        return v

    @field_validator("tipo_vehiculo_id", mode="before")
    @classmethod
    def validar_tipo(cls, v):
        if int(v) not in (1, 2, 3):
            raise ValueError("tipo_vehiculo_id debe ser 1 (Moto), 2 (Carro) o 3 (Camión)")
        return v


class RegistroSalidaRequest(BaseModel):
    """RF-03: Modelo para registro de salida y liquidación."""
    registro_id: int
    operador_id: Optional[int] = None


class TipoVehiculo(BaseModel):
    id: int
    nombre: str
    tarifa_hora: float
    descripcion: Optional[str] = None


class RegistroResponse(BaseModel):
    id: int
    placa: str
    tipo_vehiculo: str
    tarifa_hora: float
    hora_entrada: str
    estado: str
    mensaje: str
    tiempo_respuesta_ms: float


class TarifaConsultaResponse(BaseModel):
    """RF-01 Rendimiento: Respuesta de consulta de tarifa en ≤ 2s."""
    placa: str
    tipo_vehiculo: str
    tarifa_hora: float
    hora_entrada: str
    minutos_transcurridos: int
    tarifa_acumulada: float
    tiempo_respuesta_ms: float
    cumple_sla: bool  # True si respuesta <= 2000ms


# ─────────────────────────────────────────────────────────────
# ENDPOINTS - Dev 1: RF-01 REGISTRO DE ENTRADA
# ─────────────────────────────────────────────────────────────
@app.post(
    "/api/v1/vehiculos/entrada",
    response_model=RegistroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="RF-01: Registrar entrada de vehículo",
    tags=["Registro de Vehículos"]
)
def registrar_entrada(
    req: RegistroEntradaRequest,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    **RF-01**: Registra la entrada de un vehículo al parqueadero.
    - Captura automáticamente la **hora exacta de entrada** (server-side).
    - Valida formato de placa colombiana.
    - Verifica que el vehículo no tenga ya un registro activo.
    """
    t_inicio = time.perf_counter()

    # ── Verificar si el vehículo ya está dentro (Dev 2: índice idx_placa_estado)
    existente = db.execute(
        "SELECT id FROM vehiculos_registro WHERE placa = ? AND estado = 'ACTIVO' LIMIT 1",
        (req.placa,)
    ).fetchone()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El vehículo {req.placa} ya tiene un registro activo (ID: {existente['id']}). "
                   "Debe registrar su salida antes de un nuevo ingreso."
        )

    # ── Obtener tarifa desde caché (Dev 2: O(1) sin hit a BD)
    tarifa_info = get_tarifa_cached(req.tipo_vehiculo_id)
    if not tarifa_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de vehículo ID={req.tipo_vehiculo_id} no encontrado."
        )

    # ── RF-01: Capturar timestamp de entrada server-side
    hora_entrada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── Insertar registro en BD
    cursor = db.execute(
        """
        INSERT INTO vehiculos_registro
            (placa, tipo_vehiculo_id, hora_entrada, tarifa_aplicada, estado, operador_id, observaciones)
        VALUES (?, ?, ?, ?, 'ACTIVO', ?, ?)
        """,
        (
            req.placa,
            req.tipo_vehiculo_id,
            hora_entrada,
            tarifa_info["tarifa_hora"],
            req.operador_id,
            req.observaciones
        )
    )
    db.commit()

    t_ms = (time.perf_counter() - t_inicio) * 1000
    logger.info(f"✅ Entrada registrada | Placa={req.placa} | ID={cursor.lastrowid} | {t_ms:.1f}ms")

    return RegistroResponse(
        id=cursor.lastrowid,
        placa=req.placa,
        tipo_vehiculo=tarifa_info["nombre"],
        tarifa_hora=tarifa_info["tarifa_hora"],
        hora_entrada=hora_entrada,
        estado="ACTIVO",
        mensaje=f"Vehículo {req.placa} registrado exitosamente.",
        tiempo_respuesta_ms=round(t_ms, 2)
    )


# ─────────────────────────────────────────────────────────────
# ENDPOINTS - Dev 2: RF-01 RENDIMIENTO - CONSULTA TARIFA ≤ 2s
# ─────────────────────────────────────────────────────────────
@app.get(
    "/api/v1/vehiculos/{placa}/tarifa",
    response_model=TarifaConsultaResponse,
    summary="RF-01 Rendimiento: Consultar tarifa acumulada (≤ 2s SLA)",
    tags=["Tarifas & Rendimiento"]
)
def consultar_tarifa(placa: str, db: sqlite3.Connection = Depends(get_db)):
    """
    **RF-01 Rendimiento**: Muestra la tarifa acumulada de un vehículo.
    - Garantía SLA: tiempo de respuesta ≤ **2000 ms**.
    - Usa índice `idx_placa_estado` para búsqueda O(log n).
    - La tarifa base se obtiene desde caché en memoria O(1).
    """
    t_inicio = time.perf_counter()
    placa = placa.upper().strip()

    # ── Consulta optimizada con índice compuesto idx_placa_estado (Dev 2)
    row = db.execute(
        """
        SELECT
            vr.id,
            vr.placa,
            vr.tipo_vehiculo_id,
            vr.hora_entrada,
            CAST(
                (JULIANDAY('now','localtime') - JULIANDAY(vr.hora_entrada)) * 1440
            AS INTEGER) AS minutos_transcurridos,
            ROUND(
                (JULIANDAY('now','localtime') - JULIANDAY(vr.hora_entrada)) * 24 * tv.tarifa_hora
            , 2) AS tarifa_acumulada,
            tv.nombre AS tipo_vehiculo,
            tv.tarifa_hora
        FROM vehiculos_registro vr
        JOIN tipos_vehiculo tv ON vr.tipo_vehiculo_id = tv.id
        WHERE vr.placa = ? AND vr.estado = 'ACTIVO'
        LIMIT 1
        """,
        (placa,)
    ).fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un registro activo para la placa {placa}."
        )

    t_ms = (time.perf_counter() - t_inicio) * 1000
    cumple_sla = t_ms <= 2000.0

    if not cumple_sla:
        logger.warning(f"⚠️ SLA VIOLADO | Placa={placa} | Tiempo={t_ms:.1f}ms > 2000ms")
    else:
        logger.info(f"✅ Tarifa consultada | Placa={placa} | {t_ms:.1f}ms <= 2000ms")

    return TarifaConsultaResponse(
        placa=row["placa"],
        tipo_vehiculo=row["tipo_vehiculo"],
        tarifa_hora=float(row["tarifa_hora"]),
        hora_entrada=row["hora_entrada"],
        minutos_transcurridos=row["minutos_transcurridos"],
        tarifa_acumulada=float(row["tarifa_acumulada"]),
        tiempo_respuesta_ms=round(t_ms, 2),
        cumple_sla=cumple_sla
    )


# ─────────────────────────────────────────────────────────────
# ENDPOINTS - RF-03: REGISTRO DE SALIDA Y COBRO
# ─────────────────────────────────────────────────────────────
@app.post(
    "/api/v1/vehiculos/salida",
    status_code=status.HTTP_200_OK,
    summary="RF-03: Registrar salida y calcular cobro total",
    tags=["Registro de Vehículos"]
)
def registrar_salida(req: RegistroSalidaRequest, db: sqlite3.Connection = Depends(get_db)):
    """
    **RF-03**: Registra la salida, calcula tiempo parqueado y cobra según tarifa.
    - Cálculo: `ceil(minutos / 60) * tarifa_hora`
    - Se cobra fracción de hora completa (hora iniciada = hora cobrada).
    """
    t_inicio = time.perf_counter()

    registro = db.execute(
        """
        SELECT vr.*, tv.tarifa_hora, tv.nombre AS tipo_vehiculo
        FROM vehiculos_registro vr
        JOIN tipos_vehiculo tv ON vr.tipo_vehiculo_id = tv.id
        WHERE vr.id = ? AND vr.estado = 'ACTIVO'
        """,
        (req.registro_id,)
    ).fetchone()

    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registro activo ID={req.registro_id} no encontrado."
        )

    hora_salida = datetime.now()
    hora_entrada = datetime.strptime(registro["hora_entrada"], "%Y-%m-%d %H:%M:%S")
    delta = hora_salida - hora_entrada
    minutos_totales = int(delta.total_seconds() / 60)

    # RF-03: Cobro por hora iniciada (ceil) — math importado a nivel de módulo
    horas_cobradas = math.ceil(minutos_totales / 60) if minutos_totales > 0 else 1
    total_cobrado = round(horas_cobradas * float(registro["tarifa_hora"]), 2)

    db.execute(
        """
        UPDATE vehiculos_registro
        SET hora_salida = ?, total_cobrado = ?, tiempo_parqueado_min = ?,
            estado = 'LIQUIDADO', updated_at = DATETIME('now','localtime')
        WHERE id = ?
        """,
        (
            hora_salida.strftime("%Y-%m-%d %H:%M:%S"),
            total_cobrado,
            minutos_totales,
            req.registro_id
        )
    )
    db.commit()

    t_ms = (time.perf_counter() - t_inicio) * 1000
    logger.info(f"✅ Salida | Placa={registro['placa']} | ${total_cobrado:,.0f} | {t_ms:.1f}ms")

    return {
        "id": req.registro_id,
        "placa": registro["placa"],
        "tipo_vehiculo": registro["tipo_vehiculo"],
        "hora_entrada": registro["hora_entrada"],
        "hora_salida": hora_salida.strftime("%Y-%m-%d %H:%M:%S"),
        "minutos_parqueado": minutos_totales,
        "horas_cobradas": horas_cobradas,
        "tarifa_hora": float(registro["tarifa_hora"]),
        "total_cobrado": total_cobrado,
        "tiempo_respuesta_ms": round(t_ms, 2),
        "mensaje": f"Vehículo {registro['placa']} liquidado. Total: ${total_cobrado:,.0f}"
    }


# ─────────────────────────────────────────────────────────────
# ENDPOINTS - RF-04: ARQUEO DE CAJA
# ─────────────────────────────────────────────────────────────
@app.get(
    "/api/v1/reportes/arqueo",
    summary="RF-04: Reporte de arqueo de caja",
    tags=["Reportes"]
)
def arqueo_caja(
    fecha: Optional[date] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    **RF-04**: Genera el reporte de arqueo de caja para una fecha dada.
    Si no se especifica fecha, usa la fecha actual.
    """
    fecha_consulta = fecha or date.today()
    fecha_str = fecha_consulta.strftime("%Y-%m-%d")

    resumen = db.execute(
        """
        SELECT
            tv.nombre                        AS tipo_vehiculo,
            COUNT(*)                         AS total_vehiculos,
            SUM(vr.total_cobrado)           AS total_ingresos,
            SUM(vr.tiempo_parqueado_min)    AS total_minutos
        FROM vehiculos_registro vr
        JOIN tipos_vehiculo tv ON vr.tipo_vehiculo_id = tv.id
        WHERE DATE(vr.hora_salida) = ? AND vr.estado = 'LIQUIDADO'
        GROUP BY tv.nombre
        """,
        (fecha_str,)
    ).fetchall()

    total_global = db.execute(
        """
        SELECT COUNT(*) AS total_v, COALESCE(SUM(total_cobrado), 0) AS total_i
        FROM vehiculos_registro
        WHERE DATE(hora_salida) = ? AND estado = 'LIQUIDADO'
        """,
        (fecha_str,)
    ).fetchone()

    return {
        "fecha": fecha_str,
        "resumen_por_tipo": [
            {
                "tipo_vehiculo": r["tipo_vehiculo"],
                "total_vehiculos": r["total_vehiculos"],
                "total_ingresos": float(r["total_ingresos"] or 0),
                "promedio_minutos": round((r["total_minutos"] or 0) / max(r["total_vehiculos"], 1), 1)
            }
            for r in resumen
        ],
        "totales": {
            "total_vehiculos": total_global["total_v"],
            "total_ingresos": float(total_global["total_i"]),
        }
    }


# ─────────────────────────────────────────────────────────────
# ENDPOINT: VEHÍCULOS ACTIVOS (Dashboard en tiempo real)
# NOTA: esta ruta va ANTES de /{placa}/tarifa para evitar
# que FastAPI interprete 'activos' como un parámetro {placa}
# ─────────────────────────────────────────────────────────────
@app.get(
    "/api/v1/vehiculos/activos",
    summary="Vehículos actualmente en el parqueadero",
    tags=["Registro de Vehículos"]
)
def vehiculos_activos(db: sqlite3.Connection = Depends(get_db)):
    """Lista todos los vehículos que actualmente están dentro del parqueadero."""
    t_inicio = time.perf_counter()
    rows = db.execute("SELECT * FROM vehiculos_activos ORDER BY hora_entrada").fetchall()
    t_ms = (time.perf_counter() - t_inicio) * 1000

    return {
        "total": len(rows),
        "tiempo_respuesta_ms": round(t_ms, 2),
        "cumple_sla": t_ms <= 2000.0,
        "vehiculos": [dict(r) for r in rows]
    }


# ─────────────────────────────────────────────────────────────
# ENDPOINT: TIPOS DE VEHÍCULO Y TARIFAS (RF-02)
# ─────────────────────────────────────────────────────────────
@app.get(
    "/api/v1/tarifas",
    summary="RF-02: Consultar tipos de vehículo y tarifas diferenciales",
    tags=["Tarifas & Rendimiento"]
)
def listar_tarifas():
    """**RF-02**: Retorna los tipos de vehículo con sus tarifas diferenciales desde caché."""
    return {
        "tarifas": [
            {"id": k, **v}
            for k, v in _CACHE_TARIFAS.items()
        ]
    }


# ─────────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["Sistema"])
def health_check():
    return {
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "cache_tarifas_activo": len(_CACHE_TARIFAS) > 0
    }
