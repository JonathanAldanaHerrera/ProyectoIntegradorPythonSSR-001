🎨 FASE 5 · Componentes visuales avanzados y estilos (sintetiza L5) — 6h
Contexto: Una lista plana no basta. El despachador necesita ordenar, filtrar y leer estados de un vistazo — y que todo se vea coherente.

Actividades detalladas:

1. **Tabla/árbol avanzado**: convierte la lista de envíos en una QTableView/QTreeView o ttk.Treeview con columnas ordenables y agrupación opcional por sucursal (árbol jerárquico).
2. **Barra de filtros**: filtrar por estado (pendiente, en ruta, entregado, retrasado) y por texto, actualizando la tabla en vivo.
3. **Componentes personalizados**: un StatusBadge con color por estado, un KPICard con el conteo del día, reutilizables en toda la app.
4. **Tema y estilos**: centraliza colores/tipografía en logitrack/ui/theme.py; implementa modo claro y oscuro con un toggle. Verifica contraste legible.
5. **Entregable de la fase**: tabla avanzada + filtros + componentes personalizados + toggle de tema; docs/04-componentes.md con capturas en modo claro y oscuro.

Bonus +40 XP: Edición en línea de celdas de la tabla con validación y confirmación visual.