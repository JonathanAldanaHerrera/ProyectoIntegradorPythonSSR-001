import tkinter as tk
import tkinter.ttk as ttk

from logitrack.ui.theme import COLORES_ESTADO, obtener_paleta


class KPICard(ttk.Frame):

    def __init__(self, parent: tk.Widget, estado: str, icono: str, **kwargs) -> None:
        super().__init__(parent, style="KPI.TFrame", **kwargs)
        self.estado = estado
        self.icono = icono

        colores = COLORES_ESTADO.get(estado, {"fg": "#333333"})

        self.lbl_icono = ttk.Label(self, text=icono, font=("Segoe UI", 16), style="KPI.TLabel")
        self.lbl_icono.grid(row=0, column=0, rowspan=2, padx=(8, 4), pady=4)

        self.lbl_numero = ttk.Label(self, text="0", style="KPINumero.TLabel")
        self.lbl_numero.configure(foreground=colores["fg"])
        self.lbl_numero.grid(row=0, column=1, sticky="sw", padx=(0, 8))

        self.lbl_texto = ttk.Label(self, text=estado, style="KPITexto.TLabel")
        self.lbl_texto.grid(row=1, column=1, sticky="nw", padx=(0, 8))

        self.columnconfigure(1, weight=1)

    def actualizar(self, valor: int) -> None:
        self.lbl_numero.configure(text=str(valor))

    def refrescar_colores(self) -> None:
        p = obtener_paleta()
        colores = COLORES_ESTADO.get(self.estado, {"fg": "#333333"})
        self.configure(style="KPI.TFrame")
        self.lbl_icono.configure(style="KPI.TLabel")
        self.lbl_numero.configure(style="KPINumero.TLabel", foreground=colores["fg"])
        self.lbl_texto.configure(style="KPITexto.TLabel")


class StatusBadge(ttk.Label):

    def __init__(self, parent: tk.Widget, estado: str, **kwargs) -> None:
        colores = COLORES_ESTADO.get(estado, {"fg": "#333333", "bg": "#eeeeee"})
        super().__init__(
            parent,
            text=f" {estado} ",
            font=("Segoe UI", 9, "bold"),
            foreground=colores["fg"],
            background=colores["bg"],
            padding=(6, 2),
            **kwargs,
        )


ICONOS_ESTADO = {
    "Pendiente": "⏳",
    "En tránsito": "🚚",
    "Entregado": "✅",
    "Retrasado": "⚠️",
}
