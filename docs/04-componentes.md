# Fase 5 — Componentes visuales avanzados y estilos

## Implementación de componentes

Se ha implementado una tabla avanzada con ordenamiento, barra de filtros en vivo, componentes personalizados y un sistema de temas claro/oscuro.

### 1. Tabla Avanzada (Treeview)

- **Ordenamiento**: Al hacer clic en los encabezados de las columnas, la tabla se ordena de forma ascendente o descendente. Un indicador visual (▲/▼) muestra el estado actual.
- **Tags de colores**: Las filas se colorean de acuerdo al estado del envío, utilizando colores definidos en el sistema de temas (fondo claro para modo claro, fondo más oscuro para modo oscuro).
- **Edición en línea (Bonus)**: Se habilitó la edición en línea haciendo doble clic en una celda. Aparece un `Entry` o `Combobox` temporal que permite modificar valores directamente. Se actualizan automáticamente los KPIs y colores si cambia el estado.

### 2. Barra de filtros

- **Filtro por estado**: Un `Combobox` para seleccionar el estado a mostrar (Todos, Pendiente, En tránsito, Entregado, Retrasado).
- **Filtro por texto**: Un `Entry` que busca coincidencias parciales en el nombre del destinatario o en la dirección.
- Ambos filtros operan en tiempo real (`trace_add` sobre variables de Tkinter) actualizando la tabla dinámicamente sin requerir un botón de confirmación.

### 3. Componentes personalizados

- **KPICard**: Un componente de tarjeta compacto, reutilizable, que muestra el recuento en vivo de cada estado, junto a un icono descriptivo.
- **StatusBadge**: Etiqueta (Label) reutilizable con el color y fondo correspondiente a un estado particular.

### 4. Sistema de temas (Claro / Oscuro)

- Toda la configuración visual y colores fueron centralizados en `ui/theme.py`.
- Se definió un diccionario con las paletas de colores completas para ambos temas.
- Un botón en la barra superior (☀️/🌙) permite alternar de forma inmediata entre el modo claro y el oscuro, volviendo a aplicar el estilo y actualizando los colores específicos por estado de las filas del árbol.

## Capturas de pantalla

_Tema Claro_
![Modo Claro](files/04-tema-claro.png)

_Tema Oscuro_
![Modo Oscuro](files/04-tema-oscuro.png)

## Archivos nuevos y modificados

| Archivo                           | Cambio                                                                               |
| --------------------------------- | ------------------------------------------------------------------------------------ |
| `models/envio.py`                 | Se agregó "Retrasado" a los estados posibles y un campo de "Sucursal".               |
| `controllers/envio_controller.py` | Métodos `filtrar()`, `conteos_por_estado()` y `actualizar_envio()`.                  |
| `ui/theme.py`                     | Sistema completo de temas claro/oscuro y diccionario de paletas.                     |
| `views/components.py`             | Nuevos componentes `KPICard` y `StatusBadge`.                                        |
| `views/main_window.py`            | Barra de filtros, panel KPI, toggle de tema, ordenamiento de tabla y edición inline. |
