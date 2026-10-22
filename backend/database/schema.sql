-- ============================================================
-- SISTEMA DE GESTIÓN DE PARQUEADEROS
-- Esquema de Base de Datos - Dev 1 (Backend & Base de Datos)
-- Sprint 1 - RF-01, RF-02, RF-03, RF-04
-- ============================================================

-- ───────────────────────────────────────────────────────────
-- TABLA: tipos_vehiculo
-- RF-02: Tarifa diferencial por tipo de vehículo
-- ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tipos_vehiculo (
    id              INTEGER       PRIMARY KEY AUTOINCREMENT,
    nombre          VARCHAR(50)   NOT NULL UNIQUE,          -- 'Moto', 'Carro', 'Camión'
    tarifa_hora     DECIMAL(10,2) NOT NULL,                 -- Tarifa en pesos/hora
    descripcion     TEXT,
    activo          BOOLEAN       NOT NULL DEFAULT 1,
    created_at      DATETIME      NOT NULL DEFAULT (DATETIME('now','localtime'))
);

-- Datos iniciales de tarifas (RF-02)
INSERT OR IGNORE INTO tipos_vehiculo (nombre, tarifa_hora, descripcion) VALUES
    ('Moto',   2000.00, 'Motocicletas y bicimotos'),
    ('Carro',  4000.00, 'Automóviles particulares y taxis'),
    ('Camión', 7000.00, 'Vehículos de carga y buses');

-- ───────────────────────────────────────────────────────────
-- TABLA: vehiculos_registro
-- RF-01: Registro de vehículo por placa y hora de entrada
-- ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vehiculos_registro (
    id                  INTEGER       PRIMARY KEY AUTOINCREMENT,
    placa               VARCHAR(10)   NOT NULL,
    tipo_vehiculo_id    INTEGER       NOT NULL REFERENCES tipos_vehiculo(id),
    hora_entrada        DATETIME      NOT NULL DEFAULT (DATETIME('now','localtime')),
    hora_salida         DATETIME,
    tarifa_aplicada     DECIMAL(10,2),                      -- Snapshot tarifa al momento de entrada
    total_cobrado       DECIMAL(10,2),                      -- RF-03: Calculado al salir
    tiempo_parqueado_min INTEGER,                           -- Minutos totales
    estado              VARCHAR(20)   NOT NULL DEFAULT 'ACTIVO' 
                            CHECK(estado IN ('ACTIVO','LIQUIDADO','ANULADO')),
    operador_id         INTEGER,
    observaciones       TEXT,
    created_at          DATETIME      NOT NULL DEFAULT (DATETIME('now','localtime')),
    updated_at          DATETIME      NOT NULL DEFAULT (DATETIME('now','localtime'))
);

-- ───────────────────────────────────────────────────────────
-- ÍNDICES OPTIMIZADOS (Dev 2 - RF-01 Rendimiento ≤ 2s)
-- Garantizan respuesta < 2s en consultas por placa y estado
-- ───────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_placa             ON vehiculos_registro(placa);
CREATE INDEX IF NOT EXISTS idx_placa_estado      ON vehiculos_registro(placa, estado);
CREATE INDEX IF NOT EXISTS idx_hora_entrada      ON vehiculos_registro(hora_entrada);
CREATE INDEX IF NOT EXISTS idx_estado_entrada    ON vehiculos_registro(estado, hora_entrada DESC);
CREATE INDEX IF NOT EXISTS idx_tipo_vehiculo     ON vehiculos_registro(tipo_vehiculo_id);

-- ───────────────────────────────────────────────────────────
-- TABLA: arqueo_caja
-- RF-04: Reporte de arqueo de caja
-- ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS arqueo_caja (
    id                  INTEGER       PRIMARY KEY AUTOINCREMENT,
    fecha_arqueo        DATE          NOT NULL DEFAULT (DATE('now','localtime')),
    turno               VARCHAR(20)   NOT NULL DEFAULT 'DIA' 
                            CHECK(turno IN ('DIA','NOCHE')),
    operador_id         INTEGER,
    total_vehiculos     INTEGER       NOT NULL DEFAULT 0,
    total_motos         INTEGER       NOT NULL DEFAULT 0,
    total_carros        INTEGER       NOT NULL DEFAULT 0,
    total_camiones      INTEGER       NOT NULL DEFAULT 0,
    total_ingresos      DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    ingresos_motos      DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    ingresos_carros     DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    ingresos_camiones   DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    hora_apertura       DATETIME,
    hora_cierre         DATETIME,
    observaciones       TEXT,
    estado              VARCHAR(20)   NOT NULL DEFAULT 'ABIERTO'
                            CHECK(estado IN ('ABIERTO','CERRADO','AJUSTADO')),
    created_at          DATETIME      NOT NULL DEFAULT (DATETIME('now','localtime'))
);

-- ───────────────────────────────────────────────────────────
-- VISTA: vehiculos_activos
-- Consulta optimizada para vehículos en el parqueadero ahora
-- ───────────────────────────────────────────────────────────
CREATE VIEW IF NOT EXISTS vehiculos_activos AS
SELECT
    vr.id,
    vr.placa,
    tv.nombre          AS tipo_vehiculo,
    tv.tarifa_hora,
    vr.hora_entrada,
    CAST(
        (JULIANDAY('now','localtime') - JULIANDAY(vr.hora_entrada)) * 24 * 60
    AS INTEGER)        AS minutos_transcurridos,
    ROUND(
        (JULIANDAY('now','localtime') - JULIANDAY(vr.hora_entrada)) * 24 * tv.tarifa_hora
    , 2)               AS tarifa_acumulada
FROM vehiculos_registro vr
JOIN tipos_vehiculo tv ON vr.tipo_vehiculo_id = tv.id
WHERE vr.estado = 'ACTIVO';

-- ───────────────────────────────────────────────────────────
-- VISTA: reporte_diario
-- RF-04: Base para el arqueo de caja diario
-- ───────────────────────────────────────────────────────────
CREATE VIEW IF NOT EXISTS reporte_diario AS
SELECT
    DATE(vr.hora_salida)                 AS fecha,
    tv.nombre                            AS tipo_vehiculo,
    COUNT(*)                             AS total_vehiculos,
    SUM(vr.total_cobrado)               AS total_ingresos,
    AVG(vr.tiempo_parqueado_min)        AS promedio_minutos,
    MIN(vr.tiempo_parqueado_min)        AS min_tiempo,
    MAX(vr.tiempo_parqueado_min)        AS max_tiempo
FROM vehiculos_registro vr
JOIN tipos_vehiculo tv ON vr.tipo_vehiculo_id = tv.id
WHERE vr.estado = 'LIQUIDADO'
GROUP BY DATE(vr.hora_salida), tv.nombre;
