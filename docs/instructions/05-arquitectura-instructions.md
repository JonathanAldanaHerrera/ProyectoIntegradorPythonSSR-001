🏛️ FASE 6 · Arquitectura MVC/MVVM (sintetiza L6) — 6h
Contexto: Hasta ahora la app funciona, pero si la lógica vive dentro de los widgets, crecerá imposible. Aquí impones orden.

Actividades detalladas:

Reorganiza el código bajo MVC (o MVVM):

```bash
logitrack/
├── models/ # esquemas + acceso a datos (CERO UI)
├── views/ # widgets + bindings (CERO lógica de negocio)
├── controllers/ # eventos UI → llamadas a servicios
├── services/ # lógica de negocio (ShipmentService…)
├── ui/theme.py # tema compartido
└── app.py # bootstrap + inyección de dependencias
```

1. **Regla de dependencia:** las clases en views/ no importan nada de models/. Si lo hacen, refactor obligatorio.

2. **Controlador/ViewModel:** traduce cada evento de la vista en una llamada a un servicio y devuelve datos ya listos para pintar.

3. **Justificación:** en docs/05-arquitectura.md explica por qué MVC o MVVM para esta app (250 palabras), con un diagrama de dependencias.

4. **Entregable de la fase:** código reorganizado por capas, test que verifica que views/ no importa models/, y docs/05-arquitectura.md con el diagrama y la justificación.

Bonus +50 XP: Contenedor de inyección de dependencias que permita cambiar el backend de datos (SQLite ↔ memoria) sin tocar vistas ni controladores.
