"""
Verifica que las reglas de dependencia entre capas se respeten.

Reglas:
  - views/    no importa models/
  - services/ no importa views/
  - services/ no importa controllers/
"""
import ast
import pathlib

BASE = pathlib.Path(__file__).parent.parent.parent / "logitrack"


def _modulos_importados(path: pathlib.Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modulos: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modulos.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modulos.append(alias.name)
    return modulos


def _archivos(capa: str) -> list[pathlib.Path]:
    return [p for p in (BASE / capa).rglob("*.py") if p.name != "__init__.py"]


def test_views_no_importan_models():
    for path in _archivos("views"):
        for modulo in _modulos_importados(path):
            assert "logitrack.models" not in modulo, (
                f"Violación: {path.name} importa '{modulo}'"
            )


def test_services_no_importan_views():
    for path in _archivos("services"):
        for modulo in _modulos_importados(path):
            assert "logitrack.views" not in modulo, (
                f"Violación: {path.name} importa '{modulo}'"
            )


def test_services_no_importan_controllers():
    for path in _archivos("services"):
        for modulo in _modulos_importados(path):
            assert "logitrack.controllers" not in modulo, (
                f"Violación: {path.name} importa '{modulo}'"
            )


def test_service_retorna_dicts_no_objetos_envio():
    """El servicio nunca expone objetos Envio fuera de la capa de servicios."""
    from logitrack.services.envio_service import EnvioService

    svc = EnvioService()
    svc.registrar("Juan", "Calle 1", "Paquete", "Pendiente")

    envios = svc.listar()
    assert envios, "La lista no debe estar vacía"
    assert isinstance(envios[0], dict), "listar() debe retornar dicts"

    filtrados = svc.filtrar("Pendiente", "")
    assert isinstance(filtrados[0], dict), "filtrar() debe retornar dicts"

    registrado = svc.registrar("Ana", "Av. 2", "Sobre", "En tránsito")
    assert isinstance(registrado, dict), "registrar() debe retornar dict"


def test_controller_no_importa_modelos():
    for path in _archivos("controllers"):
        for modulo in _modulos_importados(path):
            assert "logitrack.models" not in modulo, (
                f"Violación: {path.name} importa '{modulo}'"
            )
