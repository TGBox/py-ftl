import os
from datetime import datetime
from typing import Optional


class DebugLogger:
    """Manages protocol/debug logging of all game events and actions into timestamped .txt files."""

    _instance: Optional["DebugLogger"] = None

    def __init__(self, enabled: bool = False, logs_dir: str = "logs") -> None:
        self.enabled: bool = enabled
        self.logs_dir: str = logs_dir
        self.current_log_path: Optional[str] = None
        self._file_handle = None

        if self.enabled:
            self._ensure_log_file()

    @classmethod
    def get_instance(cls) -> "DebugLogger":
        if cls._instance is None:
            from settings import DEBUG_LOG_ENABLED
            cls._instance = DebugLogger(enabled=DEBUG_LOG_ENABLED)
        return cls._instance

    def _ensure_log_file(self) -> None:
        """Creates the logs directory and opens a new timestamped txt file if not already opened."""
        if self.current_log_path and self._file_handle and not self._file_handle.closed:
            return

        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir, exist_ok=True)

        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"game_log_{now_str}.txt"
        self.current_log_path = os.path.join(self.logs_dir, filename)

        try:
            self._file_handle = open(self.current_log_path, "a", encoding="utf-8")
            start_header = f"=== PY-FTL PROTOKOLL-LOG GESTARTET AM {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"
            self._file_handle.write(start_header)
            self._file_handle.flush()
        except Exception as e:
            print(f"Fehler beim Erstellen der Log-Datei {self.current_log_path}: {e}")

    def set_enabled(self, state: bool) -> None:
        """Toggles protocol logging ON or OFF."""
        if state == self.enabled:
            return
        if state:
            self.enabled = True
            self._ensure_log_file()
            self.log("SYSTEM", "Protokollmodus vom Benutzer AKTIVIERT.")
        else:
            self.log("SYSTEM", "Protokollmodus vom Benutzer DEAKTIVIERT.")
            self.enabled = False

    def log(self, category: str, message: str) -> None:
        """Logs a minutely detailed game event if protocol mode is enabled."""
        if not self.enabled:
            return

        if not self._file_handle or self._file_handle.closed:
            self._ensure_log_file()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{category.upper()}] {message}\n"

        try:
            if self._file_handle and not self._file_handle.closed:
                self._file_handle.write(log_entry)
                self._file_handle.flush()
        except Exception as e:
            print(f"Fehler beim Schreiben des Logs: {e}")

    def close(self) -> None:
        """Closes the open log file handle cleanly."""
        if self._file_handle and not self._file_handle.closed:
            try:
                self.log("SYSTEM", "Protokollmodus beendet (Spiel beendet).")
                self._file_handle.close()
            except Exception:
                pass


# Global singleton helper function
def log_debug(category: str, message: str) -> None:
    DebugLogger.get_instance().log(category, message)
