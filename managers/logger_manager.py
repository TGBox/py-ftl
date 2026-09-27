import os
from datetime import datetime
from typing import Optional


class DebugLogger:
    """Manages debug logging into timestamped text files."""

    _instance: Optional["DebugLogger"] = None

    def __init__(self, enabled: bool = False, logs_dir: str = "logs") -> None:
        self.enabled = enabled
        self.logs_dir = logs_dir
        self.current_log_path: Optional[str] = None
        self._file_handle = None

    @classmethod
    def get_instance(cls) -> "DebugLogger":
        if cls._instance is None:
            from settings import DEBUG_LOG_ENABLED
            cls._instance = DebugLogger(enabled=DEBUG_LOG_ENABLED)
        return cls._instance

    def _ensure_file(self) -> None:
        if self._file_handle and not self._file_handle.closed:
            return
        os.makedirs(self.logs_dir, exist_ok=True)
        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.current_log_path = os.path.join(self.logs_dir, f"game_log_{now_str}.txt")
        self._file_handle = open(self.current_log_path, "a", encoding="utf-8")
        self._file_handle.write(f"=== PY-FTL PROTOKOLL-LOG GESTARTET AM {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        self._file_handle.flush()

    def set_enabled(self, state: bool) -> None:
        if state == self.enabled:
            return
        if state:
            self.enabled = True
            self.log("SYSTEM", "Protokollmodus vom Benutzer AKTIVIERT.")
        else:
            self.log("SYSTEM", "Protokollmodus vom Benutzer DEAKTIVIERT.")
            self.enabled = False

    def log(self, category: str, message: str) -> None:
        if not self.enabled:
            return
        self._ensure_file()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self._file_handle and not self._file_handle.closed:
            self._file_handle.write(f"[{timestamp}] [{category.upper()}] {message}\n")
            self._file_handle.flush()

    def close(self) -> None:
        if self._file_handle and not self._file_handle.closed:
            try:
                self._file_handle.close()
            except Exception:
                pass

    def __del__(self) -> None:
        self.close()


def log_debug(category: str, message: str) -> None:
    DebugLogger.get_instance().log(category, message)
