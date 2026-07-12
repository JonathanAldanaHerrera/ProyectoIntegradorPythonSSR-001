import tkinter as tk
import tkinter.ttk as ttk

from logitrack.controllers.envio_controller import EnvioController
from logitrack.controllers.task_worker import TaskWorker
from logitrack.ui.theme import (
    PAD_SM, PAD_MD, PAD_LG, ANCHO_PANEL, UMBRAL_RESPONSIVE,
    COLORES_ESTADO, cambiar_tema, obtener_tema_actual,
)
from logitrack.views.components import KPICard, StatusBadge, ICONOS_ESTADO


class MainWindow:

    def __init__(self, root: tk.Tk, controller: EnvioController) -> None:
        self.root = root
        self.controller = controller
        self.worker = TaskWorker(root)
        self.style = ttk.Style(root)

        self.var_destinatario = tk.StringVar()
        self.var_direccion = tk.StringVar()
        self.var_tipo = tk.StringVar(value=self.controller.tipos[0])
        self.var_estado = tk.StringVar(value=self.controller.estados[0])
        self.var_sucursal = tk.StringVar(value=self.controller.sucursales[0])
        self.var_busqueda = tk.StringVar()
        self.var_filtro_estado = tk.StringVar(value="Todos")
        self.var_filtro_texto = tk.StringVar()

        self._layout_horizontal = True
        self._botones_accion: list[ttk.Button] = []
        self._orden_columna: str = ""
        self._orden_reverso: bool = False
        self._editor_activo: tk.Widget | None = None
        self._badge_widget: tk.Widget | None = None
        self._supresion_filtros: bool = False

        self._construir_widgets()
        self._aplicar_layout_horizontal()
        self._registrar_atajos()
        self._registrar_filtros_en_vivo()

        self.root.bind("<Configure>", self._on_resize)

    # ── Widgets ──────────────────────────────────────────────────────

    def _construir_widgets(self) -> None:
        self._crear_barra_superior()
        self._crear_barra_filtros()
        self._crear_barra_kpis()
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

        self.lbl_red = ttk.Label(self.barra_superior, text="⚪", style="Filtros.TLabel")
        self.lbl_red.grid(row=0, column=1, sticky="e", padx=PAD_SM)

        self.btn_tema = ttk.Button(
            self.barra_superior, text="🌙", style="Toggle.TButton",
            command=self._toggle_tema, width=3,
        )
        self.btn_tema.grid(row=0, column=2, sticky="e", padx=PAD_SM)

        self.barra_superior.columnconfigure(0, weight=1)

    def _crear_barra_filtros(self) -> None:
        self.frame_filtros = ttk.Frame(self.root, style="Filtros.TFrame")

        ttk.Label(self.frame_filtros, text="Filtrar estado:", style="Filtros.TLabel").pack(
            side="left", padx=(0, PAD_SM)
        )
        opciones_estado = ["Todos"] + list(self.controller.estados)
        ttk.Combobox(
            self.frame_filtros, textvariable=self.var_filtro_estado,
            values=opciones_estado, state="readonly", width=14, style="Filtros.TCombobox",
        ).pack(side="left", padx=(0, PAD_LG))

        ttk.Label(self.frame_filtros, text="Buscar:", style="Filtros.TLabel").pack(
            side="left", padx=(0, PAD_SM)
        )
        ttk.Entry(self.frame_filtros, textvariable=self.var_filtro_texto, width=20).pack(
            side="left", padx=(0, PAD_SM)
        )

    def _crear_barra_kpis(self) -> None:
        self.frame_kpis = ttk.Frame(self.root)
        self.kpi_cards: dict[str, KPICard] = {}

        for estado in self.controller.estados:
            icono = ICONOS_ESTADO.get(estado, "📦")
            card = KPICard(self.frame_kpis, estado, icono)
            card.pack(side="left", fill="x", expand=True, padx=PAD_SM, pady=PAD_SM)
            self.kpi_cards[estado] = card

    def _crear_area_tabla(self) -> None:
        self.frame_tabla = ttk.Frame(self.root)
        self.frame_tabla.columnconfigure(0, weight=1)
        self.frame_tabla.rowconfigure(0, weight=1)

        columnas = ("id", "destinatario", "direccion", "tipo", "estado", "sucursal", "fecha", "clima", "lat", "lng")
        visibles = ("id", "destinatario", "direccion", "tipo", "estado", "sucursal", "fecha", "clima")
        self.tabla = ttk.Treeview(
            self.frame_tabla, columns=columnas, displaycolumns=visibles,
            show="headings", selectmode="browse"
        )

        encabezados = {
            "id": ("ID", 50, False),
            "destinatario": ("Destinatario", 130, True),
            "direccion": ("Dirección", 160, True),
            "tipo": ("Tipo", 70, False),
            "estado": ("Estado", 90, False),
            "sucursal": ("Sucursal", 80, False),
            "fecha": ("Fecha", 110, False),
            "clima": ("Clima / Ruta", 155, True),
        }
        for col, (titulo, ancho, stretch) in encabezados.items():
            self.tabla.heading(col, text=titulo, command=lambda c=col: self._ordenar_columna(c))
            self.tabla.column(col, width=ancho, minwidth=40, stretch=stretch)

        for estado, colores in COLORES_ESTADO.items():
            self.tabla.tag_configure(estado, background=colores["tag_bg"], foreground=colores["fg"])

        self.scrollbar = ttk.Scrollbar(
            self.frame_tabla, orient="vertical", command=self.tabla.yview
        )
        self.tabla.configure(yscrollcommand=self.scrollbar.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.tabla.bind("<Double-1>", self._iniciar_edicion_inline)
        self.tabla.bind("<<TreeviewSelect>>", self._on_seleccion_tabla)

    def _crear_panel_formulario(self) -> None:
        self.panel = ttk.LabelFrame(
            self.root, text="Nuevo Envío", style="Formulario.TLabelframe"
        )

        fila = 0

        ttk.Label(self.panel, text="Destinatario *").grid(row=fila, column=0, sticky="w", pady=(0, PAD_SM))
        fila += 1
        self.entry_destinatario = ttk.Entry(self.panel, textvariable=self.var_destinatario, width=25)
        self.entry_destinatario.grid(row=fila, column=0, sticky="ew", pady=(0, PAD_MD))
        fila += 1

        ttk.Label(self.panel, text="Dirección *").grid(row=fila, column=0, sticky="w", pady=(0, PAD_SM))
        fila += 1
        ttk.Entry(self.panel, textvariable=self.var_direccion, width=25).grid(row=fila, column=0, sticky="ew", pady=(0, PAD_MD))
        fila += 1

        ttk.Label(self.panel, text="Tipo").grid(row=fila, column=0, sticky="w", pady=(0, PAD_SM))
        fila += 1
        ttk.Combobox(self.panel, textvariable=self.var_tipo, values=self.controller.tipos, state="readonly", width=22).grid(
            row=fila, column=0, sticky="ew", pady=(0, PAD_MD))
        fila += 1

        ttk.Label(self.panel, text="Estado").grid(row=fila, column=0, sticky="w", pady=(0, PAD_SM))
        fila += 1
        ttk.Combobox(self.panel, textvariable=self.var_estado, values=self.controller.estados, state="readonly", width=22).grid(
            row=fila, column=0, sticky="ew", pady=(0, PAD_MD))
        fila += 1

        ttk.Label(self.panel, text="Sucursal").grid(row=fila, column=0, sticky="w", pady=(0, PAD_SM))
        fila += 1
        ttk.Combobox(self.panel, textvariable=self.var_sucursal, values=self.controller.sucursales, state="readonly", width=22).grid(
            row=fila, column=0, sticky="ew", pady=(0, PAD_MD))
        fila += 1

        frame_acciones = ttk.Frame(self.panel)
        frame_acciones.grid(row=fila, column=0, sticky="ew", pady=(PAD_MD, PAD_SM))
        btn_guardar = ttk.Button(frame_acciones, text="💾 Guardar", command=self._guardar)
        btn_guardar.pack(fill="x", pady=2)
        btn_limpiar = ttk.Button(frame_acciones, text="🧹 Limpiar", command=self._limpiar)
        btn_limpiar.pack(fill="x", pady=2)
        self._botones_accion.extend([btn_guardar, btn_limpiar])
        fila += 1

        ttk.Separator(self.panel, orient="horizontal").grid(row=fila, column=0, sticky="ew", pady=PAD_MD)
        fila += 1

        # ── Detalle selección + enriquecimiento ──────────────────────
        frame_seleccion = ttk.Frame(self.panel)
        frame_seleccion.grid(row=fila, column=0, sticky="ew", pady=(0, PAD_SM))
        ttk.Label(frame_seleccion, text="Seleccionado:", style="Filtros.TLabel").pack(side="left")
        self.lbl_seleccion_nombre = ttk.Label(frame_seleccion, text="—", style="Filtros.TLabel")
        self.lbl_seleccion_nombre.pack(side="left", padx=(PAD_SM, 0))
        self.frame_badge_seleccion = frame_seleccion
        fila += 1

        frame_enrich = ttk.Frame(self.panel)
        frame_enrich.grid(row=fila, column=0, sticky="ew", pady=(0, PAD_SM))

        ttk.Label(frame_enrich, text="📍", style="Filtros.TLabel").grid(row=0, column=0, sticky="w")
        self.lbl_lat_lng = ttk.Label(frame_enrich, text="—", style="Filtros.TLabel")
        self.lbl_lat_lng.grid(row=0, column=1, sticky="w", padx=(PAD_SM, 0))

        ttk.Label(frame_enrich, text="🌡", style="Filtros.TLabel").grid(row=1, column=0, sticky="w")
        self.lbl_clima_detalle = ttk.Label(frame_enrich, text="—", style="Filtros.TLabel", wraplength=190)
        self.lbl_clima_detalle.grid(row=1, column=1, sticky="w", padx=(PAD_SM, 0))

        frame_btn_enrich = ttk.Frame(frame_enrich)
        frame_btn_enrich.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(PAD_SM, 0))
        self.btn_enriquecer = ttk.Button(
            frame_btn_enrich, text="🌍 Enriquecer ruta",
            command=self._enriquecer_async, state="disabled",
        )
        self.btn_enriquecer.pack(side="left", fill="x", expand=True, padx=(0, 2))
        self.btn_sincronizar = ttk.Button(
            frame_btn_enrich, text="🔄 Sincronizar",
            command=self._sincronizar_async,
        )
        self.btn_sincronizar.pack(side="left", fill="x", expand=True, padx=(2, 0))
        frame_enrich.columnconfigure(1, weight=1)
        fila += 1

        frame_busqueda = ttk.Frame(self.panel)
        frame_busqueda.grid(row=fila, column=0, sticky="ew")
        btn_cargar = ttk.Button(frame_busqueda, text="📦 Cargar envíos", command=self._cargar_async)
        btn_cargar.pack(fill="x", pady=2)
        btn_todos = ttk.Button(frame_busqueda, text="📋 Mostrar todos", command=self._mostrar_todos)
        btn_todos.pack(fill="x", pady=2)
        self._botones_accion.extend([btn_cargar, btn_todos])

        self.panel.columnconfigure(0, weight=1)

    def _crear_barra_progreso(self) -> None:
        self.frame_progreso = ttk.Frame(self.root)
        self.progressbar = ttk.Progressbar(
            self.frame_progreso, mode="indeterminate",
            style="Progreso.Horizontal.TProgressbar",
        )
        self.progressbar.pack(side="left", fill="x", expand=True, padx=(0, PAD_MD))

        self.btn_cancelar = ttk.Button(
            self.frame_progreso, text="✕ Cancelar",
            style="Cancelar.TButton", command=self._cancelar_tarea,
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
        for w in (self.barra_superior, self.frame_filtros, self.frame_kpis,
                  self.frame_tabla, self.panel, self.frame_progreso, self.lbl_estado):
            w.grid_forget()

        r = 0
        self.barra_superior.grid(row=r, column=0, columnspan=2, sticky="ew", padx=PAD_LG, pady=(PAD_LG, 0)); r += 1
        self.frame_filtros.grid(row=r, column=0, columnspan=2, sticky="ew", padx=PAD_LG, pady=(PAD_MD, 0)); r += 1
        self.frame_kpis.grid(row=r, column=0, columnspan=2, sticky="ew", padx=PAD_LG, pady=(PAD_MD, 0)); r += 1
        self.frame_tabla.grid(row=r, column=0, sticky="nsew", padx=(PAD_LG, PAD_SM), pady=PAD_MD)
        self.panel.grid(row=r, column=1, sticky="nsew", padx=(PAD_SM, PAD_LG), pady=PAD_MD); r += 1
        # row r reserved for progress
        r += 1
        self.lbl_estado.grid(row=r, column=0, columnspan=2, sticky="ew")

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0, minsize=ANCHO_PANEL)
        for i in range(r + 1):
            self.root.rowconfigure(i, weight=0)
        self.root.rowconfigure(3, weight=1)

        self._layout_horizontal = True

    def _aplicar_layout_vertical(self) -> None:
        for w in (self.barra_superior, self.frame_filtros, self.frame_kpis,
                  self.frame_tabla, self.panel, self.frame_progreso, self.lbl_estado):
            w.grid_forget()

        r = 0
        self.barra_superior.grid(row=r, column=0, sticky="ew", padx=PAD_LG, pady=(PAD_LG, 0)); r += 1
        self.frame_filtros.grid(row=r, column=0, sticky="ew", padx=PAD_LG, pady=(PAD_MD, 0)); r += 1
        self.frame_kpis.grid(row=r, column=0, sticky="ew", padx=PAD_LG, pady=(PAD_MD, 0)); r += 1
        self.panel.grid(row=r, column=0, sticky="ew", padx=PAD_LG, pady=(PAD_MD, 0)); r += 1
        self.frame_tabla.grid(row=r, column=0, sticky="nsew", padx=PAD_LG, pady=PAD_MD); r += 1
        # row r reserved for progress
        r += 1
        self.lbl_estado.grid(row=r, column=0, sticky="ew")

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0, minsize=0)
        for i in range(r + 1):
            self.root.rowconfigure(i, weight=0)
        self.root.rowconfigure(4, weight=1)

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

        prog_row = 4 if self._layout_horizontal else 5
        colspan = 2 if self._layout_horizontal else 1
        self.frame_progreso.grid(row=prog_row, column=0, columnspan=colspan, sticky="ew", padx=PAD_LG, pady=(0, PAD_SM))
        self.progressbar.start(15)

    def _detener_progreso(self) -> None:
        self.progressbar.stop()
        self.frame_progreso.grid_forget()
        for btn in self._botones_accion:
            btn.configure(state="normal")

    # ── Filtros en vivo ──────────────────────────────────────────────

    def _registrar_filtros_en_vivo(self) -> None:
        self.var_filtro_estado.trace_add("write", lambda *_: self._aplicar_filtros())
        self.var_filtro_texto.trace_add("write", lambda *_: self._aplicar_filtros())

    def _aplicar_filtros(self) -> None:
        if self._supresion_filtros:
            return
        estado = self.var_filtro_estado.get()
        texto = self.var_filtro_texto.get()
        resultados = self.controller.filtrar(estado, texto)
        self._refrescar_tabla(resultados)
        self._mostrar_estado(f"🔍 {len(resultados)} envío(s) filtrado(s)", "Status.TLabel")

    # ── Ordenamiento de columnas ─────────────────────────────────────

    def _ordenar_columna(self, columna: str) -> None:
        if self._orden_columna == columna:
            self._orden_reverso = not self._orden_reverso
        else:
            self._orden_columna = columna
            self._orden_reverso = False

        filas = [(self.tabla.set(item, columna), item) for item in self.tabla.get_children()]

        try:
            filas.sort(key=lambda x: int(x[0]), reverse=self._orden_reverso)
        except ValueError:
            filas.sort(key=lambda x: x[0].lower(), reverse=self._orden_reverso)

        for idx, (_, item) in enumerate(filas):
            self.tabla.move(item, "", idx)

        indicador = " ▼" if self._orden_reverso else " ▲"
        _encabezados = {
            "id": "ID", "destinatario": "Destinatario", "direccion": "Dirección",
            "tipo": "Tipo", "estado": "Estado", "sucursal": "Sucursal",
            "fecha": "Fecha", "clima": "Clima / Ruta",
        }
        for col in self.tabla["displaycolumns"]:
            texto = _encabezados.get(col, col.capitalize())
            if col == columna:
                texto += indicador
            self.tabla.heading(col, text=texto)

    # ── Edición inline (bonus) ───────────────────────────────────────

    def _iniciar_edicion_inline(self, event: tk.Event) -> None:
        if self._editor_activo:
            self._cancelar_edicion()

        region = self.tabla.identify_region(event.x, event.y)
        if region != "cell":
            return

        columna = self.tabla.identify_column(event.x)
        item = self.tabla.identify_row(event.y)
        if not item or not columna:
            return

        col_idx = int(columna.replace("#", "")) - 1
        col_names = list(self.tabla["columns"])
        if col_idx < 0 or col_idx >= len(col_names):
            return

        col_name = col_names[col_idx]
        if col_name in ("id", "fecha", "lat", "lng", "clima"):
            return

        valor_actual = self.tabla.set(item, col_name)
        bbox = self.tabla.bbox(item, columna)
        if not bbox:
            return

        x, y, w, h = bbox

        if col_name == "estado":
            editor = ttk.Combobox(self.tabla, values=list(self.controller.estados), state="readonly", width=w // 8)
            editor.set(valor_actual)
        elif col_name == "tipo":
            editor = ttk.Combobox(self.tabla, values=list(self.controller.tipos), state="readonly", width=w // 8)
            editor.set(valor_actual)
        elif col_name == "sucursal":
            editor = ttk.Combobox(self.tabla, values=list(self.controller.sucursales), state="readonly", width=w // 8)
            editor.set(valor_actual)
        else:
            editor = ttk.Entry(self.tabla, width=w // 8)
            editor.insert(0, valor_actual)
            editor.select_range(0, tk.END)

        editor.place(x=x, y=y, width=w, height=h)
        editor.focus_set()

        editor._edit_item = item
        editor._edit_col = col_name
        editor._edit_old = valor_actual

        editor.bind("<Return>", self._confirmar_edicion)
        editor.bind("<Escape>", lambda e: self._cancelar_edicion())
        editor.bind("<FocusOut>", lambda e: self._confirmar_edicion(e))
        if isinstance(editor, ttk.Combobox):
            editor.bind("<<ComboboxSelected>>", self._confirmar_edicion)

        self._editor_activo = editor

    def _confirmar_edicion(self, event: tk.Event | None = None) -> None:
        if not self._editor_activo:
            return

        editor = self._editor_activo
        nuevo_valor = editor.get().strip()
        item = editor._edit_item
        col_name = editor._edit_col
        viejo_valor = editor._edit_old

        self._editor_activo = None
        editor.destroy()

        if not nuevo_valor or nuevo_valor == viejo_valor:
            return

        envio_id = int(self.tabla.set(item, "id"))
        if self.controller.actualizar_envio(envio_id, col_name, nuevo_valor):
            self.tabla.set(item, col_name, nuevo_valor)
            if col_name == "estado":
                self.tabla.item(item, tags=(nuevo_valor,))
                self._actualizar_kpis()
                self._on_seleccion_tabla(None)
            self._mostrar_estado(f"✓ {col_name} actualizado", "Exito.TLabel")

    def _cancelar_edicion(self) -> None:
        if self._editor_activo:
            self._editor_activo.destroy()
            self._editor_activo = None

    def _on_seleccion_tabla(self, event: tk.Event | None) -> None:
        if self._badge_widget:
            self._badge_widget.destroy()
            self._badge_widget = None
        seleccion = self.tabla.selection()
        if not seleccion:
            self.lbl_seleccion_nombre.configure(text="—")
            self.lbl_lat_lng.configure(text="—")
            self.lbl_clima_detalle.configure(text="—")
            self.btn_enriquecer.configure(state="disabled")
            return
        item = seleccion[0]
        nombre = self.tabla.set(item, "destinatario")
        estado = self.tabla.set(item, "estado")
        self.lbl_seleccion_nombre.configure(text=nombre)
        self._badge_widget = StatusBadge(self.frame_badge_seleccion, estado)
        self._badge_widget.pack(side="left", padx=(PAD_SM, 0))

        lat = self.tabla.set(item, "lat")
        lng = self.tabla.set(item, "lng")
        clima = self.tabla.set(item, "clima")
        self.lbl_lat_lng.configure(
            text=f"{float(lat):.4f}, {float(lng):.4f}" if lat else "—"
        )
        self.lbl_clima_detalle.configure(text=clima if clima and clima != "—" else "—")
        self.btn_enriquecer.configure(state="normal")

    # ── Toggle de tema ───────────────────────────────────────────────

    def _toggle_tema(self) -> None:
        nuevo = cambiar_tema(self.style, self.root)
        self.btn_tema.configure(text="☀️" if nuevo == "oscuro" else "🌙")
        self._recolorear_filas()
        for card in self.kpi_cards.values():
            card.refrescar_colores()

    def _recolorear_filas(self) -> None:
        oscuro = obtener_tema_actual() == "oscuro"
        for estado, colores in COLORES_ESTADO.items():
            tag_bg = colores["tag_bg_oscuro"] if oscuro else colores["tag_bg"]
            tag_fg = colores["tag_fg_oscuro"] if oscuro else colores["fg"]
            self.tabla.tag_configure(estado, background=tag_bg, foreground=tag_fg)

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
                self._actualizar_kpis()
                self._mostrar_estado(f"✓ {len(resultado)} envío(s) cargado(s)", "Exito.TLabel")

        self.worker.ejecutar(tarea, on_completado, lambda e: (self._detener_progreso(), self._mostrar_estado(f"Error: {e}", "Error.TLabel")))

    def _cancelar_tarea(self) -> None:
        if self.worker.esta_corriendo:
            self.worker.cancelar()

    def _enriquecer_async(self) -> None:
        seleccion = self.tabla.selection()
        if not seleccion or self.worker.esta_corriendo:
            return
        item = seleccion[0]
        envio_id = int(self.tabla.set(item, "id"))
        self._iniciar_progreso("Obteniendo datos de ruta")

        def tarea(cancel_event):
            return self.controller.enriquecer_envio_async(envio_id, cancel_event)

        def on_completado(resultado):
            self._detener_progreso()
            if resultado is None:
                self._mostrar_estado(
                    "⚠ Sin conexión — operación encolada para sincronizar", "Error.TLabel"
                )
                self._actualizar_estado_red("sin_conexion")
            else:
                clima_display = resultado.get("clima") or "—"
                self.tabla.set(item, "clima", clima_display)
                self.tabla.set(item, "lat", str(resultado.get("lat") or ""))
                self.tabla.set(item, "lng", str(resultado.get("lng") or ""))
                self._on_seleccion_tabla(None)
                self._mostrar_estado("✓ Ruta enriquecida correctamente", "Exito.TLabel")
                self._actualizar_estado_red("ok")

        self.worker.ejecutar(
            tarea, on_completado,
            lambda e: (self._detener_progreso(),
                       self._mostrar_estado(f"Error: {e}", "Error.TLabel")),
        )

    def _sincronizar_async(self) -> None:
        if self.worker.esta_corriendo:
            return
        self._iniciar_progreso("Sincronizando operaciones pendientes")

        def tarea(cancel_event):
            return self.controller.sincronizar_pendientes_async(cancel_event)

        def on_completado(resultado):
            self._detener_progreso()
            if resultado is None:
                self._mostrar_estado("⚠ Sincronización cancelada", "Error.TLabel")
                return
            exitosas, pendientes = resultado
            self._refrescar_tabla(self.controller.listar())
            self._actualizar_kpis()
            if pendientes == 0:
                self._mostrar_estado(
                    f"✓ Sincronización completa — {exitosas} op(s) procesada(s)", "Exito.TLabel"
                )
                self._actualizar_estado_red("ok")
            else:
                self._mostrar_estado(
                    f"⚠ Sincronizadas {exitosas}, {pendientes} aún pendiente(s)", "Status.TLabel"
                )

        self.worker.ejecutar(
            tarea, on_completado,
            lambda e: (self._detener_progreso(),
                       self._mostrar_estado(f"Error: {e}", "Error.TLabel")),
        )

    def _actualizar_estado_red(self, estado: str) -> None:
        iconos = {"ok": "🟢", "sin_conexion": "🔴", "sin_datos": "🟡"}
        self.lbl_red.configure(text=iconos.get(estado, "⚪"))

    # ── Acciones sincrónicas ─────────────────────────────────────────

    def _guardar(self, _event: tk.Event | None = None) -> None:
        if self.worker.esta_corriendo:
            return

        destinatario = self.var_destinatario.get()
        direccion = self.var_direccion.get()
        tipo = self.var_tipo.get()
        estado = self.var_estado.get()
        sucursal = self.var_sucursal.get()

        errores = self.controller.validar(destinatario, direccion)
        if errores:
            self._mostrar_estado(f"Error: {' | '.join(errores)}", "Error.TLabel")
            return

        envio = self.controller.registrar(destinatario, direccion, tipo, estado, sucursal)
        if envio:
            self._agregar_fila(envio)
            self._actualizar_kpis()
            self._limpiar()
            self._mostrar_estado(f"✓ Envío #{envio['id']} registrado correctamente", "Exito.TLabel")

    def _limpiar(self, _event: tk.Event | None = None) -> None:
        self.var_destinatario.set("")
        self.var_direccion.set("")
        self.var_tipo.set(self.controller.tipos[0])
        self.var_estado.set(self.controller.estados[0])
        self.var_sucursal.set(self.controller.sucursales[0])
        self._mostrar_estado("Formulario limpiado", "Status.TLabel")

    def _mostrar_todos(self) -> None:
        self._supresion_filtros = True
        self.var_filtro_estado.set("Todos")
        self.var_filtro_texto.set("")
        self._supresion_filtros = False
        envios = self.controller.listar()
        self._refrescar_tabla(envios)
        self._actualizar_kpis()
        self._mostrar_estado(f"📋 Mostrando {len(envios)} envío(s)", "Status.TLabel")

    def _foco_nuevo(self, _event: tk.Event | None = None) -> None:
        self.entry_destinatario.focus_set()
        self._mostrar_estado("Nuevo envío — completa el formulario", "Status.TLabel")

    # ── Helpers ──────────────────────────────────────────────────────

    def _agregar_fila(self, envio: dict) -> None:
        self.tabla.insert(
            "", "end", tags=(envio["estado"],),
            values=(
                envio["id"], envio["destinatario"], envio["direccion"],
                envio["tipo"], envio["estado"], envio["sucursal"], envio["fecha"],
                envio.get("clima") or "—",
                envio.get("lat") or "",
                envio.get("lng") or "",
            ),
        )

    def _refrescar_tabla(self, envios: list) -> None:
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for envio in envios:
            self._agregar_fila(envio)

    def _actualizar_kpis(self) -> None:
        conteos = self.controller.conteos_por_estado()
        for estado, card in self.kpi_cards.items():
            card.actualizar(conteos.get(estado, 0))

    def _mostrar_estado(self, mensaje: str, estilo: str) -> None:
        self.lbl_estado.configure(text=mensaje, style=estilo)

    # ── Atajos de teclado ────────────────────────────────────────────

    def _registrar_atajos(self) -> None:
        self.root.bind("<Control-n>", self._foco_nuevo)
        self.root.bind("<Control-N>", self._foco_nuevo)
        self.root.bind("<Control-s>", self._guardar)
        self.root.bind("<Control-S>", self._guardar)
        self.root.bind("<Escape>", self._limpiar)
