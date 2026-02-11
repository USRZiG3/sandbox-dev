# src/device/device_scanner.py
from __future__ import annotations
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from src.device.port_finder import find_pico_data_port


class _ScanWorker(QObject):
    found = pyqtSignal(str)
    not_found = pyqtSignal()
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, timeout_s: float):
        super().__init__()
        self.timeout_s = timeout_s

    def run(self):
        try:
            port = find_pico_data_port(timeout_s=self.timeout_s)
            if port:
                self.found.emit(port)
            else:
                self.not_found.emit()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class DeviceScanner(QObject):
    found = pyqtSignal(str)
    not_found = pyqtSignal()
    error = pyqtSignal(str)
    scanning = pyqtSignal(bool)

    def __init__(self, timeout_s: float = 1.0):
        super().__init__()
        self.timeout_s = timeout_s
        self._busy = False
        self._thread: QThread | None = None
        self._worker: _ScanWorker | None = None

    def is_busy(self) -> bool:
        return self._busy

    def scan(self):
        if self._busy:
            return

        self._busy = True
        self.scanning.emit(True)

        self._thread = QThread()
        self._worker = _ScanWorker(timeout_s=self.timeout_s)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)

        self._worker.found.connect(self.found)
        self._worker.not_found.connect(self.not_found)
        self._worker.error.connect(self.error)

        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._cleanup)

        self._thread.start()

    def _cleanup(self):
        self._busy = False
        self.scanning.emit(False)

        if self._worker:
            self._worker.deleteLater()
        if self._thread:
            self._thread.deleteLater()

        self._worker = None
        self._thread = None

    def shutdown(self):
        """
        Best-effort shutdown to avoid:
        'QThread: Destroyed while thread is still running'
        """
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(1500)

