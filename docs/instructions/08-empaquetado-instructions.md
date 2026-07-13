📦 FASE 8 · Empaquetado y distribución (sintetiza L8) — 5h
Contexto: Una app que solo corre en tu máquina con python app.py no sirve al despachador. Debe instalarse con doble clic.

Actividades detalladas:

1. **Entorno reproducible:** venv limpio + requirements.txt fijado con versiones exactas (pip freeze). El reviewer clona y corre en <2 minutos.

2. **Empaquetado con PyInstaller:** genera un ejecutable (--onefile o carpeta) que incluya recursos (icono, tema, base SQLite semilla). Resuelve rutas de recursos para que funcionen dentro del binario.

3. **Prueba en máquina limpia:** ejecuta el binario en un entorno sin Python instalado (o VM) y verifica que abre y funciona.

4. **Publicación:** sube el ejecutable/instalador a un GitHub Release v1.0.0 con notas e instrucciones de instalación por sistema operativo.

5. **Entregable de la fase:** binario empaquetado adjunto en el GitHub Release, docs/07-empaquetado.md con el comando de build, los problemas encontrados (rutas de recursos, antivirus, tamaño) y cómo se resolvieron.

Bonus +60 XP: Instalador nativo real (Inno Setup en Windows, .dmg en macOS o .deb/AppImage en Linux) en vez de un ejecutable suelto.