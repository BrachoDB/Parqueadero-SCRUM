# Auditoría estática del backend

Alcance: revisión estática de `backend/main.py` y `backend/database/schema.sql`.
No se ejecutaron pruebas de penetración. La aplicación principal del contenedor
es `backend.main:app`.

## Hallazgos

| ID | Gravedad | Hallazgo | Evidencia / impacto | Recomendación |
|---|---|---|---|---|
| A-01 | Alta (resuelto) | La API no autenticaba ni autorizaba solicitudes. | En la implementación actual las rutas privadas exigen Basic Auth, los roles se validan en cada operación, el ID del operador procede de la identidad autenticada y los clientes solo consultan vehículos asociados a su cuenta. | Mantener TLS obligatorio en producción: Basic Auth codifica credenciales en Base64, no cifra el transporte. |
| A-02 | Alta | La comprobación de entradas duplicadas no es atómica. | `registrar_entrada` consulta primero si existe un registro activo y luego inserta; dos solicitudes concurrentes para la misma placa pueden superar la comprobación. El esquema no impone unicidad para placas activas. | Añadir un índice único parcial sobre `placa WHERE estado = 'ACTIVO'` y convertir el conflicto de SQLite en HTTP 409. Ejecutar la migración verificando duplicados previos. |
| A-03 | Media | La tarifa almacenada al ingresar no se usa para liquidar. | `tarifa_aplicada` conserva la tarifa inicial, pero la consulta de salida y la tarifa acumulada usan `tipos_vehiculo.tarifa_hora`. Un cambio de tarifa puede alterar retroactivamente el precio de una estadía activa. | Calcular cargos con `vehiculos_registro.tarifa_aplicada` y devolver ese mismo valor en las consultas de tarifa. |
| A-04 | Media | CORS admite cualquier origen junto con credenciales. | La configuración usa `allow_origins=["*"]` y `allow_credentials=True`. La combinación es excesivamente permisiva para un servicio que procesa operaciones de escritura. | Restringir los orígenes a los dominios del frontend y habilitar credenciales solo si son necesarias. |
| A-05 | Media | La caché de tarifas no tiene invalidación efectiva. | `_CACHE_TTL` se define, pero no se consulta; la caché se carga solo al iniciar. Cambios de tarifa o de tipos activos en la base de datos no se reflejan hasta reiniciar. | Implementar una política de expiración/invalidez y una fuente de actualización, o eliminar la caché si no hay operaciones administrativas que la mantengan coherente. |
| A-06 | Baja | El modo WAL se vuelve a establecer por cada conexión de solicitud. | `get_db` ejecuta `PRAGMA journal_mode=WAL` cada vez que abre una conexión, aunque el modo es persistente para la base. Bajo concurrencia esto añade trabajo y puede provocar contención en SQLite. | Establecer el modo WAL durante la inicialización y conservar en `get_db` solo los pragmas por conexión necesarios. Medir el cambio con carga representativa. |

## Observaciones de validación

- Las consultas SQL observadas parametrizan los valores del usuario; no se encontró
  interpolación de entrada en las consultas revisadas.
- Pydantic valida el cuerpo de las peticiones y FastAPI responde con HTTP 422 para
  errores de validación.
- El contenedor ejecuta la aplicación como usuario no privilegiado y conserva el
  archivo SQLite en un volumen persistente.
- El despliegue de Compose no publica servicios de base de datos adicionales:
  SQLite está integrado en el proceso y el almacenamiento se conserva en un volumen.
- Las cuentas se provisionan con `python -m backend.manage_users`; las cuentas
  conocidas no se crean automáticamente en producción.
