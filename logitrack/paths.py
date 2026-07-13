import sys
from pathlib import Path


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def get_db_path() -> Path:
    return get_base_dir() / "logitrack.db"


def get_log_path() -> Path:
    return get_base_dir() / "logitrack.log"
