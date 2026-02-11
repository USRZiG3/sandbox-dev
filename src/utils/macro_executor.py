# src/utils/macro_executor.py
from __future__ import annotations

from typing import Dict, List, Optional

from pynput.keyboard import Controller, Key
from pynput.mouse import Controller as MouseController

from src.utils.logger import setup_logger
from src.data.macro_library import MACRO_LIBRARY

_mouse = MouseController()

logger = setup_logger(__name__)
_keyboard = Controller()


# ---- Build a fast lookup table: macro_id -> keys sequence ----
def _build_macro_index() -> Dict[str, dict]:
    index: Dict[str, dict] = {}
    for _, macros in MACRO_LIBRARY.items():
        for m in macros:
            mid = str(m.get("id", "")).strip()
            if mid:
                index[mid] = m
    return index



_MACRO_INDEX = _build_macro_index()


# ---- Map friendly strings to pynput Key objects ----
_SPECIAL_KEYS = {
    "CTRL": Key.ctrl,
    "CONTROL": Key.ctrl,
    "SHIFT": Key.shift,
    "ALT": Key.alt,
    "WIN": Key.cmd,       # Windows key
    "CMD": Key.cmd,

    "ENTER": Key.enter,
    "RETURN": Key.enter,
    "TAB": Key.tab,
    "ESC": Key.esc,
    "ESCAPE": Key.esc,
    "SPACE": Key.space,
    "BACKSPACE": Key.backspace,
    "DELETE": Key.delete,
    "DEL": Key.delete,

    "HOME": Key.home,
    "END": Key.end,
    "PGUP": Key.page_up,
    "PAGEUP": Key.page_up,
    "PGDN": Key.page_down,
    "PAGEDOWN": Key.page_down,

    "LEFT": Key.left,
    "RIGHT": Key.right,
    "UP": Key.up,
    "DOWN": Key.down,

    "PRTSCN": Key.print_screen,
    "PRTSCR": Key.print_screen,
    "PRINTSCREEN": Key.print_screen,


    "VOLUME_UP": Key.media_volume_up,
    "VOLUME_DOWN": Key.media_volume_down,
    "VOLUME_MUTE": Key.media_volume_mute,
    "PLAY_PAUSE": Key.media_play_pause,
    "NEXT_TRACK": Key.media_next,
    "PREV_TRACK": Key.media_previous,

}


def _to_key(token: str):
    """
    Convert a key token like 'Ctrl' or 'C' or 'PrtScn' to a pynput key.
    Returns either a Key (special) or a single character string.
    """
    t = token.strip()
    if not t:
        return None

    upper = t.upper()

    # Function keys F1..F12 support
    if upper.startswith("F") and upper[1:].isdigit():
        n = int(upper[1:])
        if 1 <= n <= 24 and hasattr(Key, f"f{n}"):
            return getattr(Key, f"f{n}")

    if upper in _SPECIAL_KEYS:
        return _SPECIAL_KEYS[upper]

    # Single character keys (letters, numbers, punctuation)
    if len(t) == 1:
        return t.lower()

    # If someone used "Ctrl" etc with odd casing/spaces, try again:
    if upper.replace(" ", "") in _SPECIAL_KEYS:
        return _SPECIAL_KEYS[upper.replace(" ", "")]

    logger.warning(f"Unrecognized key token: {token!r}")
    return None


def execute_macro_by_id(macro_id: str) -> None:
    """
    Execute a macro by its ID (e.g., 'macro_copy').

    Supports:
      - Hotkey (default):
          {"type":"hotkey", "keys":["Ctrl","C"]}
      - Media:
          {"type":"media", "key":"VOLUME_UP"}
      - Mouse scroll:
          {"type":"mouse_scroll", "dy": 1}   # dy positive=up, negative=down
    """
    macro_id = (macro_id or "").strip()
    if not macro_id:
        return

    macro = _MACRO_INDEX.get(macro_id)
    if not macro:
        logger.warning(f"Macro id not found: {macro_id}")
        return

    # Backward-compat:
    # If old index still stores a list (seq), treat as hotkey keys.
    if isinstance(macro, list):
        macro = {"type": "hotkey", "keys": macro}

    mtype = str(macro.get("type", "hotkey")).strip().lower()

    try:
        # -------------------------
        # Mouse scroll
        # -------------------------
        if mtype == "mouse_scroll":
            dy = int(macro.get("dy", 0))
            if dy == 0:
                return
            _mouse.scroll(0, dy)
            logger.info(f"Executed macro: {macro_id} -> mouse_scroll dy={dy}")
            return

        # -------------------------
        # Media key (single special key)
        # -------------------------
        if mtype == "media":
            token = str(macro.get("key", "")).strip()
            if not token:
                logger.warning(f"Macro '{macro_id}' missing media key token.")
                return

            k = _to_key(token)
            if k is None:
                logger.warning(f"Macro '{macro_id}' has invalid media key: {token!r}")
                return

            _keyboard.press(k)
            _keyboard.release(k)
            logger.info(f"Executed macro: {macro_id} -> media {token}")
            return

        # -------------------------
        # Hotkey / default
        # -------------------------
        seq = macro.get("keys", [])
        if not isinstance(seq, list) or not seq:
            logger.warning(f"Macro '{macro_id}' has invalid or empty keys: {seq!r}")
            return

        # Convert tokens to pynput objects
        keys = [_to_key(t) for t in seq]
        keys = [k for k in keys if k is not None]
        if not keys:
            logger.warning(f"Macro '{macro_id}' has no valid keys: {seq}")
            return

        modifiers = {Key.ctrl, Key.shift, Key.alt, Key.cmd}
        held = []

        # Press and hold modifiers first, in sequence
        for k in keys[:-1]:
            if k in modifiers:
                _keyboard.press(k)
                held.append(k)
            else:
                _keyboard.press(k)
                _keyboard.release(k)

        # Tap the final key
        final = keys[-1]
        _keyboard.press(final)
        _keyboard.release(final)

        logger.info(f"Executed macro: {macro_id} -> {seq}")

    except Exception as e:
        logger.exception(f"Macro execution failed for {macro_id}: {e}")

    finally:
        # Release modifiers in reverse order
        try:
            if mtype == "hotkey":
                for k in reversed(locals().get("held", [])):
                    try:
                        _keyboard.release(k)
                    except Exception:
                        pass
        except Exception:
            pass
