import threading

from logitrack.services.envio_service import EnvioService


class EnvioController:

    def __init__(self, service: EnvioService) -> None:
        self._service = service

    # ── Constantes expuestas a la vista ──────────────────────────────

    @property
    def tipos(self) -> tuple:
        return self._service.TIPOS

    @property
    def estados(self) -> tuple:
        return self._service.ESTADOS

    @property
    def sucursales(self) -> tuple:
        return self._service.SUCURSALES

    # ── Delegación al servicio ────────────────────────────────────────

    def validar(self, destinatario: str, direccion: str) -> list[str]:
        return self._service.validar(destinatario, direccion)

    def registrar(
        self, destinatario: str, direccion: str, tipo: str, estado: str,
        sucursal: str = "Central",
    ) -> dict | None:
        return self._service.registrar(destinatario, direccion, tipo, estado, sucursal)

    def listar(self) -> list[dict]:
        return self._service.listar()

    def filtrar(self, estado: str | None, texto: str) -> list[dict]:
        return self._service.filtrar(estado, texto)

    def conteos_por_estado(self) -> dict[str, int]:
        return self._service.conteos_por_estado()

    def actualizar_envio(self, envio_id: int, campo: str, valor: str) -> bool:
        return self._service.actualizar(envio_id, campo, valor)

    def cargar_envios_lento(self, cancel_event: threading.Event) -> list[dict] | None:
        return self._service.cargar_lento(cancel_event)
