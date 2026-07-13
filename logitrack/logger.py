import logging
import pathlib
import sys

from logitrack.paths import get_log_path


def configurar_logging(
    nivel: int = logging.DEBUG, archivo: pathlib.Path | None = None
) -> None:
    fmt = logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(name)-30s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    consola = logging.StreamHandler(sys.stdout)
    consola.setLevel(nivel)
    consola.setFormatter(fmt)

    ruta = archivo or get_log_path()
    fichero = logging.FileHandler(ruta, encoding="utf-8")
    fichero.setLevel(logging.DEBUG)
    fichero.setFormatter(fmt)

    raiz = logging.getLogger("logitrack")
    raiz.setLevel(logging.DEBUG)
    raiz.handlers.clear()
    raiz.addHandler(consola)
    raiz.addHandler(fichero)
    raiz.propagate = False


def get_logger(nombre: str) -> logging.Logger:
    return logging.getLogger(f"logitrack.{nombre}")
