#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== LogiTrack Build ==="
echo "Proyecto: $PROJECT_DIR"

if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv .venv
fi

echo "Activando entorno virtual..."
source .venv/bin/activate

echo "Instalando dependencias..."
pip install -r requirements.txt
pip install pyinstaller

echo "Generando ejecutable..."
pyinstaller scripts/build.spec --distpath dist --workpath build --clean -y

echo ""
echo "=== Build completado ==="
echo "Ejecutable en: dist/LogiTrack/"

if [ "$(uname)" = "Darwin" ]; then
    echo "App bundle en: dist/LogiTrack.app/"
fi
