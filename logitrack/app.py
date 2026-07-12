import tkinter as tk
import tkinter.ttk as ttk

from logitrack.controllers.envio_controller import EnvioController
from logitrack.services.envio_service import EnvioService, EnvioRepository, MemoryRepository
from logitrack.ui.theme import aplicar_tema
from logitrack.views.main_window import MainWindow


class Container:
    """Ensambla las dependencias y permite cambiar el backend de datos."""

    def __init__(self, repo: EnvioRepository | None = None) -> None:
        service = EnvioService(repo or MemoryRepository())
        self.controller = EnvioController(service)


class App:
    def __init__(self, repo: EnvioRepository | None = None) -> None:
        self.root = tk.Tk()
        self.root.title("LogiTrack Desktop")
        self.root.geometry("960x600")
        self.root.minsize(500, 400)

        style = ttk.Style(self.root)
        aplicar_tema(style)

        container = Container(repo)
        self.main_window = MainWindow(self.root, container.controller)

    def run(self) -> None:
        self.root.mainloop()
