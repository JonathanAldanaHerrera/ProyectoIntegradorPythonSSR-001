# Autoevaluación — LogiTrack Desktop

Tabla cruzada de las 8 lecciones del módulo contra evidencia concreta en el repositorio.

| # | Lección | Competencia clave | Archivos de evidencia | Estado | Observación |
|---|---------|-------------------|-----------------------|--------|-------------|
| L1 | Introducción a la programación visual y frameworks en Python | Panorama de frameworks GUI y elección justificada | `docs/00-fundamentos.md`, `logitrack/app.py` | ✅ | Se eligió Tkinter/ttk sobre PyQt y Flet; la justificación (licencia, stdlib, distribución sin dependencias nativas) está documentada en `docs/00-fundamentos.md`. `app.py` arranca la ventana raíz con `tk.Tk`. |
| L2 | Fundamentos de interfaces gráficas y widgets básicos | Ventana raíz, widgets básicos, bucle principal | `logitrack/views/main_window.py`, `logitrack/views/components.py` | ✅ | `MainWindow` construye etiquetas, entradas, comboboxes, botones, `Treeview` y barra de estado. `components.py` encapsula `KPICard`, `StatusBadge` y `ScrollableFrame` como widgets reutilizables. |
| L3 | Gestión de geometría y diseño de layouts | Layout managers responsivos, sin coordenadas absolutas | `logitrack/views/main_window.py` (`_aplicar_layout_horizontal`, `_aplicar_layout_vertical`), `logitrack/ui/theme.py` (`UMBRAL_RESPONSIVE`) | ✅ | Toda la ventana usa `grid` exclusivamente. El layout cambia entre horizontal (≥ `UMBRAL_RESPONSIVE` px) y vertical dinámicamente en `_on_resize`. Ningún widget usa `place`. |
| L4 | Manejo de eventos, señales y asincronía en interfaces | Bindings, callbacks, tareas en segundo plano sin congelar la UI | `logitrack/controllers/task_worker.py`, `logitrack/views/main_window.py` (`_cargar_async`, `_enriquecer_async`, `_sincronizar_async`) | ✅ | `TaskWorker` ejecuta tareas lentas en `threading.Thread`; los resultados se devuelven al hilo de UI mediante `root.after(0, callback)`. El evento de cancelación `threading.Event` permite interrumpir tareas en curso. |
| L5 | Componentes visuales avanzados y personalización de estilos | Tablas ordenables y filtrables, temas claro/oscuro | `logitrack/views/main_window.py` (`_ordenar_columna`, `_aplicar_filtros`, `_recolorear_filas`), `logitrack/ui/theme.py`, `logitrack/views/components.py` | ✅ | `Treeview` con `displaycolumns` (lat/lng ocultos), ordenamiento por columna, filtro en vivo con `trace_add`. Sistema de temas con `ttk.Style` y paleta `COLORES_ESTADO` con variantes claro/oscuro. |
| L6 | Patrones de arquitectura para aplicaciones GUI (MVC/MVVM) | Separación Modelo / Vista / Controlador | `logitrack/models/envio.py`, `logitrack/services/envio_service.py`, `logitrack/controllers/envio_controller.py`, `logitrack/views/main_window.py`, `tests/unit/test_arquitectura.py`, `docs/05-arquitectura.md` | ✅ | Las vistas reciben solo `dict`, nunca objetos `Envio`. El controlador es una fachada delgada sobre el servicio. Las reglas de dependencia entre capas están verificadas automáticamente por AST en `test_arquitectura.py`. |
| L7 | Integración de datos: bases de datos y consumo de APIs | Persistencia SQLite + API externa | `logitrack/services/sqlite_repository.py`, `logitrack/services/route_api_client.py`, `logitrack/services/envio_service.py` (`enriquecer`, `sincronizar_pendientes`), `docs/06-datos.md` | ✅ | SQLite 3 con WAL mode, `threading.Lock` y patrón repositorio abstracto (`EnvioRepository`). API: Nominatim (geocodificación) + Open-Meteo (clima). Cola offline `pending_ops` con deduplicación en sync. Logger integrado (`logitrack/logger.py`). |
| L8 | Empaquetado, distribución y despliegue | Entorno virtual, dependencias, ejecutable con PyInstaller | `scripts/build.spec`, `scripts/build.sh`, `scripts/build.bat`, `scripts/setup.sh`, `scripts/setup.bat`, `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`, `logitrack/paths.py`, `docs/07-empaquetado.md` | ✅ | `build.spec` congela el paquete con PyInstaller en modo `onedir`. `paths.py` resuelve rutas tanto en modo desarrollo como frozen (`sys.frozen`). `setup.sh/bat` automatizan la creación del venv e instalación de dependencias. |

---

## Resumen

| Estado | Lecciones |
|--------|-----------|
| ✅ Completado | L1, L2, L3, L4, L5, L6, L7, L8 |
| ⚠️ Parcial | — |
| ❌ Pendiente | — |

Todas las competencias del módulo tienen evidencia directa en archivos del repositorio y fueron implementadas de forma incremental a lo largo de las 8 fases del proyecto.
