import tkinter as tk
import tkinter.ttk as ttk

from logitrack.controllers.envio_controller import EnvioController
from logitrack.controllers.task_worker import TaskWorker
from logitrack.ui.theme import (
    PAD_SM, PAD_MD, PAD_LG, ANCHO_PANEL, UMBRAL_RESPONSIVE,
)


class MainWindow:

    def __init__(self, root: tk.Tk, controller: EnvioController) -> None:
        self.root = root
        self.controller = controller
        self.worker = TaskWorker(root)

        self.var_destinatario = tk.StringVar()
        self.var_direccion = tk.StringVar()
        self.var_tipo = tk.StringVar(value=EnvioController.TIPOS[0])
        self.var_estado = tk.StringVar(value=EnvioController.ESTADOS[0])
        self.var_busqueda = tk.StringVar()

        self._layout_horizontal = True
        self._botones_accion: list[ttk.Button] = []
        self._construir_widgets()
        self._aplicar_layout_horizontal()
        self._registrar_atajos()

        self.root.bind("<Configure>", self._on_resize)

    # ── Widgets ──────────────────────────────────────────────────────

    def _construir_widgets(self) -> None:
        self._crear_barra_superior()
        self._crear_area_tabla()
        self._crear_panel_formulario()
        self._crear_barra_progreso()
        self._crear_barra_estado()

    def _crear_barra_superior(self) -> None:
        self.barra_superior = ttk.Frame(self.root)
        self.lbl_titulo = ttk.Label(
            self.barra_superior,
            text="📦 LogiTrack Desktop — Registro de Envíos",
            style="Titulo.TLabel",
        )
        self.lbl_titulo.grid(row=0, column=0, sticky="w")
        self.barra_superior.columnconfigure(0, weight=1)

    def _crear_area_tabla(self) -> None:
        self.frame_tabla = ttk.Frame(self.root)
        self.frame_tabla.columnconfigure(0, weight=1)
        self.frame_tabla.rowconfigure(0, weight=1)

        columnas = ("id", "destinatario", "direccion", "tipo", "estado", "fecha")
        self.tabla = ttk.Treeview(
            self.frame_tabla, columns=columnas, show="headings", selectmode="browse"
        )

        encabezados = {
            "id": ("ID", 50, False),
            "destinatario": ("Destinatario", 160, True),
            "direccion": ("Dirección", 200, True),
            "tipo": ("Tipo", 80, False),
            "estado": ("Estado", 100, False),
            "fecha": ("Fecha", 130, False),
        }
        for col, (titulo, ancho, stretch) in encabezados.items():
            self.tabla.heading(col, text=titulo)
            self.tabla.column(col, width=ancho, minwidth=40, stretch=stretch)

        self.scrollbar = ttk.Scrollbar(
            self.frame_tabla, orient="vertical", command=self.tabla.yview
        )
        self.tabla.configure(yscrollcommand=self.scrollbar.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

    def _crear_panel_formulario(self) -> None:
        self.panel = ttk.LabelFrame(
            self.root, text="Nuevo Envío", style="Formulario.TLabelframe"
        )

        fila = 0

        ttk.Label(self.panel, text="Destinatario *").grid(
            row=fila, column=0, sticky="w", pady=(0, PAD_SM)
        )
        fila += 1
        self.entry_destinatario = ttk.Entry(
            self.panel, textvariable=self.var_destinatario, width=25
        )
        self.entry_destinatario.grid(row=fila, column=0, sticky="ew", pady=(0, PAD_MD))
        fila += 1

        ttk.Label(self.panel, text="Dirección *").grid(
            row=fila, column=0, sticky="w", pady=(0, PAD_SM)
        )
        fila += 1
        ttk.Entry(self.panel, textvariable=self.var_direccion, width=25).grid(
            row=fila, column=0, sticky="ew", pady=(0, PAD_MD)
        )
        fila += 1

        ttk.Label(self.panel, text="Tipo").grid(
            row=fila, column=0, sticky="w", pady=(0, PAD_SM)
        )
        fila += 1
        ttk.Combobox(
            self.panel,
            textvariable=self.var_tipo,
            values=EnvioController.TIPOS,
            state="readonly",
            width=22,
        ).grid(row=fila, column=0, sticky="ew", pady=(0, PAD_MD))
        fila += 1

        ttk.Label(self.panel, text="Estado").grid(
            row=fila, column=0, sticky="w", pady=(0, PAD_SM)
        )
        fila += 1
        ttk.Combobox(
            self.panel,
            textvariable=self.var_estado,
            values=EnvioController.ESTADOS,
            state="readonly",
            width=22,
        ).grid(row=fila, column=0, sticky="ew", pady=(0, PAD_MD))
        fila += 1

        frame_acciones = ttk.Frame(self.panel)
        frame_acciones.grid(row=fila, column=0, sticky="ew", pady=(PAD_MD, PAD_SM))
        btn_guardar = ttk.Button(frame_acciones, text="💾 Guardar", command=self._guardar)
        btn_guardar.pack(fill="x", pady=2)
        btn_limpiar = ttk.Button(frame_acciones, text="🧹 Limpiar", command=self._limpiar)
        btn_limpiar.pack(fill="x", pady=2)
        self._botones_accion.extend([btn_guardar, btn_limpiar])
        fila += 1

        ttk.Separator(self.panel, orient="horizontal").grid(
            row=fila, column=0, sticky="ew", pady=PAD_MD
        )
        fila += 1

        ttk.Label(self.panel, text="Buscar por destinatario").grid(
            row=fila, column=0, sticky="w", pady=(0, PAD_SM)
        )
        fila += 1
        ttk.Entry(self.panel, textvariable=self.var_busqueda, width=25).grid(
            row=fila, column=0, sticky="ew", pady=(0, PAD_MD)
        )
        fila += 1

        frame_busqueda = ttk.Frame(self.panel)
        frame_busqueda.grid(row=fila, column=0, sticky="ew")
        btn_buscar = ttk.Button(frame_busqueda, text="🔍 Buscar", command=self._buscar_async)
        btn_buscar.pack(fill="x", pady=2)
        btn_cargar = ttk.Button(frame_busqueda, text="📦 Cargar envíos", command=self._cargar_async)
        btn_cargar.pack(fill="x", pady=2)
        btn_todos = ttk.Button(frame_busqueda, text="📋 Mostrar todos", command=self._mostrar_todos)
        btn_todos.pack(fill="x", pady=2)
        self._botones_accion.extend([btn_buscar, btn_cargar, btn_todos])

        self.panel.columnconfigure(0, weight=1)

    def _crear_barra_progreso(self) -> None:
        self.frame_progreso = ttk.Frame(self.root)
        self.progressbar = ttk.Progressbar(
            self.frame_progreso,
            mode="indeterminate",
            style="Progreso.Horizontal.TProgressbar",
        )
        self.progressbar.pack(side="left", fill="x", expand=True, padx=(0, PAD_MD))

        self.btn_cancelar = ttk.Button(
            self.frame_progreso,
            text="✕ Cancelar",
            style="Cancelar.TButton",
            command=self._cancelar_tarea,
        )
        self.btn_cancelar.pack(side="right")

    def _crear_barra_estado(self) -> None:
        self.lbl_estado = ttk.Label(
            self.root,
            text="Listo — Ctrl+N: Nuevo | Ctrl+S: Guardar | Esc: Limpiar",
            style="Status.TLabel",
        )

    # ── Layout responsivo ────────────────────────────────────────────

    def _aplicar_layout_horizontal(self) -> None:
        for widget in (self.barra_superior, self.frame_tabla, self.panel, self.frame_progreso, self.lbl_estado):
            widget.grid_forget()

        self.barra_superior.grid(row=0, column=0, columnspan=2, sticky="ew", padx=PAD_LG, pady=(PAD_LG, 0))
        self.frame_tabla.grid(row=1, column=0, sticky="nsew", padx=(PAD_LG, PAD_SM), pady=PAD_LG)
        self.panel.grid(row=1, column=1, sticky="nsew", padx=(PAD_SM, PAD_LG), pady=PAD_LG)
        self.lbl_estado.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0, minsize=ANCHO_PANEL)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)
        self.root.rowconfigure(3, weight=0)

        self._layout_horizontal = True

    def _aplicar_layout_vertical(self) -> None:
        for widget in (self.barra_superior, self.frame_tabla, self.panel, self.frame_progreso, self.lbl_estado):
            widget.grid_forget()

        self.barra_superior.grid(row=0, column=0, sticky="ew", padx=PAD_LG, pady=(PAD_LG, 0))
        self.panel.grid(row=1, column=0, sticky="ew", padx=PAD_LG, pady=(PAD_LG, 0))
        self.frame_tabla.grid(row=2, column=0, sticky="nsew", padx=PAD_LG, pady=PAD_LG)
        self.lbl_estado.grid(row=4, column=0, sticky="ew")

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0, minsize=0)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=0)
        self.root.rowconfigure(4, weight=0)

        self._layout_horizontal = False

    def _on_resize(self, event: tk.Event) -> None:
        if event.widget is not self.root:
            return

        ancho = event.width
        if ancho >= UMBRAL_RESPONSIVE and not self._layout_horizontal:
            self._aplicar_layout_horizontal()
        elif ancho < UMBRAL_RESPONSIVE and self._layout_horizontal:
            self._aplicar_layout_vertical()

    # ── Gestión de progreso ──────────────────────────────────────────

    def _iniciar_progreso(self, mensaje: str) -> None:
        self._mostrar_estado(f"⏳ {mensaje}...", "Status.TLabel")
        for btn in self._botones_accion:
            btn.configure(state="disabled")

        if self._layout_horizontal:
            self.frame_progreso.grid(row=2, column=0, columnspan=2, sticky="ew", padx=PAD_LG, pady=(0, PAD_SM))
        else:
            self.frame_progreso.grid(row=3, column=0, sticky="ew", padx=PAD_LG, pady=(0, PAD_SM))

        self.progressbar.start(15)

    def _detener_progreso(self) -> None:
        self.progressbar.stop()
        self.frame_progreso.grid_forget()
        for btn in self._botones_accion:
            btn.configure(state="normal")

    # ── Acciones asíncronas ──────────────────────────────────────────

    def _cargar_async(self) -> None:
        if self.worker.esta_corriendo:
            return

        self._iniciar_progreso("Cargando envíos")

        def tarea(cancel_event):
            return self.controller.cargar_envios_lento(cancel_event)

        def on_completado(resultado):
            self._detener_progreso()
            if resultado is None:
                self._mostrar_estado("⚠ Carga cancelada", "Error.TLabel")
            else:
                self._refrescar_tabla(resultado)
                self._mostrar_estado(
                    f"✓ {len(resultado)} envío(s) cargado(s)", "Exito.TLabel"
                )

        def on_error(exc):
            self._detener_progreso()
            self._mostrar_estado(f"Error: {exc}", "Error.TLabel")

        self.worker.ejecutar(tarea, on_completado, on_error)

    def _buscar_async(self) -> None:
        if self.worker.esta_corriendo:
            return

        termino = self.var_busqueda.get()
        self._iniciar_progreso("Buscando")

        def tarea(cancel_event):
            return self.controller.buscar_lento(termino, cancel_event)

        def on_completado(resultado):
            self._detener_progreso()
            if resultado is None:
                self._mostrar_estado("⚠ Búsqueda cancelada", "Error.TLabel")
            else:
                self._refrescar_tabla(resultado)
                self._mostrar_estado(
                    f"🔍 {len(resultado)} resultado(s) encontrado(s)", "Exito.TLabel"
                )

        self.worker.ejecutar(tarea, on_completado)

    def _cancelar_tarea(self) -> None:
        if self.worker.esta_corriendo:
            self.worker.cancelar()

    # ── Acciones sincrónicas ─────────────────────────────────────────

    def _guardar(self, _event: tk.Event | None = None) -> None:
        if self.worker.esta_corriendo:
            return

        destinatario = self.var_destinatario.get()
        direccion = self.var_direccion.get()
        tipo = self.var_tipo.get()
        estado = self.var_estado.get()

        errores = self.controller.validar(destinatario, direccion)
        if errores:
            self._mostrar_estado(f"Error: {' | '.join(errores)}", "Error.TLabel")
            return

        envio = self.controller.registrar(destinatario, direccion, tipo, estado)
        if envio:
            self._agregar_fila(envio)
            self._limpiar()
            self._mostrar_estado(
                f"✓ Envío #{envio.id} registrado correctamente", "Exito.TLabel"
            )

    def _limpiar(self, _event: tk.Event | None = None) -> None:
        self.var_destinatario.set("")
        self.var_direccion.set("")
        self.var_tipo.set(EnvioController.TIPOS[0])
        self.var_estado.set(EnvioController.ESTADOS[0])
        self.var_busqueda.set("")
        self._mostrar_estado("Formulario limpiado", "Status.TLabel")

    def _mostrar_todos(self) -> None:
        self.var_busqueda.set("")
        envios = self.controller.listar()
        self._refrescar_tabla(envios)
        self._mostrar_estado(
            f"📋 Mostrando {len(envios)} envío(s)", "Status.TLabel"
        )

    def _foco_nuevo(self, _event: tk.Event | None = None) -> None:
        self.entry_destinatario.focus_set()
        self._mostrar_estado("Nuevo envío — completa el formulario", "Status.TLabel")

    # ── Helpers ──────────────────────────────────────────────────────

    def _agregar_fila(self, envio) -> None:
        self.tabla.insert(
            "", "end",
            values=(
                envio.id,
                envio.destinatario,
                envio.direccion,
                envio.tipo,
                envio.estado,
                envio.fecha,
            ),
        )

    def _refrescar_tabla(self, envios: list) -> None:
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for envio in envios:
            self._agregar_fila(envio)

    def _mostrar_estado(self, mensaje: str, estilo: str) -> None:
        self.lbl_estado.configure(text=mensaje, style=estilo)

    # ── Atajos de teclado ────────────────────────────────────────────

    def _registrar_atajos(self) -> None:
        self.root.bind("<Control-n>", self._foco_nuevo)
        self.root.bind("<Control-N>", self._foco_nuevo)
        self.root.bind("<Control-s>", self._guardar)
        self.root.bind("<Control-S>", self._guardar)
        self.root.bind("<Escape>", self._limpiar)
