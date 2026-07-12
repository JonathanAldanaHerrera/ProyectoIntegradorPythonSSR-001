# Fase 6 — Arquitectura MVC con capa de servicios

## Justificación del patrón elegido

LogiTrack adopta **MVC con capa de servicios explícita**, una variante del MVC clásico que agrega una capa intermedia entre el controlador y los modelos. La razón principal es la separación estricta de responsabilidades a medida que la app crece.

En un MVC puro el controlador concentra tanto la traducción de eventos de la vista como la lógica de negocio. Esto funciona en prototipos, pero se vuelve frágil rápidamente: validaciones, filtros y cálculos quedan enterrados entre llamadas a la UI. La capa `services/` resuelve esto extrayendo toda la lógica a una clase independiente (`EnvioService`) que no sabe nada de Tkinter, no maneja hilos y es fácil de testear en aislamiento.

El controlador (`EnvioController`) queda como coordinador delgado: recibe el evento de la vista, llama al servicio y retorna datos listos para pintar —siempre en forma de `dict`, nunca como objetos del modelo. Esto garantiza que `views/` sea completamente ciega a `models/`, cumpliendo la regla de dependencia más importante del patrón.

Se optó por MVC sobre MVVM porque Tkinter no tiene un sistema de bindings bidireccional nativo (las `StringVar` son solo para primitivos). Un ViewModel completo requeriría una capa de observabilidad que añadiría complejidad sin beneficio claro para el tamaño actual de la app. MVC con servicios ofrece el mismo aislamiento con menos abstracción.

El bonus de inyección de dependencias se resuelve con un `Container` en `app.py`: ensambla `EnvioRepository → EnvioService → EnvioController` y permite cambiar el backend de datos pasando un repositorio distinto, sin tocar ni vistas ni controladores.

## Diagrama de dependencias

```
┌─────────────────────────────────────────────────────────┐
│  views/                                                 │
│  MainWindow ──────────────────────────────────────────► │ ui/theme.py
│      │                                                  │
│      │  llama a                                         │
│      ▼                                                  │
│  controllers/                                           │
│  EnvioController ─────────────────────────────────────► │ services/
│                                                         │ EnvioService
│                                                         │     │
│                                                         │     │ importa
│                                                         │     ▼
│                                                         │ models/
│                                                         │ Envio
│                                                         │     │
│                                                         │     ▲
│                                                         │ services/
│                                                         │ EnvioRepository
│                                                         │ MemoryRepository
└─────────────────────────────────────────────────────────┘

Reglas verificadas por tests:
  views/       ✗ → models/
  services/    ✗ → views/
  services/    ✗ → controllers/
  controllers/ ✗ → models/
```

## Estructura de archivos

```
logitrack/
├── models/
│   └── envio.py              # Esquema de datos puro
├── services/
│   └── envio_service.py      # Lógica de negocio + repositorio abstracto
├── controllers/
│   ├── envio_controller.py   # Coordinador delgado
│   └── task_worker.py        # Worker de tareas asíncronas
├── views/
│   ├── components.py         # Widgets reutilizables
│   └── main_window.py        # UI — cero imports de models/
├── ui/
│   └── theme.py              # Paleta y estilos centralizados
└── app.py                    # Bootstrap + Container (DI)
```

## Cómo cambiar el backend (bonus DI)

```python
# Memoria (default)
App().run()

# SQLite (cuando se implemente SQLiteRepository)
from logitrack.services.envio_service import SQLiteRepository
App(repo=SQLiteRepository("logitrack.db")).run()
```

## Ejecución de tests

```bash
python -m pytest tests/test_arquitectura.py -v
```
