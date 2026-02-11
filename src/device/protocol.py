# src/device/protocol.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional


def is_hello(msg: Dict[str, Any]) -> bool:
    return msg.get("t") == "hello"


def is_hb(msg: Dict[str, Any]) -> bool:
    return msg.get("t") == "hb"


def is_key(msg: Dict[str, Any]) -> bool:
    return msg.get("t") == "key" and "k" in msg and "edge" in msg

def is_enc(msg: Dict[str, Any]) -> bool:
    return msg.get("t") == "enc" and "id" in msg and "d" in msg

def is_btn(msg: Dict[str, Any]) -> bool:
    return msg.get("t") == "btn" and "id" in msg and "edge" in msg



@dataclass(frozen=True)
class HelloInfo:
    type: str
    fw_version: str
    keys: int
    pins: list[str]

    @staticmethod
    def from_msg(msg: Dict[str, Any]) -> "HelloInfo":
        return HelloInfo(
            type=str(msg.get("type", "")),
            fw_version=str(msg.get("fw_version", "")),
            keys=int(msg.get("keys", 0)),
            pins=[str(p) for p in (msg.get("pins") or [])],
        )


@dataclass(frozen=True)
class KeyEvent:
    k: int
    edge: str  # "down" or "up"
    ts: Optional[float] = None

    @staticmethod
    def from_msg(msg: Dict[str, Any]) -> "KeyEvent":
        return KeyEvent(
            k=int(msg["k"]),
            edge=str(msg["edge"]),
            ts=(float(msg["ts"]) if "ts" in msg else None),
        )
    
@dataclass(frozen=True)
class EncoderEvent:
    id: int
    d: int
    pos: Optional[int] = None
    ts: Optional[float] = None

    @staticmethod
    def from_msg(msg: Dict[str, Any]) -> "EncoderEvent":
        return EncoderEvent(
            id=int(msg["id"]),
            d=int(msg["d"]),
            pos=(int(msg["pos"]) if "pos" in msg else None),
            ts=(float(msg["ts"]) if "ts" in msg else None),
        )

@dataclass(frozen=True)
class ButtonEvent:
    id: int
    edge: str  # "down" / "up"
    ts: Optional[float] = None

    @staticmethod
    def from_msg(msg: Dict[str, Any]) -> "ButtonEvent":
        return ButtonEvent(
            id=int(msg["id"]),
            edge=str(msg["edge"]),
            ts=(float(msg["ts"]) if "ts" in msg else None),
        )

