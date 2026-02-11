"""
macro_library.py
"""

MACRO_LIBRARY = {
    "Editing": [
        {"id": "macro_copy", "name": "Copy", "type": "hotkey", "keys": ["Ctrl", "C"]},
        {"id": "macro_paste", "name": "Paste", "type": "hotkey", "keys": ["Ctrl", "V"]},
        {"id": "macro_cut", "name": "Cut", "type": "hotkey", "keys": ["Ctrl", "X"]},
        {"id": "macro_undo", "name": "Undo", "type": "hotkey", "keys": ["Ctrl", "Z"]},
        {"id": "macro_redo", "name": "Redo", "type": "hotkey", "keys": ["Ctrl", "Y"]},
        {"id": "macro_select_all", "name": "Select All", "type": "hotkey", "keys": ["Ctrl", "A"]},
        {"id": "macro_find", "name": "Find", "type": "hotkey", "keys": ["Ctrl", "F"]},
        {"id": "macro_save", "name": "Save", "type": "hotkey", "keys": ["Ctrl", "S"]},
    ],

    "Navigation": [
        {"id": "macro_home", "name": "Home", "type": "hotkey", "keys": ["Home"]},
        {"id": "macro_end", "name": "End", "type": "hotkey", "keys": ["End"]},
        {"id": "macro_page_up", "name": "Page Up", "type": "hotkey", "keys": ["PageUp"]},
        {"id": "macro_page_down", "name": "Page Down", "type": "hotkey", "keys": ["PageDown"]},
        {"id": "macro_back", "name": "Back", "type": "hotkey", "keys": ["Alt", "Left"]},
        {"id": "macro_forward", "name": "Forward", "type": "hotkey", "keys": ["Alt", "Right"]},

        # Real scrolling (mouse wheel)
        {"id": "macro_scroll_up", "name": "Scroll Up", "type": "mouse_scroll", "dy": 1},
        {"id": "macro_scroll_down", "name": "Scroll Down", "type": "mouse_scroll", "dy": -1},
    ],

    "System": [
        {"id": "macro_screenshot", "name": "Screenshot", "type": "hotkey", "keys": ["PrtScn"]},
        {"id": "macro_task_switch", "name": "Alt-Tab", "type": "hotkey", "keys": ["Alt", "Tab"]},
        {"id": "macro_close_window", "name": "Close Window", "type": "hotkey", "keys": ["Alt", "F4"]},

        # Media keys (best for encoder testing)
        {"id": "macro_vol_up", "name": "Volume Up", "type": "media", "key": "VOLUME_UP"},
        {"id": "macro_vol_down", "name": "Volume Down", "type": "media", "key": "VOLUME_DOWN"},
        {"id": "macro_mute", "name": "Mute", "type": "media", "key": "VOLUME_MUTE"},
        {"id": "macro_media_play_pause", "name": "Play/Pause", "type": "media", "key": "PLAY_PAUSE"},
        {"id": "macro_media_next", "name": "Next Track", "type": "media", "key": "NEXT_TRACK"},
        {"id": "macro_media_prev", "name": "Prev Track", "type": "media", "key": "PREV_TRACK"},
    ],
}

