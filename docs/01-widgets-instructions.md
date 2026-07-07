🧱 FASE 2 · Ventana principal y widgets básicos (sintetiza L2) — 5h
Contexto: El despachador necesita una ventana donde registrar y ver envíos. Aquí nacen los widgets base.

Actividades detalladas:

1. **Ventana principal** con: barra superior de título, área central para la tabla de envíos, panel lateral con el formulario de alta (destinatario, dirección, tipo, estado) y una barra de estado inferior.
2. **Widgets básicos**: etiquetas, campos de entrada, combos de selección, botones (Guardar, Limpiar, Buscar).
3. **Bucle principal**: la app corre su mainloop/exec() y responde a los controles (todavía con datos en memoria).
4. **Validación básica de formulario**: campos obligatorios, feedback visible al usuario.

**Entregable de la fase**: ventana funcional donde se puede dar de alta un envío (en memoria) y verlo listado; screenshot en docs/01-widgets.md.

**Bonus +30 XP**: Atajos de teclado para las acciones principales (alta = Ctrl+N, limpiar = Esc) documentados.