import tkinter.ttk as ttk

COLOR_EXITO = "#2e7d32"
COLOR_ERROR = "#c62828"
COLOR_NORMAL = "#333333"

FUENTE_BASE = ("Segoe UI", 10)
FUENTE_TITULO = ("Segoe UI", 14, "bold")
FUENTE_STATUS = ("Segoe UI", 9)

PAD_SM = 4
PAD_MD = 8
PAD_LG = 12
PAD_XL = 16

ANCHO_PANEL = 280
UMBRAL_RESPONSIVE = 700


def aplicar_tema(style: ttk.Style) -> None:
    style.theme_use("clam")

    style.configure("TLabel", font=FUENTE_BASE, padding=2)
    style.configure("TEntry", font=FUENTE_BASE, padding=4)
    style.configure("TCombobox", font=FUENTE_BASE, padding=4)
    style.configure(
        "TButton",
        font=FUENTE_BASE,
        padding=(12, 6),
    )

    style.configure(
        "Titulo.TLabel",
        font=FUENTE_TITULO,
        foreground="#1a237e",
        padding=(10, 8),
    )

    style.configure(
        "Status.TLabel",
        font=FUENTE_STATUS,
        foreground=COLOR_NORMAL,
        padding=(10, 4),
        background="#e0e0e0",
    )
    style.configure(
        "Exito.TLabel",
        font=FUENTE_STATUS,
        foreground=COLOR_EXITO,
        padding=(10, 4),
        background="#e8f5e9",
    )
    style.configure(
        "Error.TLabel",
        font=FUENTE_STATUS,
        foreground=COLOR_ERROR,
        padding=(10, 4),
        background="#ffebee",
    )

    style.configure(
        "Formulario.TLabelframe",
        font=FUENTE_BASE,
        padding=10,
    )
    style.configure("Formulario.TLabelframe.Label", font=("Segoe UI", 11, "bold"))

    style.configure("Treeview", font=FUENTE_BASE, rowheight=28)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
