import tkinter as tk
import tkinter.ttk as ttk
from typing import Any

FUENTE_BASE = ("Segoe UI", 10)
FUENTE_TITULO = ("Segoe UI", 14, "bold")
FUENTE_STATUS = ("Segoe UI", 9)
FUENTE_KPI_NUMERO = ("Segoe UI", 20, "bold")
FUENTE_KPI_LABEL = ("Segoe UI", 9)

PAD_SM = 4
PAD_MD = 8
PAD_LG = 12
PAD_XL = 16

ANCHO_PANEL = 280
UMBRAL_RESPONSIVE = 700

COLORES_ESTADO = {
    "Pendiente": {
        "bg": "#fff3e0",
        "fg": "#e65100",
        "tag_bg": "#ffe0b2",
        "tag_bg_oscuro": "#3d2800",
        "tag_fg_oscuro": "#ffb74d",
    },
    "En tránsito": {
        "bg": "#e3f2fd",
        "fg": "#0d47a1",
        "tag_bg": "#bbdefb",
        "tag_bg_oscuro": "#0a1f3d",
        "tag_fg_oscuro": "#90caf9",
    },
    "Entregado": {
        "bg": "#e8f5e9",
        "fg": "#1b5e20",
        "tag_bg": "#c8e6c9",
        "tag_bg_oscuro": "#0f2e14",
        "tag_fg_oscuro": "#a5d6a7",
    },
    "Retrasado": {
        "bg": "#ffebee",
        "fg": "#b71c1c",
        "tag_bg": "#ffcdd2",
        "tag_bg_oscuro": "#3d0a0a",
        "tag_fg_oscuro": "#ef9a9a",
    },
}

TEMAS = {
    "claro": {
        "bg": "#f5f5f5",
        "fg": "#212121",
        "bg_alt": "#ffffff",
        "bg_panel": "#fafafa",
        "bg_barra": "#e0e0e0",
        "fg_titulo": "#1a237e",
        "fg_muted": "#757575",
        "bg_exito": "#e8f5e9",
        "fg_exito": "#2e7d32",
        "bg_error": "#ffebee",
        "fg_error": "#c62828",
        "bg_treeview": "#ffffff",
        "fg_treeview": "#212121",
        "bg_heading": "#eeeeee",
        "bg_selected": "#1565c0",
        "fg_selected": "#ffffff",
        "border": "#bdbdbd",
        "progressbar": "#1565c0",
    },
    "oscuro": {
        "bg": "#1e1e2e",
        "fg": "#cdd6f4",
        "bg_alt": "#313244",
        "bg_panel": "#2a2a3c",
        "bg_barra": "#45475a",
        "fg_titulo": "#89b4fa",
        "fg_muted": "#a6adc8",
        "bg_exito": "#1e3a2f",
        "fg_exito": "#a6e3a1",
        "bg_error": "#3e1e1e",
        "fg_error": "#f38ba8",
        "bg_treeview": "#313244",
        "fg_treeview": "#cdd6f4",
        "bg_heading": "#45475a",
        "bg_selected": "#89b4fa",
        "fg_selected": "#1e1e2e",
        "border": "#585b70",
        "progressbar": "#89b4fa",
    },
}

_tema_actual = "claro"


def obtener_tema_actual() -> str:
    return _tema_actual


def obtener_paleta(tema: str | None = None) -> dict[str, Any]:
    return TEMAS[tema or _tema_actual]


def aplicar_tema(
    style: ttk.Style, root: tk.Tk | None = None, tema: str = "claro"
) -> None:
    global _tema_actual
    _tema_actual = tema
    p = TEMAS[tema]

    style.theme_use("clam")

    if root:
        root.configure(bg=p["bg"])

    style.configure(".", background=p["bg"], foreground=p["fg"], font=FUENTE_BASE)
    style.configure("TFrame", background=p["bg"])
    style.configure(
        "TLabel", font=FUENTE_BASE, padding=2, background=p["bg"], foreground=p["fg"]
    )
    style.configure(
        "TEntry",
        font=FUENTE_BASE,
        padding=4,
        fieldbackground=p["bg_alt"],
        foreground=p["fg"],
    )
    style.configure(
        "TCombobox",
        font=FUENTE_BASE,
        padding=4,
        fieldbackground=p["bg_alt"],
        foreground=p["fg"],
    )
    style.configure(
        "TButton",
        font=FUENTE_BASE,
        padding=(12, 6),
        background=p["bg_alt"],
        foreground=p["fg"],
    )
    style.map("TButton", background=[("active", p["bg_barra"])])
    style.configure("TSeparator", background=p["border"])

    style.configure(
        "Titulo.TLabel",
        font=FUENTE_TITULO,
        foreground=p["fg_titulo"],
        padding=(10, 8),
        background=p["bg"],
    )

    style.configure(
        "Status.TLabel",
        font=FUENTE_STATUS,
        foreground=p["fg_muted"],
        padding=(10, 4),
        background=p["bg_barra"],
    )
    style.configure(
        "Exito.TLabel",
        font=FUENTE_STATUS,
        foreground=p["fg_exito"],
        padding=(10, 4),
        background=p["bg_exito"],
    )
    style.configure(
        "Error.TLabel",
        font=FUENTE_STATUS,
        foreground=p["fg_error"],
        padding=(10, 4),
        background=p["bg_error"],
    )

    style.configure(
        "Formulario.TLabelframe", font=FUENTE_BASE, padding=10, background=p["bg_panel"]
    )
    style.configure(
        "Formulario.TLabelframe.Label",
        font=("Segoe UI", 11, "bold"),
        background=p["bg_panel"],
        foreground=p["fg"],
    )

    style.configure(
        "Treeview",
        font=FUENTE_BASE,
        rowheight=28,
        background=p["bg_treeview"],
        foreground=p["fg_treeview"],
        fieldbackground=p["bg_treeview"],
    )
    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        background=p["bg_heading"],
        foreground=p["fg"],
    )
    style.map(
        "Treeview",
        background=[("selected", p["bg_selected"])],
        foreground=[("selected", p["fg_selected"])],
    )

    style.configure(
        "Progreso.Horizontal.TProgressbar",
        troughcolor=p["bg_barra"],
        background=p["progressbar"],
        thickness=6,
    )
    style.configure(
        "Cancelar.TButton", font=FUENTE_BASE, foreground=p["fg_error"], padding=(8, 4)
    )

    style.configure("Filtros.TFrame", background=p["bg"])
    style.configure(
        "Filtros.TLabel",
        background=p["bg"],
        foreground=p["fg_muted"],
        font=FUENTE_STATUS,
    )
    style.configure("Filtros.TCombobox", font=FUENTE_STATUS)

    style.configure("KPI.TFrame", background=p["bg_alt"], relief="solid", borderwidth=1)
    style.configure("KPI.TLabel", background=p["bg_alt"], foreground=p["fg"])
    style.configure(
        "KPINumero.TLabel",
        font=FUENTE_KPI_NUMERO,
        background=p["bg_alt"],
        foreground=p["fg"],
    )
    style.configure(
        "KPITexto.TLabel",
        font=FUENTE_KPI_LABEL,
        background=p["bg_alt"],
        foreground=p["fg_muted"],
    )

    style.configure(
        "Toggle.TButton",
        font=("Segoe UI", 14),
        padding=(8, 2),
        background=p["bg"],
        foreground=p["fg"],
    )


def cambiar_tema(style: ttk.Style, root: tk.Tk) -> str:
    nuevo = "oscuro" if _tema_actual == "claro" else "claro"
    aplicar_tema(style, root, nuevo)
    return nuevo
