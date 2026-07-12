import threading
import tkinter as tk
from typing import Any, Callable


class TaskWorker:

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._thread: threading.Thread | None = None
        self._cancel_event = threading.Event()

    @property
    def esta_corriendo(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def cancel_event(self) -> threading.Event:
        return self._cancel_event

    def ejecutar(
        self,
        tarea: Callable[[threading.Event], Any],
        on_completado: Callable[[Any], None],
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        if self.esta_corriendo:
            return

        self._cancel_event.clear()

        def _wrapper() -> None:
            try:
                resultado = tarea(self._cancel_event)
                if not self._cancel_event.is_set():
                    self._root.after(0, on_completado, resultado)
                else:
                    self._root.after(0, on_completado, None)
            except Exception as e:
                if on_error:
                    self._root.after(0, on_error, e)

        self._thread = threading.Thread(target=_wrapper, daemon=True)
        self._thread.start()

    def cancelar(self) -> None:
        self._cancel_event.set()
