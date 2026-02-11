# src/device/port_finder.py
from __future__ import annotations
import json
import time
from typing import Optional

import serial
from serial.tools import list_ports


def find_pico_data_port(
    timeout_s: float = 7.0,
    expected_type: str = "pico-macropad-backend",
) -> Optional[str]:
    ports = [p.device for p in list_ports.comports()]

    for port in ports:
        try:
            with serial.Serial(port, 115200, timeout=0.2) as ser:
                deadline = time.monotonic() + timeout_s

                while time.monotonic() < deadline:
                    raw = ser.readline()
                    if not raw:
                        continue

                    try:
                        msg = json.loads(raw.decode("utf-8").strip())
                    except Exception:
                        continue

                    t = msg.get("t")

                    # Best-case: hello tells us the type
                    if t == "hello":
                        if expected_type and msg.get("type") != expected_type:
                            break
                        return port

                    # Fallback: heartbeat proves this port is streaming our protocol
                    if t == "hb":
                        # If we want to be extra strict later, we can require
                        # that a hello appears eventually after hb. For now:
                        return port

        except Exception:
            continue

    return None

