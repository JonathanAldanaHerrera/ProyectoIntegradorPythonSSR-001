# Fase 1 — Fundamentos y elección de framework GUI

## 1. Panorama de frameworks — Matriz comparativa

| Criterio               | Tkinter                          | PyQt6                              | Kivy                                | Flet                                |
|------------------------|----------------------------------|------------------------------------|-------------------------------------|-------------------------------------|
| **Curva de aprendizaje** | Baja — incluido en stdlib, API simple y bien documentada. Ideal para principiantes. | Media-Alta — API extensa basada en Qt; requiere entender signals/slots y el ecosistema Qt. | Media — paradigma propio (lenguaje KV), diferente al desarrollo desktop clásico. | Baja — API declarativa inspirada en Flutter; abstracciones modernas y productivas. |
| **Licencia**           | PSF (Python Software Foundation) — libre sin restricciones. | GPL v3 / Comercial — la versión gratuita obliga a liberar el código bajo GPL. Licencia comercial de pago. | MIT — totalmente libre para uso comercial y privado. | Apache 2.0 — libre para uso comercial sin restricciones. |
| **Look nativo**        | Parcial — `ttk` ofrece widgets con aspecto nativo en Windows, macOS y Linux. Apariencia básica pero funcional. | Excelente — Qt renderiza widgets con look nativo del SO. Resultado profesional out of the box. | No nativo — motor gráfico propio (OpenGL). Los widgets no se parecen a los del SO. Orientado a móvil/táctil. | No nativo — renderiza con Flutter engine. Apariencia Material Design consistente pero ajena al SO. |
| **Empaquetado**        | Sencillo — PyInstaller o cx_Freeze generan ejecutables sin dependencias externas (Tkinter ya está en Python). | Complejo — PyInstaller funciona pero el binario es pesado (+100 MB) por las librerías Qt. | Complejo — requiere Buildozer para móvil; en desktop, PyInstaller funciona pero con configuración extra. | En desarrollo — `flet pack` empaqueta con Flutter, pero la herramienta aún está madurando. |
| **Comunidad**          | Muy amplia — décadas de existencia, abundante documentación, Stack Overflow y tutoriales. | Amplia — comunidad profesional activa, documentación oficial extensa, pero nicho más especializado. | Moderada — comunidad activa principalmente en desarrollo móvil con Python. | Creciente — proyecto joven (2022+), comunidad entusiasta pero aún pequeña. |

## 2. Decisión justificada — Tkinter

Para el caso de uso de **LogiTrack** —una aplicación de escritorio para mostrador de paquetería que operará en modo offline— la elección de **Tkinter** es la más adecuada por las siguientes razones:

**Cero dependencias externas.** Tkinter viene incluido en la biblioteca estándar de Python, lo que significa que cualquier máquina con Python instalado puede ejecutar la aplicación sin pasos de instalación adicionales. Esto es crítico para un entorno de mostrador donde la simplicidad del despliegue reduce el riesgo de errores de configuración y minimiza la necesidad de soporte técnico.

**Empaquetado liviano y confiable.** Al no depender de librerías externas pesadas como Qt o el motor de Flutter, el ejecutable generado con PyInstaller es significativamente más pequeño y el proceso de empaquetado más predecible. Para un negocio de paquetería que necesita instalar la herramienta en una o varias terminales de mostrador, un instalador ligero y rápido es una ventaja operativa real.

**Operación offline garantizada.** Tkinter no requiere conexión a internet para renderizar su interfaz ni descarga componentes en tiempo de ejecución. Toda la lógica visual se resuelve localmente, alineándose perfectamente con el requisito de funcionamiento offline-friendly del caso LogiTrack.

**Look nativo suficiente con `ttk`.** Aunque Tkinter no iguala la sofisticación visual de Qt, el módulo `ttk` (Themed Tk) proporciona widgets con apariencia nativa del sistema operativo que resultan familiares y funcionales para el usuario final en un contexto de punto de venta. La prioridad del proyecto es la usabilidad y la robustez, no la estética de una aplicación de consumo masivo.

**Curva de aprendizaje baja y alta productividad.** Para un proyecto académico con alcance definido y tiempo limitado, la simplicidad de la API de Tkinter permite avanzar rápidamente en la funcionalidad del negocio sin invertir semanas en aprender un framework más complejo. La abundante documentación y comunidad facilitan la resolución de problemas.

> **Nota:** Se descartó PyQt6 por las restricciones de la licencia GPL (requiere liberar el código fuente o adquirir licencia comercial), Kivy por su orientación a interfaces táctiles/móviles que no se alinea con un desktop de mostrador, y Flet por ser un proyecto todavía joven cuya herramienta de empaquetado aún está madurando.

## 3. Esqueleto de ventana — "Hola mundo" visual

El archivo `logitrack/__main__.py` contiene la ventana raíz mínima:

```python
import tkinter as tk


def main() -> None:
    root = tk.Tk()
    root.title("LogiTrack Desktop")
    root.geometry("800x600")
    root.mainloop()


if __name__ == "__main__":
    main()
```

### Ejecución

```bash
python -m logitrack
```

Esto abre una ventana vacía de 800×600 píxeles con el título **"LogiTrack Desktop"** que se cierra limpiamente al presionar el botón de cerrar (×). No requiere dependencias externas.

## 4. Estructura del repositorio inicial

```
ProyectoIntegradorPythonSSR-001/
├── docs/
│   ├── 00-fundamentos.md          ← este documento
│   └── 00-fundamentos-instructions.md
├── logitrack/
│   ├── __init__.py                ← marca el paquete Python
│   └── __main__.py                ← ventana raíz (punto de entrada)
├── tests/                         ← pruebas unitarias (futuras fases)
├── .gitignore
├── README.md
└── requirements.txt               ← vacío por ahora (sin dependencias externas)
```
