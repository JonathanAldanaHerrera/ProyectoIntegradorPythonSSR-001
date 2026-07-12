📐 FASE 3 · Geometría y layouts (sintetiza L3) — 4h
Contexto: Una ventana que se rompe al redimensionar delata a un aficionado. Aquí maquetas de verdad.

Actividades detalladas:

1. **Refactor a layout managers:** reemplaza cualquier posición absoluta por grid/pack (Tkinter) o QVBoxLayout/QGridLayout (PyQt).

2. **Diseño responsivo:** al agrandar la ventana, la tabla crece y el formulario lateral mantiene su ancho; al encoger, nada se superpone.

3. **Jerarquía visual:** agrupa controles relacionados en frames/contenedores con espaciados consistentes (múltiplos de 4px).

4. **Prueba de estrés de layout:** capturas de la ventana en 3 tamaños (pequeña, media, maximizada) demostrando que no se rompe.

5. **Entregable de la fase:** ventana totalmente maquetada con layout managers; docs/02-layouts.md con las 3 capturas de redimensionamiento y explicación de la estrategia de geometría.

**Bonus +40 XP:** Layout que se reorganiza (formulario pasa de lateral a superior) por debajo de cierto ancho, estilo responsive de escritorio.