import threading
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from logitrack.models.envio import Envio

if TYPE_CHECKING:
    from logitrack.services.route_api_client import RouteApiClient


class EnvioRepository(ABC):

    @abstractmethod
    def todos(self) -> list[Envio]: ...

    @abstractmethod
    def agregar(self, envio: Envio) -> int: ...  # retorna el id asignado

    @abstractmethod
    def obtener_por_id(self, envio_id: int) -> Envio | None: ...

    @abstractmethod
    def actualizar_campo(
        self, envio_id: int, campo: str, valor: str | float | None
    ) -> bool: ...

    def registrar_log(self, envio_id: int, accion: str, resultado: str) -> None:
        pass

    def encolar_pendiente(self, envio_id: int, operacion: str) -> None:
        pass

    def obtener_pendientes(self) -> list[dict[str, Any]]:
        return []

    def eliminar_pendiente(self, op_id: int) -> None:
        pass

    def limpiar_pendientes(self) -> int:
        return 0


class MemoryRepository(EnvioRepository):

    def __init__(self) -> None:
        self._envios: list[Envio] = []
        self._contador: int = 1

    def todos(self) -> list[Envio]:
        return list(self._envios)

    def agregar(self, envio: Envio) -> int:
        envio.id = self._contador
        self._contador += 1
        self._envios.append(envio)
        return envio.id

    def obtener_por_id(self, envio_id: int) -> Envio | None:
        return next((e for e in self._envios if e.id == envio_id), None)

    def actualizar_campo(
        self, envio_id: int, campo: str, valor: str | float | None
    ) -> bool:
        envio = self.obtener_por_id(envio_id)
        if not envio or not hasattr(envio, campo):
            return False
        if campo in ("lat", "lng"):
            try:
                setattr(envio, campo, float(valor) if valor is not None else None)
            except (ValueError, TypeError):
                setattr(envio, campo, None)
        else:
            setattr(envio, campo, valor)
        return True


