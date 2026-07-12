import threading
import time

from logitrack.models.envio import Envio


class EnvioController:
    TIPOS = ("Paquete", "Sobre", "Carga")
    ESTADOS = ("Pendiente", "En tránsito", "Entregado")

    def __init__(self) -> None:
        self._envios: list[Envio] = []
        self._siguiente_id: int = 1

    def validar(self, destinatario: str, direccion: str) -> list[str]:
        errores: list[str] = []
        if not destinatario.strip():
            errores.append("Destinatario es obligatorio")
        if not direccion.strip():
            errores.append("Dirección es obligatoria")
        return errores

    def registrar(
        self, destinatario: str, direccion: str, tipo: str, estado: str
    ) -> Envio | None:
        errores = self.validar(destinatario, direccion)
        if errores:
            return None

        envio = Envio(
            id=self._siguiente_id,
            destinatario=destinatario.strip(),
            direccion=direccion.strip(),
            tipo=tipo,
            estado=estado,
        )
        self._envios.append(envio)
        self._siguiente_id += 1
        return envio

    def buscar(self, termino: str) -> list[Envio]:
        termino = termino.strip().lower()
        if not termino:
            return list(self._envios)
        return [e for e in self._envios if termino in e.destinatario.lower()]

    def listar(self) -> list[Envio]:
        return list(self._envios)

    def cargar_envios_lento(self, cancel_event: threading.Event) -> list[Envio] | None:
        for _ in range(25):
            if cancel_event.is_set():
                return None
            time.sleep(0.1)
        return list(self._envios)

    def buscar_lento(self, termino: str, cancel_event: threading.Event) -> list[Envio] | None:
        for _ in range(15):
            if cancel_event.is_set():
                return None
            time.sleep(0.1)
        return self.buscar(termino)

