# src/device/pico_serial.py
from __future__ import annotations

import json
import threading
import time
from typing import Any, Dict, Optional

import serial
from PyQt6.QtCore import QObject, pyqtSignal

from .protocol import HelloInfo, KeyEvent, EncoderEvent, ButtonEvent, is_hello, is_hb, is_key, is_enc, is_btn


class PicoSerialClient(QObject):
    connected = pyqtSignal(str)        # port
    disconnected = pyqtSignal()
    hello = pyqtSignal(object)         # HelloInfo
    heartbeat = pyqtSignal(float)      # ts
    key_event = pyqtSignal(object)     # KeyEvent
    encoder_event = pyqtSignal(object)   # EncoderEvent
    button_event = pyqtSignal(object)    # ButtonEvent

    parse_error = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._ser: Optional[serial.Serial] = None
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self.key_state: list[bool] = []

    def start(self, port: str) -> None:
        self.stop()
        self._stop.clear()
        self._ser = serial.Serial(port, 115200, timeout=0.2)
        self.connected.emit(port)
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None
        if self._ser:
            try:
                self._ser.close()
            except Exception:
                pass
        self._ser = None
        self.disconnected.emit()

    def _reader_loop(self) -> None:
        assert self._ser is not None
        ser = self._ser

        while not self._stop.is_set():
            try:
                raw = ser.readline()
                if not raw:
                    continue

                try:
                    line = raw.decode("utf-8").strip()
                    msg: Dict[str, Any] = json.loads(line)
                except Exception as e:
                    self.parse_error.emit(f"{repr(raw)} | {e}")
                    continue

                if is_hello(msg):
                    info = HelloInfo.from_msg(msg)
                    self.key_state = [False] * max(0, info.keys)
                    self.hello.emit(info)

                elif is_hb(msg):
                    self.heartbeat.emit(float(msg.get("ts", time.monotonic())))

                elif is_key(msg):
                    ev = KeyEvent.from_msg(msg)
                    if 0 <= ev.k < len(self.key_state):
                        self.key_state[ev.k] = (ev.edge == "down")
                    self.key_event.emit(ev)

                elif is_enc(msg):
                    ev = EncoderEvent.from_msg(msg)
                    self.encoder_event.emit(ev)

                elif is_btn(msg):
                    ev = ButtonEvent.from_msg(msg)
                    self.button_event.emit(ev)


            except (serial.SerialException, OSError):
                break
            except Exception as e:
                self.parse_error.emit(str(e))

        self.disconnected.emit()
