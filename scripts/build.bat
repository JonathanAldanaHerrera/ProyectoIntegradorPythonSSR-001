@echo off
setlocal

set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..

cd /d "%PROJECT_DIR%"

echo === LogiTrack Build ===
echo Proyecto: %PROJECT_DIR%

if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
)

echo Activando entorno virtual...
call .venv\Scripts\activate.bat

echo Instalando dependencias...
pip install -r requirements.txt
pip install pyinstaller

echo Generando ejecutable...
pyinstaller scripts\build.spec --distpath dist --workpath build --clean -y

echo.
echo === Build completado ===
echo Ejecutable en: dist\LogiTrack\

endlocal
