# Fase 7 — Integración de datos: SQLite y API externa

## Esquema de la base de datos

La base de datos se crea automáticamente en `logitrack.db` al iniciar la app. Se usa SQLite 3 con WAL mode para soportar lecturas concurrentes del hilo de UI y el worker en segundo plano.

### Tabla `shipments`

| Columna     | Tipo    | Restricciones           | Descripción                        |
|-------------|---------|-------------------------|------------------------------------|
| id          | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único               |
| destinatario| TEXT    | NOT NULL                | Nombre del receptor                |
| direccion   | TEXT    | NOT NULL                | Dirección de entrega               |
| tipo        | TEXT    | NOT NULL                | Paquete / Sobre / Carga            |
| estado      | TEXT    | NOT NULL                | Pendiente / En tránsito / Entregado / Retrasado |
| sucursal    | TEXT    | NOT NULL DEFAULT 'Central' | Sucursal de origen              |
| fecha       | TEXT    | NOT NULL                | Fecha de registro (YYYY-MM-DD HH:MM) |
| lat         | REAL    | NULL                    | Latitud geocodificada              |
| lng         | REAL    | NULL                    | Longitud geocodificada             |
| clima       | TEXT    | NULL                    | Descripción del clima de la ruta   |

### Tabla `sucursales`

| Columna | Tipo    | Restricciones     | Descripción              |
|---------|---------|-------------------|--------------------------|
| id      | INTEGER | PRIMARY KEY       | Identificador            |
| nombre  | TEXT    | NOT NULL UNIQUE   | Nombre (ej. "Norte")     |
| ciudad  | TEXT    | NULL              | Ciudad de la sucursal    |

Registros iniciales: Central (CDMX), Norte (Monterrey), Sur (Oaxaca), Oriente (Veracruz).

### Tabla `logs`

| Columna   | Tipo    | Restricciones | Descripción                             |
|-----------|---------|---------------|-----------------------------------------|
| id        | INTEGER | PRIMARY KEY   | Identificador                           |
| envio_id  | INTEGER | FK shipments  | Envío relacionado                       |
| accion    | TEXT    | NOT NULL      | Nombre de la operación (ej. "enriquecer") |
| resultado | TEXT    | NULL          | "ok: lat=…" o "fallo: …"               |
| ts        | TEXT    | NOT NULL      | Timestamp UTC `datetime('now')`         |

### Tabla `pending_ops` (cola offline)

| Columna   | Tipo    | Restricciones | Descripción                              |
|-----------|---------|---------------|------------------------------------------|
| id        | INTEGER | PRIMARY KEY   | Identificador                            |
| envio_id  | INTEGER | FK shipments  | Envío pendiente de enriquecer            |
| operacion | TEXT    | NOT NULL      | Siempre `"enriquecer"` en v1             |
| creado    | TEXT    | NOT NULL      | Timestamp UTC de la inserción            |

---

## Contrato de la API externa

### 1. Geocodificación — Nominatim (OpenStreetMap)

**Endpoint:** `GET https://nominatim.openstreetmap.org/search`

| Parámetro       | Valor          | Descripción              |
|-----------------|----------------|--------------------------|
| q               | `{direccion}`  | Dirección a geocodificar |
| format          | `json`         | Formato de respuesta     |
| limit           | `1`            | Un resultado máximo      |
| accept-language | `es`           | Localización en español  |

**Ejemplo de respuesta:**
```json
[
  {
    "lat": "19.4326",
    "lon": "-99.1332",
    "display_name": "Ciudad de México, México"
  }
]
```

**Campos usados:** `lat` (float), `lon` (float).  
**Sin autenticación requerida.** Header `User-Agent` obligatorio por política de uso.

---

### 2. Clima actual — Open-Meteo

**Endpoint:** `GET https://api.open-meteo.com/v1/forecast`

| Parámetro       | Valor   | Descripción                       |
|-----------------|---------|-----------------------------------|
| latitude        | float   | Latitud obtenida de Nominatim     |
| longitude       | float   | Longitud obtenida de Nominatim    |
| current_weather | `true`  | Solicita el bloque de clima actual |

**Ejemplo de respuesta:**
```json
{
  "current_weather": {
    "temperature": 22.5,
    "windspeed": 14.2,
    "weathercode": 2
  }
}
```

**Campos usados:** `temperature` (°C), `weathercode` (código WMO → descripción legible).  
**Sin autenticación requerida.**

---

## Estrategia de manejo de fallos

```
Usuario presiona "Enriquecer ruta"
         │
         ▼
GET Nominatim ──── Timeout/Error ──────────────────► encolar en pending_ops
         │                                           mostrar 🔴 Sin conexión
         │ OK
         ▼
GET Open-Meteo ─── Timeout/Error ──► clima = None   ┐
         │                          lat/lng guardados│
         │ OK                                        │
         ▼                                           │
Actualizar shipments (lat, lng, clima)               │
Registrar en logs                                    │
Mostrar 🟢 en UI ◄───────────────────────────────────┘
```

**Parámetros de resiliencia:**
- Timeout por llamada: **8 segundos**
- Reintentos: **2** con pausa de **1 segundo** entre intentos
- La app sigue usable con datos locales aunque la API falle
- Las operaciones fallidas se guardan en `pending_ops` y se reintentán con "🔄 Sincronizar"

**Orden de degradación:**
1. Ambas APIs disponibles → lat, lng y clima completos
2. Solo Nominatim falla → operación encolada, sin enriquecimiento
3. Solo Open-Meteo falla → lat/lng guardados, clima = NULL
4. Sin conexión completa → operación encolada, indicador 🔴

---

---

## Sistema de logging

### Por qué se agregó

Durante el desarrollo de la integración con APIs externas surgió un problema de difícil diagnóstico: las llamadas a la API fallaban de forma intermitente y la tabla `pending_ops` crecía sin control. Sin visibilidad interna era imposible distinguir si el fallo era por red, por rate-limiting de Nominatim, por dirección inválida o por un bug en la lógica de cola. El logger se agregó para:

- **Observar el flujo completo** de cada operación de enriquecimiento (geocodificación → clima → escritura en BD)
- **Medir latencia real** de cada llamada HTTP y cada operación SQL
- **Detectar acumulación de errores** en `pending_ops` antes de que se conviertan en un ciclo infinito
- **Separar niveles** de detalle: DEBUG para trazabilidad técnica, WARNING/ERROR para condiciones anómalas

### Paquetes utilizados

| Paquete | Origen | Uso |
|---------|--------|-----|
| `logging` | Stdlib Python | Logger raíz, handlers, formateadores, niveles |
| `pathlib` | Stdlib Python | Ruta al archivo `.log` de forma multiplataforma |
| `sys` | Stdlib Python | Handler de consola via `sys.stdout` |

No se requiere instalar ninguna dependencia adicional; todo es de la librería estándar de Python.

### Arquitectura del logger

El módulo central es `logitrack/logger.py`. Expone dos funciones:

```python
configurar_logging(nivel=logging.DEBUG, archivo="logitrack.log")
get_logger(nombre: str) -> logging.Logger
```

**`configurar_logging`** debe llamarse una sola vez al arrancar la app (en `__main__.py`), antes de cualquier import que use `get_logger`. Configura el logger raíz `logitrack` con dos handlers:

```
logitrack (raíz)
├── StreamHandler → sys.stdout   (nivel configurable, por defecto DEBUG)
└── FileHandler  → logitrack.log (siempre DEBUG, modo append)
```

**`get_logger`** crea loggers hijos bajo la jerarquía `logitrack.<nombre>`, lo que permite filtrar por módulo:

```
logitrack
├── logitrack.app
├── logitrack.api.route     ← route_api_client.py
└── logitrack.db.sqlite     ← sqlite_repository.py
```

Al ser hijos del logger raíz, heredan su configuración automáticamente. `propagate = False` evita que los mensajes suban al logger raíz de Python y se dupliquen en consola.

### Formato de los registros

```
YYYY-MM-DD HH:MM:SS  NIVEL     logitrack.modulo               mensaje
2026-07-12 15:26:25  INFO      logitrack.db.sqlite             Migración completada — tablas listas
2026-07-12 15:26:58  DEBUG     logitrack.api.route             GET nominatim.openstreetmap.org → HTTP 200  (723ms, intento 1/3)
2026-07-12 15:27:33  WARNING   logitrack.db.sqlite             PENDING_OP encolada → envio_id=7  operacion='enriquecer'
```

### Niveles utilizados y su significado

| Nivel | Cuándo se usa |
|-------|---------------|
| `DEBUG` | Trazas de bajo nivel: cada SELECT, latencia de requests, cooldowns de Nominatim, reintentos |
| `INFO` | Operaciones completadas con éxito: INSERT, UPDATE, geocodificación OK, clima OK |
| `WARNING` | Condiciones anómalas pero recuperables: dirección sin resultados, op encolada, 0 filas afectadas en UPDATE |
| `ERROR` | Fallos irrecuperables: campo no permitido en UPDATE, agotados todos los intentos HTTP |

### Qué se registra en cada módulo

**`logitrack.api.route`** (`route_api_client.py`):

| Evento | Nivel |
|--------|-------|
| Inicio de geocodificación con la dirección | `INFO` |
| Cooldown activo antes de llamar a Nominatim | `DEBUG` |
| Respuesta HTTP exitosa con código, latencia e intento | `DEBUG` |
| Nominatim sin resultados para la dirección | `WARNING` |
| Error HTTP 4xx/5xx con código e intento | `WARNING` |
| Timeout con latencia medida | `WARNING` |
| ConnectionError con detalle del error | `WARNING` |
| Reintento programado con pausa | `DEBUG` |
| Agotados todos los intentos sin respuesta | `ERROR` |
| Resultado de geocodificación (lat, lng) | `INFO` |
| Inicio y resultado de consulta de clima | `INFO` |
| Open-Meteo sin respuesta | `WARNING` |
| Estado final del enriquecimiento | `INFO` |

**`logitrack.db.sqlite`** (`sqlite_repository.py`):

| Evento | Nivel |
|--------|-------|
| Conexión exitosa con ruta absoluta al archivo | `INFO` |
| Inicio y fin de migración DDL | `DEBUG` / `INFO` |
| SELECT con cantidad de filas y latencia | `DEBUG` |
| INSERT con id asignado, destinatario, dirección y estado | `INFO` |
| UPDATE exitoso con campo, valor, id y latencia | `INFO` |
| UPDATE sin filas afectadas | `WARNING` |
| Campo no permitido en UPDATE (guard SQL injection) | `ERROR` |
| Log de resultado de API guardado en tabla `logs` | `INFO` |
| Operación encolada en `pending_ops` | `WARNING` |
| Operación pendiente eliminada | `INFO` |
| Limpieza total de `pending_ops` | `WARNING` |

---

## Ejecución e instalación

```bash
# Instalar dependencia HTTP
pip install requests

# Ejecutar la aplicación (crea logitrack.db y logitrack.log automáticamente)
python -m logitrack

# Ejecutar tests de arquitectura
python -m pytest tests/test_arquitectura.py -v
```
