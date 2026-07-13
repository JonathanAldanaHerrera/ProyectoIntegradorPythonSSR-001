#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== LogiTrack Setup ==="
echo "Proyecto: $PROJECT_DIR"

if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv .venv
fi

echo "Activando entorno virtual..."
source .venv/bin/activate

echo "Instalando dependencias de producción..."
pip install --upgrade pip -q
pip install -r requirements.txt

echo "Instalando dependencias de desarrollo..."
pip install -r requirements-dev.txt

echo ""
echo "=== Setup completado ==="
echo "Activar entorno: source .venv/bin/activate"
echo "Ejecutar app:    python -m logitrack"
echo "Ejecutar tests:  python -m pytest tests/ -v"
echo "Generar build:   ./scripts/build.sh"
