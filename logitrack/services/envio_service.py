import threading
import time
from abc import ABC, abstractmethod

from logitrack.models.envio import Envio


class EnvioRepository(ABC):

    @abstractmethod
    def todos(self) -> list[Envio]: ...

    @abstractmethod
    def agregar(self, envio: Envio) -> None: ...

    @abstractmethod
    def obtener_por_id(self, envio_id: int) -> Envio | None: ...

    @abstractmethod
    def actualizar_campo(self, envio_id: int, campo: str, valor: str) -> bool: ...

    @abstractmethod
    def siguiente_id(self) -> int: ...


class MemoryRepository(EnvioRepository):

    def __init__(self) -> None:
        self._envios: list[Envio] = []
        self._contador: int = 1

    def todos(self) -> list[Envio]:
        return list(self._envios)

    def agregar(self, envio: Envio) -> None:
        self._envios.append(envio)

    def obtener_por_id(self, envio_id: int) -> Envio | None:
        return next((e for e in self._envios if e.id == envio_id), None)

    def actualizar_campo(self, envio_id: int, campo: str, valor: str) -> bool:
        envio = self.obtener_por_id(envio_id)
        if envio and hasattr(envio, campo):
            setattr(envio, campo, valor)
            return True
        return False

    def siguiente_id(self) -> int:
        id_ = self._contador
        self._contador += 1
        return id_


class EnvioService:
    TIPOS = ("Paquete", "Sobre", "Carga")
    ESTADOS = ("Pendiente", "En tránsito", "Entregado", "Retrasado")
    SUCURSALES = ("Central", "Norte", "Sur", "Oriente")

    def __init__(self, repo: EnvioRepository | None = None) -> None:
        self._repo = repo or MemoryRepository()

    # ── Conversión interna ────────────────────────────────────────────

    @staticmethod
    def _a_dict(envio: Envio) -> dict:
        return {
            "id": envio.id,
            "destinatario": envio.destinatario,
            "direccion": envio.direccion,
            "tipo": envio.tipo,
            "estado": envio.estado,
            "sucursal": envio.sucursal,
            "fecha": envio.fecha,
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
        self, destinatario: str, direccion: str, tipo: str, estado: str,
        sucursal: str = "Central",
    ) -> dict | None:
        if self.validar(destinatario, direccion):
            return None
        envio = Envio(
            id=self._repo.siguiente_id(),
            destinatario=destinatario.strip(),
            direccion=direccion.strip(),
            tipo=tipo,
            estado=estado,
            sucursal=sucursal,
        )
        self._repo.agregar(envio)
        return self._a_dict(envio)

    def listar(self) -> list[dict]:
        return [self._a_dict(e) for e in self._repo.todos()]

    def buscar(self, termino: str) -> list[dict]:
        termino = termino.strip().lower()
        if not termino:
            return self.listar()
        return [self._a_dict(e) for e in self._repo.todos()
                if termino in e.destinatario.lower()]

    def filtrar(self, estado: str | None, texto: str) -> list[dict]:
        resultado = self._repo.todos()
        if estado and estado != "Todos":
            resultado = [e for e in resultado if e.estado == estado]
        texto = texto.strip().lower()
        if texto:
            resultado = [
                e for e in resultado
                if texto in e.destinatario.lower() or texto in e.direccion.lower()
            ]
        return [self._a_dict(e) for e in resultado]

    def conteos_por_estado(self) -> dict[str, int]:
        conteos = {estado: 0 for estado in self.ESTADOS}
        for envio in self._repo.todos():
            if envio.estado in conteos:
                conteos[envio.estado] += 1
        return conteos

    def actualizar(self, envio_id: int, campo: str, valor: str) -> bool:
        if campo in ("id", "fecha"):
            return False
        return self._repo.actualizar_campo(envio_id, campo, valor)

    def cargar_lento(self, cancel_event: threading.Event) -> list[dict] | None:
        for _ in range(25):
            if cancel_event.is_set():
                return None
            time.sleep(0.1)
        return self.listar()

    def buscar_lento(self, termino: str, cancel_event: threading.Event) -> list[dict] | None:
        for _ in range(15):
            if cancel_event.is_set():
                return None
            time.sleep(0.1)
        return self.buscar(termino)
