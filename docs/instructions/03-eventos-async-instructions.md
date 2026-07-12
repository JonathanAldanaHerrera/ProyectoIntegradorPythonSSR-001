⚡ FASE 4 · Eventos, señales y asincronía (sintetiza L4) — 6h
Contexto: El pecado capital de una GUI es congelarse. Cuando el despachador pulsa “Buscar” y la app deja de responder, pierdes su confianza.

Actividades detalladas:

1. **Modelo de eventos:** conecta cada control a su manejador vía bindings (Tkinter) o señales/slots (PyQt). Documenta el flujo evento → callback.
2. **Tarea larga simulada:** una consulta que tarda 2–3 segundos (p. ej. cargar todos los envíos). Ejecútala en un hilo/worker o con asyncio, nunca en el hilo de la UI.
3. **Indicador de carga:** mientras la tarea corre, muestra un spinner o barra de progreso y deshabilita el botón; al terminar, actualiza la tabla desde el hilo principal de forma segura.
4. **Manejo de cancelación:** permite cancelar una búsqueda en curso sin dejar la UI en estado inconsistente.
5. **Entregable de la fase:**  demostración (video de 30s) de que la ventana sigue respondiendo mientras corre una tarea larga; docs/03-eventos-async.md con el diagrama de hilos y la estrategia de sincronización con la UI.

Bonus +50 XP: Cola de tareas en segundo plano con varias operaciones concurrentes y su progreso individual reflejado en la UI.