class EnvioService:
    TIPOS = ("Paquete", "Sobre", "Carga")
    ESTADOS = ("Pendiente", "En tránsito", "Entregado", "Retrasado")
    SUCURSALES = ("Central", "Norte", "Sur", "Oriente")

    def __init__(self, repo: EnvioRepository | None = None) -> None:
        self._repo = repo or MemoryRepository()

    # ── Conversión interna ────────────────────────────────────────────

    @staticmethod
    def _a_dict(envio: Envio) -> dict[str, Any]:
        return {
            "id": envio.id,
            "destinatario": envio.destinatario,
            "direccion": envio.direccion,
            "tipo": envio.tipo,
            "estado": envio.estado,
            "sucursal": envio.sucursal,
            "fecha": envio.fecha,
            "lat": envio.lat,
            "lng": envio.lng,
            "clima": envio.clima,
        }

    # ── Lógica de negocio ─────────────────────────────────────────────

    def validar(self, destinatario: str, direccion: str) -> list[str]:
        errores: list[str] = []
        if not destinatario.strip():
            errores.append("Destinatario es obligatorio")
        if not direccion.strip():
            errores.append("Dirección es obligatoria")
        return errores

    def registrar(
        self,
        destinatario: str,
        direccion: str,
        tipo: str,
        estado: str,
        sucursal: str = "Central",
    ) -> dict[str, Any] | None:
        if self.validar(destinatario, direccion):
            return None
        envio = Envio(
            id=0,  # placeholder; el repo asigna el id real
            destinatario=destinatario.strip(),
            direccion=direccion.strip(),
            tipo=tipo,
            estado=estado,
            sucursal=sucursal,
        )
        envio.id = self._repo.agregar(envio)
        return self._a_dict(envio)

    def listar(self) -> list[dict[str, Any]]:
        return [self._a_dict(e) for e in self._repo.todos()]

    def buscar(self, termino: str) -> list[dict[str, Any]]:
        termino = termino.strip().lower()
        if not termino:
            return self.listar()
        return [
            self._a_dict(e)
            for e in self._repo.todos()
            if termino in e.destinatario.lower()
        ]

    def filtrar(self, estado: str | None, texto: str) -> list[dict[str, Any]]:
        resultado = self._repo.todos()
        if estado and estado != "Todos":
            resultado = [e for e in resultado if e.estado == estado]
        texto = texto.strip().lower()
        if texto:
            resultado = [
                e
                for e in resultado
                if texto in e.destinatario.lower() or texto in e.direccion.lower()
            ]
        return [self._a_dict(e) for e in resultado]

    def conteos_por_estado(self) -> dict[str, int]:
        conteos = {estado: 0 for estado in self.ESTADOS}
        for envio in self._repo.todos():
            if envio.estado in conteos:
                conteos[envio.estado] += 1
        return conteos

    def actualizar(self, envio_id: int, campo: str, valor: str | float | None) -> bool:
        if campo in ("id", "fecha"):
            return False
        return self._repo.actualizar_campo(envio_id, campo, valor)

    # ── Enriquecimiento con API externa ──────────────────────────────

    def enriquecer(
        self,
        envio_id: int,
        cliente: "RouteApiClient",
        encolar_si_falla: bool = True,
    ) -> dict[str, Any] | None:
        envio = self._repo.obtener_por_id(envio_id)
        if not envio:
            return None

        datos = cliente.obtener_datos_ruta(envio.direccion)

        if datos and "lat" in datos:
            if datos.get("lat") is not None:
                self._repo.actualizar_campo(envio_id, "lat", datos["lat"])
                self._repo.actualizar_campo(envio_id, "lng", datos["lng"])
            if datos.get("clima"):
                self._repo.actualizar_campo(envio_id, "clima", datos["clima"])
            self._repo.registrar_log(
                envio_id,
                "enriquecer",
                f"ok: lat={datos.get('lat'):.4f}, clima={datos.get('clima')}",
            )
            actualizado = self._repo.obtener_por_id(envio_id)
            return self._a_dict(actualizado) if actualizado else None
        else:
            if encolar_si_falla:
                self._repo.encolar_pendiente(envio_id, "enriquecer")
            self._repo.registrar_log(envio_id, "enriquecer", f"fallo: {datos}")
            return None

    def sincronizar_pendientes(self, cliente: "RouteApiClient") -> tuple[int, int]:
        pendientes = self._repo.obtener_pendientes()

        vistos: dict[int, int] = {}  # envio_id → op_id a procesar
        duplicados: list[int] = []
        for op in pendientes:
            eid = op["envio_id"]
            if eid not in vistos:
                vistos[eid] = op["id"]
            else:
                duplicados.append(op["id"])
        for dup_id in duplicados:
            self._repo.eliminar_pendiente(dup_id)

        exitosas = 0
        for envio_id, op_id in vistos.items():
            resultado = self.enriquecer(envio_id, cliente, encolar_si_falla=False)
            self._repo.eliminar_pendiente(op_id)
            if resultado is not None:
                exitosas += 1
        restantes = len(self._repo.obtener_pendientes())
        return exitosas, restantes

    def enriquecer_lento(
        self,
        envio_id: int,
        cliente: "RouteApiClient",
        cancel_event: threading.Event,
    ) -> dict[str, Any] | None:
        if cancel_event.is_set():
            return None
        return self.enriquecer(envio_id, cliente, encolar_si_falla=True)

    # ── Operaciones lentas (simuladas) ───────────────────────────────

    def cargar_lento(
        self, cancel_event: threading.Event
    ) -> list[dict[str, Any]] | None:
        for _ in range(25):
            if cancel_event.is_set():
                return None
            time.sleep(0.1)
        return self.listar()

    def buscar_lento(
        self, termino: str, cancel_event: threading.Event
    ) -> list[dict[str, Any]] | None:
        for _ in range(15):
            if cancel_event.is_set():
                return None
            time.sleep(0.1)
        return self.buscar(termino)
