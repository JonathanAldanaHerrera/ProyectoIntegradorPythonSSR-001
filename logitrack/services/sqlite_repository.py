import pathlib
import sqlite3
import threading
import time
from typing import Any

from logitrack.logger import get_logger
from logitrack.models.envio import Envio
from logitrack.services.envio_service import EnvioRepository

_log = get_logger("db.sqlite")

_CAMPOS_PERMITIDOS = frozenset(
    {"destinatario", "direccion", "tipo", "estado", "sucursal", "lat", "lng", "clima"}
)

_DDL = """
CREATE TABLE IF NOT EXISTS shipments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    destinatario TEXT NOT NULL,
    direccion   TEXT NOT NULL,
    tipo        TEXT NOT NULL,
    estado      TEXT NOT NULL,
    sucursal    TEXT NOT NULL DEFAULT 'Central',
    fecha       TEXT NOT NULL,
    lat         REAL,
    lng         REAL,
    clima       TEXT
);

CREATE TABLE IF NOT EXISTS sucursales (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre  TEXT NOT NULL UNIQUE,
    ciudad  TEXT
);

CREATE TABLE IF NOT EXISTS logs (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    envio_id  INTEGER,
    accion    TEXT NOT NULL,
    resultado TEXT,
    ts        TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (envio_id) REFERENCES shipments(id)
);

CREATE TABLE IF NOT EXISTS pending_ops (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    envio_id  INTEGER,
    operacion TEXT NOT NULL,
    creado    TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (envio_id) REFERENCES shipments(id)
);
"""

_SUCURSALES_INICIALES = [
    ("Central", "CDMX"),
    ("Norte", "Monterrey"),
    ("Sur", "Oaxaca"),
    ("Oriente", "Veracruz"),
]


class SQLiteRepository(EnvioRepository):

    def __init__(self, db_path: str = "logitrack.db") -> None:
        self._path = pathlib.Path(db_path)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        _log.info("Conectado a base de datos: %s", self._path.resolve())
        self._migrar()

    # ── Migración ─────────────────────────────────────────────────────

    def _migrar(self) -> None:
        _log.debug("Ejecutando migración DDL")
        with self._lock:
            self._conn.executescript(_DDL)
            self._conn.executemany(
                "INSERT OR IGNORE INTO sucursales (nombre, ciudad) VALUES (?, ?)",
                _SUCURSALES_INICIALES,
            )
            self._conn.commit()
        _log.info("Migración completada — tablas listas")

    # ── EnvioRepository interface ─────────────────────────────────────

    def todos(self) -> list[Envio]:
        t0 = time.monotonic()
        with self._lock:
            cur = self._conn.execute("SELECT * FROM shipments ORDER BY id")
            filas = cur.fetchall()
        ms = (time.monotonic() - t0) * 1000
        _log.debug("SELECT shipments → %d filas  (%.0fms)", len(filas), ms)
        return [self._fila_a_envio(row) for row in filas]

    def agregar(self, envio: Envio) -> int:
        t0 = time.monotonic()
        with self._lock:
            cur = self._conn.execute(
                """INSERT INTO shipments
                   (destinatario, direccion, tipo, estado, sucursal, fecha, lat, lng, clima)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    envio.destinatario,
                    envio.direccion,
                    envio.tipo,
                    envio.estado,
                    envio.sucursal,
                    envio.fecha,
                    envio.lat,
                    envio.lng,
                    envio.clima,
                ),
            )
            self._conn.commit()
            nuevo_id: int = cur.lastrowid or 0
        ms = (time.monotonic() - t0) * 1000
        _log.info(
            "INSERT shipments → id=%d  dest='%s'  dir='%s'  estado='%s'  (%.0fms)",
            nuevo_id,
            envio.destinatario,
            envio.direccion,
            envio.estado,
            ms,
        )
        return nuevo_id

    def obtener_por_id(self, envio_id: int) -> Envio | None:
        t0 = time.monotonic()
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM shipments WHERE id = ?", (envio_id,)
            )
            row = cur.fetchone()
        ms = (time.monotonic() - t0) * 1000
        if row:
            _log.debug(
                "SELECT shipments WHERE id=%d → encontrado  (%.0fms)", envio_id, ms
            )
        else:
            _log.warning(
                "SELECT shipments WHERE id=%d → no encontrado  (%.0fms)", envio_id, ms
            )
        return self._fila_a_envio(row) if row else None

    def actualizar_campo(
        self, envio_id: int, campo: str, valor: str | float | None
    ) -> bool:
        if campo not in _CAMPOS_PERMITIDOS:
            _log.error(
                "UPDATE shipments → campo '%s' no permitido (id=%d)", campo, envio_id
            )
            return False
        t0 = time.monotonic()
        with self._lock:
            cur = self._conn.execute(
                f"UPDATE shipments SET {campo} = ? WHERE id = ?", (valor, envio_id)
            )
            self._conn.commit()
            actualizado = cur.rowcount > 0
        ms = (time.monotonic() - t0) * 1000
        if actualizado:
            _log.info(
                "UPDATE shipments SET %s=%r WHERE id=%d → OK  (%.0fms)",
                campo,
                valor,
                envio_id,
                ms,
            )
        else:
            _log.warning(
                "UPDATE shipments SET %s=%r WHERE id=%d → 0 filas afectadas  (%.0fms)",
                campo,
                valor,
                envio_id,
                ms,
            )
        return actualizado

    # ── Métodos de persistencia extendidos ────────────────────────────

    def registrar_log(self, envio_id: int, accion: str, resultado: str) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO logs (envio_id, accion, resultado) VALUES (?, ?, ?)",
                (envio_id, accion, resultado),
            )
            self._conn.commit()
        _log.info(
            "LOG registrado → envio_id=%d  accion='%s'  resultado='%s'",
            envio_id,
            accion,
            resultado,
        )

    def encolar_pendiente(self, envio_id: int, operacion: str) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO pending_ops (envio_id, operacion) VALUES (?, ?)",
                (envio_id, operacion),
            )
            self._conn.commit()
        _log.warning(
            "PENDING_OP encolada → envio_id=%d  operacion='%s'", envio_id, operacion
        )

    def obtener_pendientes(self) -> list[dict[str, Any]]:
        with self._lock:
            cur = self._conn.execute("SELECT * FROM pending_ops ORDER BY creado")
            filas = [dict(row) for row in cur.fetchall()]
        _log.debug("SELECT pending_ops → %d operaciones pendientes", len(filas))
        return filas

    def eliminar_pendiente(self, op_id: int) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM pending_ops WHERE id = ?", (op_id,))
            self._conn.commit()
        _log.info("PENDING_OP eliminada → id=%d", op_id)

    def limpiar_pendientes(self) -> int:
        with self._lock:
            cur = self._conn.execute("DELETE FROM pending_ops")
            self._conn.commit()
            eliminadas = cur.rowcount
        _log.warning("PENDING_OPS limpieza total → %d entradas eliminadas", eliminadas)
        return eliminadas

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _fila_a_envio(row: sqlite3.Row) -> Envio:
        return Envio(
            id=row["id"],
            destinatario=row["destinatario"],
            direccion=row["direccion"],
            tipo=row["tipo"],
            estado=row["estado"],
            sucursal=row["sucursal"],
            fecha=row["fecha"],
            lat=row["lat"],
            lng=row["lng"],
            clima=row["clima"],
        )

    def __del__(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass
