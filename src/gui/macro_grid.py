"""
macro_grid.py
--------------
MNAV Macropad Configurator - Macro Grid Component
Theme-integrated, safe drag-and-drop macro assignment.
"""

from PyQt6.QtWidgets import QGridLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDragLeaveEvent

from src.utils.logger import setup_logger
from src.gui.styles import build_frame_styles

logger = setup_logger(__name__)


# ============================================================
# MacroGrid (Theme-Aware Grid Container)
# ============================================================
class MacroGrid(QFrame):
    """A 12-key grid for macro assignment with full theme support."""

    button_selected = pyqtSignal(int)  # NEW: emitted when a key is clicked


    def __init__(self, key_names=None, encoders=None):
        super().__init__()
        self.theme = None
        self.setObjectName("MacroGrid")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self.key_buttons = {}
        self.encoder_tiles = {}  # NEW: id -> EncoderTile

        if key_names is None:
            key_names = [f"K{i}" for i in range(1, 13)]

        if encoders is None:
            encoders = []  # like ["E0"]

        self._build_grid(key_names, encoders)


    # --------------------------------------------------------
    # Build 3x4 Grid
    # --------------------------------------------------------
    def _build_grid(self, key_names, encoders):
        layout = QGridLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        cols = 4
        key_height = 60  # matches MacroButton fixed height

        # --- keys ---
        for idx, key_name in enumerate(key_names):
            try:
                key_id = int(str(key_name).replace("K", ""))
            except Exception:
                key_id = idx + 1

            r = idx // cols
            c = idx % cols

            button = MacroButton(key_name, key_id)
            button.selected.connect(self.button_selected)
            self.key_buttons[key_id] = button
            layout.addWidget(button, r, c)

        # --- encoder tiles (place after keys) ---
        start = len(key_names)
        for e_idx, enc_name in enumerate(encoders):
            # enc_name like "E0"
            try:
                enc_id = int(str(enc_name).replace("E", ""))
            except Exception:
                enc_id = e_idx

            r = (start + e_idx) // cols
            c = (start + e_idx) % cols

            tile = EncoderTile(enc_name, key_height)
            self.encoder_tiles[enc_id] = tile
            layout.addWidget(tile, r, c)



    # --------------------------------------------------------
    # Theme Application
    # --------------------------------------------------------
    def apply_theme(self, theme):
        """Apply theme to the grid container and its buttons."""
        self.theme = theme

        # Frame styling
        self.setStyleSheet(build_frame_styles(theme))

        for btn in self.key_buttons.values():
            btn.apply_theme(theme)
        for tile in self.encoder_tiles.values():
            tile.apply_theme(theme)


    # --------------------------------------------------------
    # Grid Reset for New Profiles
    # --------------------------------------------------------
    def reset_grid(self):
        for key_id, button in self.key_buttons.items():
            button.setProperty("macro_id", "")
            button.setText(f"K{key_id}")
            button.setChecked(False)
            if self.theme:
                button.apply_theme(self.theme)


    # --------------------------------------------------------
    # Persistence Helpers
    # --------------------------------------------------------
    def get_macro_assignments(self):
        assignments = {}
        for key_id, button in self.key_buttons.items():
            macro_id = button.property("macro_id") or ""
            # If macro_id exists, store it; else store label for backward compatibility
            if macro_id:
                assignments[f"K{key_id}"] = macro_id
            else:
                label = button.text().strip()
                assignments[f"K{key_id}"] = label if label else ""
        return assignments


    def load_macro_assignments(self, assignments):
        if not assignments:
            self.reset_grid()
            return

        for key_name, value in assignments.items():
            try:
                key_id = int(key_name.replace("K", ""))
                if key_id not in self.key_buttons:
                    continue

                btn = self.key_buttons[key_id]
                value = str(value).strip()

                # If it's an id-like value, store it and render a nice label
                if value and "_" in value:
                    btn.setProperty("macro_id", value)
                    btn.setText(value.split("_")[-1].capitalize())
                else:
                    # Backward compatible: label-only assignments
                    btn.setProperty("macro_id", "")
                    btn.setText(value if value else f"K{key_id}")

            except Exception:
                pass

    def pulse_encoder(self, enc_id: int = 0, ms: int = 80):
        tile = self.encoder_tiles.get(enc_id)
        if tile:
            tile.pulse(ms=ms)





