import tkinter as tk
import tkinter.ttk as ttk

from logitrack.controllers.envio_controller import EnvioController
from logitrack.ui.theme import aplicar_tema
from logitrack.views.main_window import MainWindow


class App:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("LogiTrack Desktop")
        self.root.geometry("960x600")
        self.root.minsize(500, 400)

        style = ttk.Style(self.root)
        aplicar_tema(style)

        self.controller = EnvioController()
        self.main_window = MainWindow(self.root, self.controller)

    def run(self) -> None:
        self.root.mainloop()
