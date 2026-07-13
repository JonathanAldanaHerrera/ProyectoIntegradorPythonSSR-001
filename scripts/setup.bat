@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..

cd /d "%PROJECT_DIR%"

echo === LogiTrack Setup ===
echo Proyecto: %PROJECT_DIR%

if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
)

echo Activando entorno virtual...
call .venv\Scripts\activate.bat

echo Instalando dependencias de produccion...
pip install --upgrade pip -q
pip install -r requirements.txt

echo Instalando dependencias de desarrollo...
pip install -r requirements-dev.txt

echo.
echo === Setup completado ===
echo Activar entorno: .venv\Scripts\activate
echo Ejecutar app:    python -m logitrack
echo Ejecutar tests:  python -m pytest tests\ -v
echo Generar build:   pyinstaller scripts\build.spec

endlocal
