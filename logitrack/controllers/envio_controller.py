import threading
import time

from logitrack.models.envio import Envio


class EnvioController:
    TIPOS = ("Paquete", "Sobre", "Carga")
    ESTADOS = ("Pendiente", "En tránsito", "Entregado", "Retrasado")
    SUCURSALES = ("Central", "Norte", "Sur", "Oriente")

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
        self, destinatario: str, direccion: str, tipo: str, estado: str,
        sucursal: str = "Central",
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
            sucursal=sucursal,
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

    def filtrar(self, estado: str | None, texto: str) -> list[Envio]:
        resultado = list(self._envios)
        if estado and estado != "Todos":
            resultado = [e for e in resultado if e.estado == estado]
        texto = texto.strip().lower()
        if texto:
            resultado = [
                e for e in resultado
                if texto in e.destinatario.lower() or texto in e.direccion.lower()
            ]
        return resultado

    def conteos_por_estado(self) -> dict[str, int]:
        conteos = {estado: 0 for estado in self.ESTADOS}
        for envio in self._envios:
            if envio.estado in conteos:
                conteos[envio.estado] += 1
        return conteos

    def actualizar_envio(self, envio_id: int, campo: str, valor: str) -> bool:
        if campo in ("id", "fecha"):
            return False
        for envio in self._envios:
            if envio.id == envio_id:
                if hasattr(envio, campo):
                    setattr(envio, campo, valor)
                    return True
        return False

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
