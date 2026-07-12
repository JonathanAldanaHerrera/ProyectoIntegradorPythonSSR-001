import threading

from logitrack.services.envio_service import EnvioService


class EnvioController:

    def __init__(self, service: EnvioService, cliente=None) -> None:
        self._service = service
        self._cliente = cliente  # RouteApiClient | None

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

    def actualizar_envio(self, envio_id: int, campo: str, valor: str | float | None) -> bool:
        return self._service.actualizar(envio_id, campo, valor)

    def cargar_envios_lento(self, cancel_event: threading.Event) -> list[dict] | None:
        return self._service.cargar_lento(cancel_event)

    # ── Enriquecimiento con API externa ──────────────────────────────

    def enriquecer_envio_async(
        self, envio_id: int, cancel_event: threading.Event
    ) -> dict | None:
        if cancel_event.is_set() or self._cliente is None:
            return None
        return self._service.enriquecer_lento(envio_id, self._cliente, cancel_event)

    def sincronizar_pendientes_async(
        self, cancel_event: threading.Event
    ) -> tuple[int, int] | None:
        if cancel_event.is_set() or self._cliente is None:
            return None
        return self._service.sincronizar_pendientes(self._cliente)

    @property
    def tiene_cliente_api(self) -> bool:
        return self._cliente is not None