# ============================================================
# MacroButton — Theme-Aware Drag-and-Drop Button
# ============================================================
class MacroButton(QPushButton):
    """Represents a macro key capable of receiving drag-and-drop macro IDs."""

    selected = pyqtSignal(int)  # NEW: emit when clicked
    RADIUS = 6  # Unified UI radius

    def __init__(self, label, key_id):
        super().__init__(label)
        self.key_id = key_id
        self.theme = None

        self.setFixedSize(100, 60)
        self.setAcceptDrops(True)
        self.setCheckable(True)
        self.setProperty("macro_id", "")

    # --------------------------------------------------------
    # Click Event — Select the Button
    # --------------------------------------------------------
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.selected.emit(self.key_id)

    # --------------------------------------------------------
    # Theme Application
    # --------------------------------------------------------
    def apply_theme(self, theme):
        self.theme = theme
        self._apply_default_style()

    # --------------------------------------------------------
    # Style Builders
    # --------------------------------------------------------
    def _apply_default_style(self):
        t = self.theme
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['mantle']};
                color: {t['text']};
                border: 1px solid {t['overlay']};
                border-radius: {self.RADIUS}px;
            }}
            QPushButton:checked {{
                background-color: {t['blue']};
                color: {t['crust']};
            }}
            QPushButton:hover {{
                border-color: {t['green']};
            }}
        """)

    def _apply_drop_hover_style(self):
        t = self.theme
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {t['mantle']};
                color: {t['text']};
                border: 2px solid {t['accent']};
                border-radius: {self.RADIUS}px;
            }}
        """)

    def _apply_error_style(self):
        """Temporary red border when rejecting an invalid drop."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme['mantle']};
                color: {self.theme['text']};
                border: 2px solid #f38ba8;
                border-radius: {self.RADIUS}px;
            }}
        """)
        QTimer.singleShot(200, self._apply_default_style)

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------
    def _is_valid_macro(self, macro_id: str):
        return isinstance(macro_id, str) and "_" in macro_id

    # --------------------------------------------------------
    # Drag Events (Theme-Aware)
    # --------------------------------------------------------
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasFormat("application/x-mnav-macro"):
            macro_id = event.mimeData().data("application/x-mnav-macro").data().decode("utf-8")
            if self._is_valid_macro(macro_id):
                self._apply_drop_hover_style()
                event.acceptProposedAction()
                return
        event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        event.accept()
        self._apply_default_style()

    def dropEvent(self, event: QDropEvent):
        try:
            if not event.mimeData().hasFormat("application/x-mnav-macro"):
                self._apply_error_style()
                event.ignore()
                return

            macro_id = event.mimeData().data("application/x-mnav-macro").data().decode("utf-8")
            if not self._is_valid_macro(macro_id):
                self._apply_error_style()
                event.ignore()
                return

            macro_label = macro_id.split("_")[-1].capitalize()
            self.setProperty("macro_id", macro_id)   # <-- keep the real ID
            self.setText(macro_label)


            logger.info(f"Macro '{macro_id}' assigned to {macro_label}")
            event.acceptProposedAction()

        except Exception as e:
            logger.error(f"Drop failed: {e}")
            event.ignore()

        finally:
            self._apply_default_style()
class EncoderTile(QPushButton):
    """
    Non-interactive encoder indicator tile.
    Inverted colors vs normal keys:
      - Resting: active color (blue) background
      - Active: resting color (mantle) background
    """
    def __init__(self, label: str, key_height: int):
        super().__init__(label)
        self.theme = None
        self._active = False

        # circle: radius = y/2 where y is key height
        diameter = int(key_height)
        radius = diameter // 2

        self.setFixedSize(diameter, diameter)
        self.setEnabled(False)  # non-interactive
        self.setCheckable(False)

        self._radius = radius

    def apply_theme(self, theme):
        self.theme = theme
        self._apply_style()

    def set_active(self, active: bool):
        self._active = bool(active)
        self._apply_style()

    def pulse(self, ms: int = 80):
        """Briefly invert to show activity."""
        self.set_active(True)
        QTimer.singleShot(ms, lambda: self.set_active(False))

    def _apply_style(self):
        if not self.theme:
            return

        t = self.theme
        r = self._radius

        # Inverted scheme:
        # Resting = key active color
        # Active  = key resting color
        if not self._active:
            bg = t["blue"]
            fg = t["crust"]
            border = t["overlay"]
        else:
            bg = t["mantle"]
            fg = t["text"]
            border = t["green"]

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                border-radius: {r}px;
                font-weight: 700;
            }}
        """)









