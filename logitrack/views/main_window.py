import tkinter as tk
import tkinter.ttk as ttk

from logitrack.controllers.envio_controller import EnvioController


class MainWindow:
    """Ventana principal de LogiTrack con tabla de envíos, formulario y barra de estado."""

    def __init__(self, root: tk.Tk, controller: EnvioController) -> None:
        self.root = root
        self.controller = controller

        # Variables del formulario
        self.var_destinatario = tk.StringVar()
        self.var_direccion = tk.StringVar()
        self.var_tipo = tk.StringVar(value=EnvioController.TIPOS[0])
        self.var_estado = tk.StringVar(value=EnvioController.ESTADOS[0])
        self.var_busqueda = tk.StringVar()

        self._construir_interfaz()
        self._registrar_atajos()

    # ── Construcción de la interfaz ──────────────────────────────────

    def _construir_interfaz(self) -> None:
        """Ensambla las 4 zonas de la ventana."""
        self._construir_barra_superior()
        self._construir_area_central()
        self._construir_panel_lateral()
        self._construir_barra_estado()

        # Configurar expansión del grid principal
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

    def _construir_barra_superior(self) -> None:
        """Barra con el título de la aplicación."""
        barra = ttk.Frame(self.root)
        barra.grid(row=0, column=0, columnspan=2, sticky="ew")

        ttk.Label(
            barra,
            text="📦 LogiTrack Desktop — Registro de Envíos",
            style="Titulo.TLabel",
        ).pack(side="left", fill="x", expand=True)

    def _construir_area_central(self) -> None:
        """Tabla Treeview para listar envíos."""
        frame_tabla = ttk.Frame(self.root)
        frame_tabla.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        frame_tabla.columnconfigure(0, weight=1)
        frame_tabla.rowconfigure(0, weight=1)

        columnas = ("id", "destinatario", "direccion", "tipo", "estado", "fecha")
        self.tabla = ttk.Treeview(
            frame_tabla, columns=columnas, show="headings", selectmode="browse"
        )

        # Configurar encabezados y anchos
        encabezados = {
            "id": ("ID", 50),
            "destinatario": ("Destinatario", 160),
            "direccion": ("Dirección", 200),
            "tipo": ("Tipo", 80),
            "estado": ("Estado", 100),
            "fecha": ("Fecha", 130),
        }
        for col, (titulo, ancho) in encabezados.items():
            self.tabla.heading(col, text=titulo)
            self.tabla.column(col, width=ancho, minwidth=40)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(
            frame_tabla, orient="vertical", command=self.tabla.yview
        )
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _construir_panel_lateral(self) -> None:
        """Panel con formulario de alta y búsqueda."""
        panel = ttk.LabelFrame(
            self.root, text="Nuevo Envío", style="Formulario.TLabelframe"
        )
        panel.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)

        fila = 0

        # Destinatario
        ttk.Label(panel, text="Destinatario *").grid(
            row=fila, column=0, sticky="w", pady=(0, 2)
        )
        fila += 1
        self.entry_destinatario = ttk.Entry(
            panel, textvariable=self.var_destinatario, width=25
        )
        self.entry_destinatario.grid(row=fila, column=0, sticky="ew", pady=(0, 8))
        fila += 1

        # Dirección
        ttk.Label(panel, text="Dirección *").grid(
            row=fila, column=0, sticky="w", pady=(0, 2)
        )
        fila += 1
        ttk.Entry(panel, textvariable=self.var_direccion, width=25).grid(
            row=fila, column=0, sticky="ew", pady=(0, 8)
        )
        fila += 1

        # Tipo
        ttk.Label(panel, text="Tipo").grid(
            row=fila, column=0, sticky="w", pady=(0, 2)
        )
        fila += 1
        ttk.Combobox(
            panel,
            textvariable=self.var_tipo,
            values=EnvioController.TIPOS,
            state="readonly",
            width=22,
        ).grid(row=fila, column=0, sticky="ew", pady=(0, 8))
        fila += 1

        # Estado
        ttk.Label(panel, text="Estado").grid(
            row=fila, column=0, sticky="w", pady=(0, 2)
        )
        fila += 1
        ttk.Combobox(
            panel,
            textvariable=self.var_estado,
            values=EnvioController.ESTADOS,
            state="readonly",
            width=22,
        ).grid(row=fila, column=0, sticky="ew", pady=(0, 8))
        fila += 1

        # Botones
        frame_botones = ttk.Frame(panel)
        frame_botones.grid(row=fila, column=0, sticky="ew", pady=(10, 5))

        ttk.Button(frame_botones, text="💾 Guardar", command=self._guardar).pack(
            fill="x", pady=2
        )
        ttk.Button(frame_botones, text="🧹 Limpiar", command=self._limpiar).pack(
            fill="x", pady=2
        )
        fila += 1

        # Separador
        ttk.Separator(panel, orient="horizontal").grid(
            row=fila, column=0, sticky="ew", pady=10
        )
        fila += 1

        # Búsqueda
        ttk.Label(panel, text="Buscar por destinatario").grid(
            row=fila, column=0, sticky="w", pady=(0, 2)
        )
        fila += 1
        ttk.Entry(panel, textvariable=self.var_busqueda, width=25).grid(
            row=fila, column=0, sticky="ew", pady=(0, 8)
        )
        fila += 1
        ttk.Button(frame_botones := ttk.Frame(panel), text="🔍 Buscar", command=self._buscar).pack(
            fill="x", pady=2
        )
        ttk.Button(frame_botones, text="📋 Mostrar todos", command=self._mostrar_todos).pack(
            fill="x", pady=2
        )
        frame_botones.grid(row=fila, column=0, sticky="ew")

        # Expandir columna del panel
        panel.columnconfigure(0, weight=1)

    def _construir_barra_estado(self) -> None:
        """Barra inferior con mensajes de estado."""
        self.lbl_estado = ttk.Label(
            self.root, text="Listo — Ctrl+N: Nuevo | Ctrl+S: Guardar | Esc: Limpiar",
            style="Status.TLabel",
        )
        self.lbl_estado.grid(row=2, column=0, columnspan=2, sticky="ew")

    # ── Acciones ─────────────────────────────────────────────────────

    def _guardar(self, _event: tk.Event | None = None) -> None:
        """Registra un envío vía el controller."""
        destinatario = self.var_destinatario.get()
        direccion = self.var_direccion.get()
        tipo = self.var_tipo.get()
        estado = self.var_estado.get()

        # Validar
        errores = self.controller.validar(destinatario, direccion)
        if errores:
            self._mostrar_estado(f"Error: {' | '.join(errores)}", "Error.TLabel")
            return

        # Registrar
        envio = self.controller.registrar(destinatario, direccion, tipo, estado)
        if envio:
            self._agregar_fila(envio)
            self._limpiar()
            self._mostrar_estado(
                f"✓ Envío #{envio.id} registrado correctamente", "Exito.TLabel"
            )

    def _limpiar(self, _event: tk.Event | None = None) -> None:
        """Limpia los campos del formulario."""
        self.var_destinatario.set("")
        self.var_direccion.set("")
        self.var_tipo.set(EnvioController.TIPOS[0])
        self.var_estado.set(EnvioController.ESTADOS[0])
        self.var_busqueda.set("")
        self._mostrar_estado("Formulario limpiado", "Status.TLabel")

    def _buscar(self) -> None:
        """Filtra la tabla por destinatario."""
        termino = self.var_busqueda.get()
        resultados = self.controller.buscar(termino)
        self._refrescar_tabla(resultados)
        self._mostrar_estado(
            f"🔍 {len(resultados)} resultado(s) encontrado(s)", "Status.TLabel"
        )

    def _mostrar_todos(self) -> None:
        """Muestra todos los envíos en la tabla."""
        self.var_busqueda.set("")
        envios = self.controller.listar()
        self._refrescar_tabla(envios)
        self._mostrar_estado(
            f"📋 Mostrando {len(envios)} envío(s)", "Status.TLabel"
        )

    def _foco_nuevo(self, _event: tk.Event | None = None) -> None:
        """Pone el foco en el campo Destinatario para iniciar un alta."""
        self.entry_destinatario.focus_set()
        self._mostrar_estado("Nuevo envío — completa el formulario", "Status.TLabel")

    # ── Helpers ──────────────────────────────────────────────────────

    def _agregar_fila(self, envio) -> None:
        """Agrega una fila al Treeview."""
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
        """Limpia y recarga la tabla con los envíos dados."""
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for envio in envios:
            self._agregar_fila(envio)

    def _mostrar_estado(self, mensaje: str, estilo: str) -> None:
        """Actualiza el texto y estilo de la barra de estado."""
        self.lbl_estado.configure(text=mensaje, style=estilo)

    # ── Atajos de teclado ────────────────────────────────────────────

    def _registrar_atajos(self) -> None:
        """Registra los atajos de teclado globales."""
        self.root.bind("<Control-n>", self._foco_nuevo)
        self.root.bind("<Control-N>", self._foco_nuevo)
        self.root.bind("<Control-s>", self._guardar)
        self.root.bind("<Control-S>", self._guardar)
        self.root.bind("<Escape>", self._limpiar)
