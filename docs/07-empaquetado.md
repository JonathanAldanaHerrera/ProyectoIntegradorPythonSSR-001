# Fase 8 — Empaquetado y distribución

## Entorno reproducible

El proyecto usa un `requirements.txt` con versiones fijadas (`pip freeze`):

```
certifi==2026.6.17
charset-normalizer==3.4.9
idna==3.18
iniconfig==2.3.0
packaging==26.2
pluggy==1.6.0
Pygments==2.20.0
pytest==9.1.1
requests==2.34.2
urllib3==2.7.0
```

### Setup en macOS / Linux

```bash
git clone https://github.com/JonathanAldanaHerrera/ProyectoIntegradorPythonSSR-001.git
cd ProyectoIntegradorPythonSSR-001
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m logitrack
```

### Setup en Windows

```powershell
git clone https://github.com/JonathanAldanaHerrera/ProyectoIntegradorPythonSSR-001.git
cd ProyectoIntegradorPythonSSR-001
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m logitrack
```

## Empaquetado con PyInstaller

### Build en macOS / Linux

```bash
chmod +x scripts/build.sh
./scripts/build.sh
```

Esto genera:
- `dist/LogiTrack/LogiTrack` — ejecutable de terminal
- `dist/LogiTrack.app/` — app bundle nativa de macOS (doble clic para abrir)

Para ejecutar desde terminal:

```bash
./dist/LogiTrack/LogiTrack
```

Para abrir como app nativa:

```bash
open dist/LogiTrack.app
```

O simplemente hacer doble clic sobre `LogiTrack.app` en Finder.

### Build en Windows

```powershell
scripts\build.bat
```

Esto genera:
- `dist\LogiTrack\LogiTrack.exe` — ejecutable

Para ejecutar:

```powershell
dist\LogiTrack\LogiTrack.exe
```

O hacer doble clic sobre `LogiTrack.exe` en el Explorador de archivos.

### Build manual (cualquier SO)

```bash
pip install pyinstaller
pyinstaller scripts/build.spec --distpath dist --workpath build --clean -y
```

### Configuración del spec

- **Modo**: `onedir` (carpeta) — más confiable que `--onefile` para apps con SQLite, ya que SQLite necesita escribir archivos WAL junto a la DB
- **Windowed**: `console=False` — no muestra consola al abrir
- **macOS**: genera un `.app` bundle con `BUNDLE()` y `Info.plist`
- **Exclusiones**: `matplotlib`, `numpy`, `pandas`, `scipy`, `PIL` — no son dependencias pero PyInstaller a veces las detecta por importaciones transitivas

## Estructura del ejecutable generado

### macOS

```
dist/LogiTrack.app/
└── Contents/
    ├── Info.plist
    ├── MacOS/
    │   └── LogiTrack          ← ejecutable
    └── Frameworks/            ← librerías empaquetadas

dist/LogiTrack/
├── LogiTrack                  ← ejecutable standalone
├── logitrack.db               ← se crea al primer uso
├── logitrack.log              ← se crea al primer uso
└── _internal/                 ← runtime de Python + dependencias
```

### Windows

```
dist\LogiTrack\
├── LogiTrack.exe              ← ejecutable (doble clic)
├── logitrack.db               ← se crea al primer uso
├── logitrack.log              ← se crea al primer uso
└── _internal\                 ← runtime de Python + dependencias
```

## Instalación del ejecutable por SO

### macOS

1. Copiar la carpeta `dist/LogiTrack.app` a `/Applications/` (o cualquier ubicación)
2. Doble clic para abrir
3. Si aparece "No se puede abrir porque es de un desarrollador no identificado":
   - Ir a **Preferencias del Sistema → Privacidad y Seguridad**
   - Click en **Abrir de todas formas**
   - O ejecutar: `xattr -d com.apple.quarantine dist/LogiTrack.app`

### Windows

1. Copiar la carpeta `dist\LogiTrack\` completa a la ubicación deseada (ej. `C:\Program Files\LogiTrack\`)
2. Doble clic en `LogiTrack.exe` para abrir
3. Si Windows Defender bloquea el ejecutable:
   - Click en **Más información → Ejecutar de todas formas**
   - O agregar excepción en la configuración de Windows Defender

## Problemas encontrados y soluciones

### 1. Rutas de recursos en modo frozen

**Problema**: PyInstaller cambia el directorio de trabajo. Las rutas relativas como `"logitrack.db"` apuntan a una ubicación incorrecta.

**Solución**: Se creó `logitrack/paths.py` con un helper que detecta `sys.frozen`:

```python
def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent  # junto al .exe/.app
    return Path(__file__).resolve().parent.parent  # raíz del proyecto
```

Todos los módulos que necesitan rutas de archivos (`logger.py`, `app.py`) usan `get_db_path()` y `get_log_path()`.

### 2. SQLite WAL y onefile

**Problema**: Si se empaqueta con `--onefile`, PyInstaller extrae todo a un directorio temporal en cada ejecución. Los archivos WAL de SQLite se pierden.

**Solución**: Se usa `--onedir` en vez de `--onefile`. La DB se crea junto al ejecutable y persiste entre ejecuciones.

### 3. Tamaño del binario

**Problema**: El ejecutable inicial pesa ~80-100 MB porque incluye todo el runtime de Python + tkinter.

**Solución**: Se excluyen librerías no utilizadas en el spec (`matplotlib`, `numpy`, etc.) y se habilita UPX para compresión. El resultado está en el rango de ~40-60 MB.

### 4. Antivirus (Windows)

**Problema**: Algunos antivirus (especialmente Windows Defender) pueden marcar ejecutables de PyInstaller como falsos positivos.

**Solución**: El usuario debe agregar una excepción en Windows Defender:
1. Abrir **Seguridad de Windows → Protección contra virus y amenazas**
2. **Configuración → Exclusiones → Agregar exclusión**
3. Seleccionar la carpeta `LogiTrack\`

## Archivos nuevos y modificados

| Archivo | Cambio |
|---------|--------|
| `logitrack/paths.py` | **Nuevo** — helper de rutas frozen/desarrollo |
| `logitrack/logger.py` | Usa `get_log_path()` en vez de ruta hardcodeada |
| `logitrack/app.py` | Usa `get_db_path()` al instanciar SQLiteRepository |
| `scripts/build.spec` | **Nuevo** — configuración PyInstaller |
| `scripts/build.sh` | **Nuevo** — script de build macOS/Linux |
| `scripts/build.bat` | **Nuevo** — script de build Windows |
| `.gitignore` | +dist/, build/, *.db, .DS_Store |
| `README.md` | Documentación completa del proyecto |

