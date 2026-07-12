# Fase 4 — Eventos, señales y asincronía

## Modelo de eventos

Cada control de la UI está conectado a su manejador mediante bindings de Tkinter o el parámetro `command` de los widgets:

### Mapa de eventos

| Widget | Evento / Binding | Callback | Tipo |
|--------|-----------------|----------|------|
| Botón "Guardar" | `command` | `_guardar()` | Sincrónico |
| Botón "Limpiar" | `command` | `_limpiar()` | Sincrónico |
| Botón "Buscar" | `command` | `_buscar_async()` | Asíncrono (hilo) |
| Botón "Cargar envíos" | `command` | `_cargar_async()` | Asíncrono (hilo) |
| Botón "Mostrar todos" | `command` | `_mostrar_todos()` | Sincrónico |
| Botón "Cancelar" | `command` | `_cancelar_tarea()` | Sincrónico |
| `Ctrl+N` | `bind("<Control-n>")` | `_foco_nuevo()` | Sincrónico |
| `Ctrl+S` | `bind("<Control-s>")` | `_guardar()` | Sincrónico |
| `Esc` | `bind("<Escape>")` | `_limpiar()` | Sincrónico |
| Ventana resize | `bind("<Configure>")` | `_on_resize()` | Sincrónico |

### Flujo evento → callback

```
Usuario interactúa con widget
        │
        ▼
  Tkinter mainloop detecta evento
        │
        ▼
  Callback registrado se ejecuta
        │
        ├── Sincrónico → se ejecuta directo en el hilo principal
        │
        └── Asíncrono → TaskWorker lanza Thread
                │
                ├── Deshabilita botones
                ├── Muestra barra de progreso
                ├── Ejecuta operación en hilo secundario
                │       │
                │       ├── Comprueba cancel_event cada 0.1s
                │       │
                │       └── Al terminar: root.after(callback)
                │
                └── Callback en hilo principal:
                        ├── Actualiza tabla
                        ├── Detiene barra de progreso
                        └── Rehabilita botones
```

## Diagrama de hilos

```
┌─────────────────────────────────────────────────────────────────┐
│                    HILO PRINCIPAL (UI)                          │
│                                                                 │
│  tk.mainloop()                                                  │
│    │                                                            │
│    ├── click "Cargar envíos"                                    │
│    │     ├── _iniciar_progreso()  → progressbar.start()         │
│    │     ├── deshabilita botones                                │
│    │     └── worker.ejecutar(tarea, on_completado)              │
│    │              │                                             │
│    │              │  lanza Thread ──────────────────────┐        │
│    │              │                                    │        │
│    │   (UI sigue respondiendo)                         │        │
│    │   (se puede mover/redimensionar la ventana)       │        │
│    │   (se puede cancelar)                             │        │
│    │              │                                    │        │
│    │              │  ◄── root.after(on_completado) ────┘        │
│    │              │                                             │
│    │     ├── _detener_progreso()  → progressbar.stop()          │
│    │     ├── _refrescar_tabla(resultado)                        │
│    │     └── rehabilita botones                                 │
│    │                                                            │
│    ├── click "Cancelar"                                         │
│    │     └── worker.cancelar() → cancel_event.set()             │
│    │              │                                             │
│    │              │  ◄── hilo detecta cancel_event              │
│    │              │  ◄── root.after(on_completado, None)        │
│    │              │                                             │
│    │     ├── muestra "Carga cancelada"                          │
│    │     └── rehabilita botones                                 │
│    │                                                            │
└────┴────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  HILO SECUNDARIO (Worker)                       │
│                                                                 │
│  threading.Thread(daemon=True)                                  │
│    │                                                            │
│    ├── ejecuta tarea(cancel_event)                              │
│    │     ├── loop: time.sleep(0.1)                              │
│    │     │         if cancel_event.is_set(): return None        │
│    │     └── retorna resultado                                  │
│    │                                                            │
│    └── root.after(0, on_completado, resultado)                  │
│         (agenda callback en el hilo principal)                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Estrategia de sincronización

### ¿Por qué `root.after()`?

Tkinter **no es thread-safe**: modificar widgets desde un hilo secundario causa crashes o comportamiento errático. La solución es `root.after(0, callback)`, que agenda la ejecución del callback en la siguiente iteración del mainloop (hilo principal).

### Mecanismo de cancelación

1. `TaskWorker` expone un `threading.Event` llamado `cancel_event`
2. La operación costosa comprueba `cancel_event.is_set()` en cada iteración de su loop
3. Al hacer click en "Cancelar", se llama `cancel_event.set()`
4. El hilo detecta la señal y retorna `None`
5. El callback `on_completado` recibe `None` y muestra el mensaje de cancelación
6. La UI vuelve a estado normal sin inconsistencias

### Protección contra operaciones concurrentes

- `TaskWorker.esta_corriendo` impide lanzar una segunda tarea
- Los botones se deshabilitan durante la ejecución
- `_guardar()` también verifica que no haya tarea corriendo

## Video demostrativo

Demostración de ~30s donde la ventana sigue respondiendo mientras corre una tarea larga (carga de envíos), incluyendo cancelación en curso.

![Video demostrativo — eventos y asincronía](files/03-eventos-async-evidencia.mp4)
## Archivos nuevos y modificados

| Archivo | Cambio |
|---------|--------|
| `controllers/task_worker.py` | **Nuevo** — Worker con threading, cancelación y root.after() |
| `controllers/envio_controller.py` | Métodos `cargar_envios_lento()` y `buscar_lento()` con simulación de 2.5s y 1.5s |
| `views/main_window.py` | Progressbar, botón cancelar, operaciones async, deshabilitación de botones |
| `ui/theme.py` | Estilos para Progressbar y botón cancelar |
