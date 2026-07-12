from logitrack.app import App
from logitrack.logger import configurar_logging, get_logger


def main() -> None:
    configurar_logging()
    log = get_logger("app")
    log.info("=== LogiTrack iniciando ===")
    app = App()
    log.info("=== LogiTrack cerrando ===")
    app.run()


if __name__ == "__main__":
    main()
