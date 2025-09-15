import threading
import time

class CleanupWorker:
    """
    Executa uma função de limpeza periodicamente em uma thread.
    """
    def __init__(self, cleanup_func, interval=0.5):
        self.cleanup_func = cleanup_func
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread = None

    def _run(self):
        while not self._stop_event.is_set():
            try:
                self.cleanup_func()
            except Exception as e:
                print(f"⚠️ Erro no CleanupWorker: {e}")
            self._stop_event.wait(self.interval)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self, join=True):
        self._stop_event.set()
        if join and self._thread:
            self._thread.join()