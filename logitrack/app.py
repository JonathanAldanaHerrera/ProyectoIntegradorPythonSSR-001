import tkinter as tk
import tkinter.ttk as ttk

from logitrack.controllers.envio_controller import EnvioController
from logitrack.services.envio_service import EnvioRepository, EnvioService
from logitrack.services.route_api_client import RouteApiClient
from logitrack.services.sqlite_repository import SQLiteRepository
from logitrack.ui.theme import aplicar_tema
from logitrack.views.main_window import MainWindow


class Container:
    """Ensambla las dependencias y permite cambiar el backend de datos."""

    def __init__(
        self,
        repo: EnvioRepository | None = None,
        cliente: RouteApiClient | None = None,
    ) -> None:
        service = EnvioService(repo or SQLiteRepository("logitrack.db"))
        self.controller = EnvioController(service, cliente or RouteApiClient())


class App:
    def __init__(
        self,
        repo: EnvioRepository | None = None,
        cliente: RouteApiClient | None = None,
    ) -> None:
        self.root = tk.Tk()
        self.root.title("LogiTrack Desktop")
        self.root.geometry("1060x620")
        self.root.minsize(600, 420)

        style = ttk.Style(self.root)
        aplicar_tema(style)

        container = Container(repo, cliente)
        self.main_window = MainWindow(self.root, container.controller)

    def run(self) -> None:
        self.root.mainloop()
