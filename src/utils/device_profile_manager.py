# src/utils/device_profile_manager.py 

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

DEFAULT_DEVICES_PATH = os.path.join("config", "devices.json")


@dataclass(frozen=True)
class DeviceProfile:
    device_id: str
    name: str
    match: Dict[str, Any]
    ui_keys: List[str]
    ui_encoders: List[str]


def load_devices_config(path: str = DEFAULT_DEVICES_PATH) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing devices config: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_default_device_profile(path: str = DEFAULT_DEVICES_PATH) -> DeviceProfile:
    cfg = load_devices_config(path)
    default_id = cfg.get("default_device_id")
    devices = cfg.get("devices", [])
    for d in devices:
        if d.get("device_id") == default_id:
            return _to_profile(d)
    raise ValueError(f"default_device_id '{default_id}' not found in {path}")


def match_device_profile(
    hello_type: str,
    path: str = DEFAULT_DEVICES_PATH
) -> Optional[DeviceProfile]:
    cfg = load_devices_config(path)
    for d in cfg.get("devices", []):
        match = d.get("match", {})
        if match.get("type") == hello_type:
            return _to_profile(d)
    return None


def _to_profile(d: Dict[str, Any]) -> DeviceProfile:
    ui = d.get("ui", {})
    return DeviceProfile(
        device_id=str(d.get("device_id")),
        name=str(d.get("name")),
        match=dict(d.get("match", {})),
        ui_keys=list(ui.get("keys", [])),
        ui_encoders=list(ui.get("encoders", [])),
    )
