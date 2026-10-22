# 🚗 Sistema de Gestión de Parqueaderos

<div align="center">

![Estado del Proyecto](https://img.shields.io/badge/Estado-Sprint%201%20Activo-brightgreen?style=for-the-badge)
![Metodología](https://img.shields.io/badge/Metodología-SCRUM-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-yellow?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal?style=for-the-badge&logo=fastapi)
![SQLite](https://img.shields.io/badge/Base%20de%20Datos-SQLite-blue?style=for-the-badge&logo=sqlite)
![SLA](https://img.shields.io/badge/SLA-≤%202%20segundos-critical?style=for-the-badge)

**Sistema automatizado de control de acceso y gestión de vehículos en parqueadero,
desarrollado con metodología SCRUM y arquitectura REST API.**

</div>

---

## 📋 Tabla de Contenidos

1. [Descripción General](#-descripción-general)
2. [Equipo Scrum](#-equipo-scrum)
3. [Requerimientos Funcionales](#-requerimientos-funcionales)
4. [Arquitectura del Sistema](#-arquitectura-del-sistema)
5. [Sprint Planning](#-sprint-planning)
6. [Instalación y Ejecución](#-instalación-y-ejecución)
7. [Endpoints de la API](#-endpoints-de-la-api)
8. [Estructura del Proyecto](#-estructura-del-proyecto)
9. [Criterios de Aceptación (DoD)](#-criterios-de-aceptación-dod)
10. [Pruebas de Rendimiento](#-pruebas-de-rendimiento)

---

## 🏢 Descripción General

El **Sistema de Gestión de Parqueaderos** es una solución backend desarrollada en **Python/FastAPI** que automatiza el control de acceso vehicular. Permite registrar la entrada y salida de vehículos, calcular cobros según tarifas diferenciales por tipo de vehículo y generar reportes de arqueo de caja.

### Características Clave

| Característica | Descripción |
|---|---|
| ⚡ **Rendimiento** | Tiempo de respuesta garantizado **≤ 2 segundos** (SLA RF-01) |
| 🎯 **Precisión** | Captura de timestamp de entrada generado **server-side** |
| 🚗 **Tarifa Diferencial** | Tarifas distintas para Moto, Carro y Camión (RF-02) |
| 📊 **Reportes** | Arqueo de caja diario con desglose por tipo de vehículo (RF-04) |
| 🔒 **Validación** | Validación de formato de placa colombiana (ABC123 / ABC12D) |
| 🧠 **Caché** | Caché en memoria para tarifas → respuesta < 1ms |
| 🗃️ **Índices BD** | Índices compuestos en SQLite para búsqueda O(log n) |

---

## 👥 Equipo Scrum

El proyecto es desarrollado por un equipo Scrum de **5 integrantes** siguiendo los roles y ceremonias establecidos en el framework Scrum.

### Organigrama del Equipo

```
┌─────────────────────────────────────────────────────────┐
│                   EQUIPO SCRUM                          │
│               Parqueadero - Sprint 1                    │
├──────────────┬──────────────────────────────────────────┤
│  PRODUCT     │  SCRUM                                   │
│  OWNER (PO)  │  MASTER (SM)                             │
│              │                                          │
│  • Valida    │  • Orquesta el equipo                    │
│    historias │  • Remueve impedimentos                  │
│  • Define    │  • Asegura la calidad                    │
│    el DoD    │  • Monitorea el burndown                 │
│  • Prioriza  │                                          │
│    el backlog│                                          │
├──────────────┴──────────────────────────────────────────┤
│              EQUIPO DE DESARROLLO                        │
│  ┌───────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │    Dev 1      │  │    Dev 2    │  │    Dev 3     │  │
│  │  Backend &    │  │ Optimización│  │Documentación │  │
│  │  Base Datos   │  │ Rendimiento │  │ & Integración│  │
│  │               │  │             │  │              │  │
│  │ RF-01         │  │ SLA ≤ 2s   │  │ README.md    │  │
│  │ Esquema BD    │  │ Caché       │  │ Estructura   │  │
│  │ API REST      │  │ Índices BD  │  │ Scrum        │  │
│  └───────────────┘  └─────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Responsabilidades por Rol

#### 🎯 Product Owner (PO)
- Define y prioriza el **Product Backlog**
- Valida las **historias de usuario** y los criterios DoD
- Aprueba los entregables de cada Sprint
- Representa los intereses del negocio (operadores de parqueadero)

#### 🏃 Scrum Master (SM)
- **Facilita** las ceremonias Scrum (Planning, Daily, Review, Retrospectiva)
- **Remueve impedimentos** técnicos y organizativos
- **Garantiza** el cumplimiento del SLA de 2 segundos
- Monitorea el **Sprint Burndown** y la velocidad del equipo

#### 💻 Desarrollador 1 — Backend & Base de Datos
- Diseño del **esquema relacional** (SQLite)
- Implementación de la **API REST** con FastAPI
- Lógica de **registro de entrada** (RF-01) y salida/liquidación (RF-03)
- Validación de **formato de placa** colombiana

#### ⚡ Desarrollador 2 — Optimización & Rendimiento
- Implementación de **caché en memoria** para tarifas (O(1))
- Configuración de **pragmas SQLite** (WAL, caché 16MB)
- Creación de **índices compuestos** para búsquedas O(log n)
- **Pruebas de carga** y validación del SLA ≤ 2 segundos

#### 📝 Desarrollador 3 — Documentación & Integración
- Redacción del `README.md` oficial del proyecto
- Documentación de **endpoints API** (OpenAPI/Swagger)
- Estructura del proyecto y **guía de instalación**
- Integración de la documentación **Scrum** con los RF

---

## 📌 Requerimientos Funcionales

El sistema implementa los siguientes requerimientos funcionales, definidos y priorizados por el **Product Owner**:

### RF-01 — Registro de Vehículo por Placa y Hora de Entrada

> **Historia de usuario:** *Como operador del parqueadero, quiero registrar un vehículo ingresando su placa para que el sistema capture automáticamente la hora exacta de entrada.*

| Atributo | Detalle |
|---|---|
| **ID** | RF-01 |
| **Nombre** | Registro de Vehículo |
| **Prioridad** | 🔴 Alta |
| **Sprint** | Sprint 1 |
| **Responsable** | Dev 1 |

**Criterios de Aceptación:**
- ✅ El sistema acepta la placa del vehículo como parámetro de entrada
- ✅ La **hora de entrada se genera server-side** (no puede ser modificada por el cliente)
- ✅ Se valida el formato de placa colombiana (ej: `ABC123`, `ABC12D`)
- ✅ Si el vehículo ya está registrado como activo, se rechaza el duplicado (HTTP 409)
- ✅ El registro queda persistido en la base de datos

---

### RF-01 (Rendimiento) — Tiempo Máximo 2 Segundos para Mostrar Tarifa

> **Historia de usuario:** *Como operador, quiero que el sistema muestre la tarifa del vehículo en un tiempo máximo de 2 segundos para no generar cuellos de botella en la entrada.*

| Atributo | Detalle |
|---|---|
| **ID** | RF-01-PERF |
| **Nombre** | SLA de Rendimiento |
| **Prioridad** | 🔴 Alta |
| **Sprint** | Sprint 1 |
| **Responsable** | Dev 2 |
| **Métrica** | Tiempo de respuesta ≤ **2000 ms** |

**Mecanismos de Optimización Implementados:**

| Capa | Técnica |
|---|---|
| **1. Caché Memoria** | Tarifas precargadas al inicio · Consulta O(1) sin hit a BD |
| **2. Índices SQLite** | `idx_placa_estado` compuesto · Búsqueda O(log n) |
| **3. SQLite Pragmas** | WAL mode · `cache_size=-16000` (16 MB RAM) · `temp_store=MEMORY` |
| **4. Monitoreo** | Respuesta incluye `tiempo_respuesta_ms` y `cumple_sla` · Alertas en log |

**Criterios de Aceptación:**
- ✅ Endpoint `/api/v1/vehiculos/{placa}/tarifa` responde en **≤ 2000 ms**
- ✅ Campo `cumple_sla: true` en respuesta cuando se cumple el SLA
- ✅ **Advertencia en log** si alguna consulta supera el límite
- ✅ Bajo carga de 10 consultas concurrentes, el máximo sigue siendo ≤ 2s

---

### RF-02 — Tipo de Vehículo / Tarifa Diferencial

> **Historia de usuario:** *Como administrador, quiero definir tarifas diferentes según el tipo de vehículo para maximizar los ingresos de manera justa.*

| Tipo de Vehículo | Tarifa/Hora | Descripción |
|---|---|---|
| 🏍️ **Moto** | $2.000 COP | Motocicletas y bicimotos |
| 🚗 **Carro** | $4.000 COP | Automóviles particulares y taxis |
| 🚛 **Camión** | $7.000 COP | Vehículos de carga y buses |

**Criterios de Aceptación:**
- ✅ El sistema distingue al menos 3 tipos de vehículo
- ✅ Cada tipo tiene tarifa independiente configurable en BD
- ✅ La tarifa al momento de entrada queda guardada como snapshot
- ✅ Cambios en tarifa no afectan vehículos ya dentro del parqueadero

---

### RF-03 — Cálculo por Tiempo y Tarifa

> **Historia de usuario:** *Como cajero, quiero que el sistema calcule automáticamente el monto a cobrar según el tiempo de permanencia y la tarifa.*

**Fórmula de Cálculo:**
```
tiempo_parqueado  = hora_salida - hora_entrada   (en minutos)
horas_cobradas    = ceil(tiempo_parqueado / 60)  (hora iniciada = hora cobrada)
total_cobrado     = horas_cobradas × tarifa_hora
```

**Ejemplo:**
```
Vehículo: Carro  | Tarifa: $4.000/hora
Entrada:  09:00  | Salida: 11:20  → 140 min → ceil(140/60) = 3 horas
Total:    3 × $4.000 = $12.000 COP
```

**Criterios de Aceptación:**
- ✅ Cálculo automático al registrar la salida
- ✅ Se cobra por hora iniciada (fracción = hora completa)
- ✅ El resultado incluye minutos, horas cobradas y total en COP
- ✅ Registro histórico completo de la transacción

---

### RF-04 — Reporte de Arqueo de Caja

> **Historia de usuario:** *Como administrador, quiero un reporte de cierre de caja diario para verificar ingresos totales y movimiento de vehículos.*

**Criterios de Aceptación:**
- ✅ Reporte filtra por fecha (por defecto hoy)
- ✅ Desglosa ingresos y cantidad por tipo de vehículo
- ✅ Muestra el total global de ingresos del día
- ✅ Solo incluye registros con estado `LIQUIDADO`

---

## 🏗️ Arquitectura del Sistema

```
CLIENTE (Frontend / Postman)
         │  HTTP/JSON
         ▼
┌─────────────────────────────────────────────┐
│         FastAPI (Python 3.11+)              │
│                                             │
│  /entrada  /salida  /tarifa  /arqueo        │
│              │                              │
│   ┌──────────┴──────────┐                  │
│   │  Caché en Memoria   │ ← Tarifas O(1)   │
│   └──────────┬──────────┘                  │
│              │                              │
│   ┌──────────▼──────────┐                  │
│   │  SQLite + WAL       │                  │
│   │  + Índices B-Tree   │                  │
│   │  + 16MB Cache RAM   │                  │
│   └─────────────────────┘                  │
└─────────────────────────────────────────────┘
```

---

## 📅 Sprint Planning

### Sprint 1 — Control de Acceso Base

**Meta del Sprint:** *"Tener el registro de vehículos funcionando con tarifa diferencial, validación de rendimiento ≤ 2s y documentación completa."*

| ID | Tarea | Responsable | Estimación | Estado |
|---|---|---|---|---|
| T-01 | Diseñar esquema BD (tablas, vistas, índices) | Dev 1 | 4h | ✅ Done |
| T-02 | Implementar `POST /vehiculos/entrada` | Dev 1 | 6h | ✅ Done |
| T-03 | Implementar `POST /vehiculos/salida` | Dev 1 | 4h | ✅ Done |
| T-04 | Implementar caché en memoria para tarifas | Dev 2 | 3h | ✅ Done |
| T-05 | Configurar pragmas SQLite para rendimiento | Dev 2 | 2h | ✅ Done |
| T-06 | Crear índices compuestos en BD | Dev 2 | 2h | ✅ Done |
| T-07 | Implementar tests de SLA ≤ 2s | Dev 2 | 4h | ✅ Done |
| T-08 | Implementar `GET /tarifas` (RF-02) | Dev 1 | 2h | ✅ Done |
| T-09 | Implementar `GET /arqueo` (RF-04) | Dev 1 | 3h | ✅ Done |
| T-10 | Redactar README.md completo | Dev 3 | 4h | ✅ Done |
| T-11 | Validación PO: historias de usuario y DoD | PO | 2h | ✅ Done |
| T-12 | Review de calidad y retrospectiva | SM | 1h | 🔄 En curso |

**Velocidad del Sprint:** 37h estimadas · 36h completadas

---

## ⚙️ Instalación y Ejecución

### Prerrequisitos
- Python **3.11+**
- `pip` o `pip3`

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd Parqueadero-SCRUM
```

### 2. Entorno virtual e instalación
```bash
# Windows
python -m venv venv && venv\Scripts\activate

# macOS / Linux
python3 -m venv venv && source venv/bin/activate

# Instalar dependencias
pip install -r backend/requirements.txt
```

### 3. Iniciar el servidor
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Documentación interactiva

| Recurso | URL |
|---|---|
| 📖 Swagger UI | http://localhost:8000/docs |
| 📄 ReDoc | http://localhost:8000/redoc |
| ❤️ Health Check | http://localhost:8000/health |

### 5. Ejecutar pruebas
```bash
pytest tests/test_rendimiento_sla.py -v
```

---

## 🔌 Endpoints de la API

| Método | Endpoint | RF | Descripción |
|---|---|---|---|
| `POST` | `/api/v1/vehiculos/entrada` | RF-01 | Registra entrada de vehículo |
| `POST` | `/api/v1/vehiculos/salida` | RF-03 | Registra salida y liquida cobro |
| `GET` | `/api/v1/vehiculos/activos` | RF-01 | Lista vehículos en el parqueadero |
| `GET` | `/api/v1/vehiculos/{placa}/tarifa` | RF-01-PERF | Tarifa acumulada (SLA ≤ 2s) |
| `GET` | `/api/v1/tarifas` | RF-02 | Tarifas diferenciales por tipo |
| `GET` | `/api/v1/reportes/arqueo` | RF-04 | Arqueo de caja por fecha |

### Ejemplo — Registro de Entrada
```bash
curl -X POST "http://localhost:8000/api/v1/vehiculos/entrada" \
  -H "Content-Type: application/json" \
  -d '{"placa": "ABC123", "tipo_vehiculo_id": 2, "operador_id": 1}'
```

```json
{
  "id": 1,
  "placa": "ABC123",
  "tipo_vehiculo": "Carro",
  "tarifa_hora": 4000.0,
  "hora_entrada": "2026-10-22 14:35:00",
  "estado": "ACTIVO",
  "tiempo_respuesta_ms": 12.5
}
```

### Ejemplo — Consulta Tarifa (SLA ≤ 2s)
```bash
curl "http://localhost:8000/api/v1/vehiculos/ABC123/tarifa"
```

```json
{
  "placa": "ABC123",
  "tipo_vehiculo": "Carro",
  "tarifa_hora": 4000.0,
  "hora_entrada": "2026-10-22 14:35:00",
  "minutos_transcurridos": 75,
  "tarifa_acumulada": 5000.0,
  "tiempo_respuesta_ms": 8.3,
  "cumple_sla": true
}
```

---

## 📁 Estructura del Proyecto

```
Parqueadero-SCRUM/
│
├── backend/
│   ├── main.py                  # API REST FastAPI (Dev 1 + Dev 2)
│   ├── requirements.txt         # Dependencias Python
│   └── database/
│       ├── schema.sql           # Esquema BD + Índices (Dev 1 + Dev 2)
│       └── parqueadero.db       # Base de datos SQLite (auto-generada)
│
├── tests/
│   └── test_rendimiento_sla.py  # Tests SLA ≤ 2s y funcionales (Dev 2)
│
└── README.md                    # Documentación oficial (Dev 3)
```

---

## ✅ Criterios de Aceptación (DoD)

Un ítem del backlog se considera **DONE** cuando cumple todos los siguientes criterios:

| Criterio | RF-01 | RF-01-PERF | RF-02 | RF-03 | RF-04 |
|---|---|---|---|---|---|
| Código implementado | ✅ | ✅ | ✅ | ✅ | ✅ |
| Tests pasando | ✅ | ✅ | ✅ | ✅ | ✅ |
| SLA ≤ 2s verificado | ✅ | ✅ | ✅ | ✅ | ✅ |
| Documentado en README | ✅ | ✅ | ✅ | ✅ | ✅ |
| Validado por PO | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 📊 Pruebas de Rendimiento

| Test | Descripción | Límite |
|---|---|---|
| `test_registro_entrada_tiempo_respuesta` | Registro de entrada completo | ≤ 2000 ms |
| `test_consulta_tarifa_tiempo_respuesta` | Consulta tarifa acumulada | ≤ 2000 ms |
| `test_vehiculos_activos_tiempo_respuesta` | Listado de vehículos activos | ≤ 2000 ms |
| `test_tarifas_cache_tiempo_respuesta` | Tarifas desde caché en memoria | < 100 ms |
| `test_arqueo_caja_tiempo_respuesta` | Reporte de arqueo de caja | ≤ 2000 ms |
| `test_sla_bajo_carga_concurrente` | 10 requests simultáneos | ≤ 2000 ms c/u |

---

## 🏷️ Tecnologías Utilizadas

| Tecnología | Versión | Uso |
|---|---|---|
| **Python** | 3.11+ | Lenguaje principal del backend |
| **FastAPI** | 0.104+ | Framework REST API |
| **SQLite** | 3.x | Base de datos relacional |
| **Pydantic** | 2.5+ | Validación de datos y modelos |
| **Uvicorn** | 0.24+ | Servidor ASGI de producción |
| **Pytest** | 7.4+ | Framework de pruebas |
| **httpx** | 0.25+ | Cliente HTTP para tests |

---

## 📜 Licencia

Proyecto educativo desarrollado con metodología **Scrum** para el curso de Ingeniería de Software.
Todos los derechos reservados © 2026.

---

<div align="center">

**Desarrollado con ❤️ por el Equipo Scrum — Parqueadero-SCRUM**
*1 Product Owner · 1 Scrum Master · 3 Desarrolladores*

</div>
