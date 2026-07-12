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


class ScrollableFrame(ttk.Frame):
    """Frame con scroll vertical. Coloca los widgets en self.interior."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        super().__init__(parent, **kwargs)

        self._canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        self._scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self.interior = ttk.Frame(self._canvas)

        self._interior_id = self._canvas.create_window(
            (0, 0), window=self.interior, anchor="nw"
        )

        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._scrollbar.grid(row=0, column=1, sticky="ns")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.interior.bind("<Configure>", self._actualizar_scroll_region)
        self._canvas.bind("<Configure>", self._ajustar_ancho_interior)

        self._canvas.bind("<Enter>", self._activar_rueda)
        self._canvas.bind("<Leave>", self._desactivar_rueda)

    def _actualizar_scroll_region(self, _event: tk.Event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _ajustar_ancho_interior(self, event: tk.Event) -> None:
        self._canvas.itemconfigure(self._interior_id, width=event.width)

    def _activar_rueda(self, _event: tk.Event) -> None:
        self._canvas.bind_all("<MouseWheel>", self._on_rueda)
        self._canvas.bind_all("<Button-4>", self._on_rueda)
        self._canvas.bind_all("<Button-5>", self._on_rueda)

    def _desactivar_rueda(self, _event: tk.Event) -> None:
        self._canvas.unbind_all("<MouseWheel>")
        self._canvas.unbind_all("<Button-4>")
        self._canvas.unbind_all("<Button-5>")

    def _on_rueda(self, event: tk.Event) -> None:
        if event.num == 4:          # Linux scroll up
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5:        # Linux scroll down
            self._canvas.yview_scroll(1, "units")
        else:                       # Windows / macOS
            self._canvas.yview_scroll(-1 * (event.delta // 120), "units")
