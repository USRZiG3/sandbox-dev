"""
macro_palette.py
----------------
MNAV Macropad Configurator - Macro Palette Component
Displays categorized macro actions as draggable list items with rounded drag visuals.
Now updated for dynamic theme support via the theme engine.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QFrame, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QMimeData, QPoint, QTimer
from PyQt6.QtGui import QFont, QDrag, QPixmap, QPainter, QColor, QPainterPath

from src.data.macro_library import MACRO_LIBRARY
from src.utils.logger import setup_logger

from src.gui.styles import (
    build_list_styles,
    build_combo_styles,
    build_frame_styles,
    get_theme
)

logger = setup_logger(__name__)


# ============================================================
# Draggable Macro List — Now Theme-Aware
# ============================================================
class DraggableMacroList(QListWidget):
    """Custom QListWidget subclass with safe drag handling and dynamic theme preview."""

    def __init__(self):
        super().__init__()
        self.theme = get_theme("Mocha")  # default; updated by apply_theme()

        self.setSelectionMode(self.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(False)

    # --------------------------------------------------------
    # Apply Theme to List Widget
    # --------------------------------------------------------
    def apply_theme(self, theme):
        """Apply theme-derived styling."""
        self.theme = theme
        self.setStyleSheet(build_list_styles(theme))

    # --------------------------------------------------------
    # Drag Start
    # --------------------------------------------------------
    def startDrag(self, supported_actions):
        selected_items = self.selectedItems()
        if not selected_items:
            logger.warning("Drag start aborted: no item selected.")
            return
        
        item = selected_items[0]
        macro_name = item.text()
        macro_id = item.data(Qt.ItemDataRole.UserRole)

        if not macro_id or "_" not in macro_id:
            logger.warning(f"Drag aborted: invalid macro ID '{macro_id}'.")
            return

        # -------------------------
        # INTERNAL MIME PAYLOAD
        # -------------------------
        mime_data = QMimeData()
        mime_data.setData("application/x-mnav-macro", macro_id.encode("utf-8"))
        mime_data.setText("")  # Prevent external text drops

        # -------------------------
        # Dynamic Drag Preview
        # -------------------------
        theme = self.theme
        accent = theme["accent"]
        overlay = theme["overlay"]
        text_color = theme["crust"] if "crust" in theme else "#181926"

        font = QFont("Segoe UI", 10)
        metrics = self.fontMetrics()
        text_width = metrics.horizontalAdvance(macro_name)

        padding_x, padding_y = 14, 8
        pixmap_width = text_width + padding_x * 2
        pixmap_height = metrics.height() + padding_y * 2
        radius = 6

        pixmap = QPixmap(pixmap_width, pixmap_height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Rounded background
        path = QPainterPath()
        path.addRoundedRect(0, 0, pixmap_width, pixmap_height, radius, radius)

        painter.fillPath(path, QColor(accent))
        painter.setPen(QColor(overlay))
        painter.drawPath(path)

        # Text
        painter.setFont(font)
        painter.setPen(QColor(text_color))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, macro_name)
        painter.end()

        # -------------------------
        # Execute Drag
        # -------------------------
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap_width // 2, pixmap_height // 2))

        result = drag.exec(Qt.DropAction.CopyAction)

        if result == Qt.DropAction.IgnoreAction:
            logger.info("Drag ended outside MNAV window — safely canceled.")
            self._show_cancel_feedback()

        self.viewport().unsetCursor()

    # --------------------------------------------------------
    # Cancel feedback
    # --------------------------------------------------------
    def _show_cancel_feedback(self):
        self.viewport().setToolTip("Drag canceled")
        QTimer.singleShot(1200, lambda: self.viewport().setToolTip(""))



# ============================================================
# MacroPalette Container (Theme-Aware)
# ============================================================
class MacroPalette(QFrame):
    """Displays macro categories and draggable macro actions."""

    def __init__(self):
        super().__init__()
        self.theme = get_theme("Mocha")
        self.setObjectName("MacroPalette")
        self._build_ui()

    # --------------------------------------------------------
    # UI Layout
    # --------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        self.title = QLabel("Macro Library")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))

        # Category dropdown
        self.category_dropdown = QComboBox()
        self.category_dropdown.setObjectName("MacroPaletteDropdown")
        self.category_dropdown.addItems(list(MACRO_LIBRARY.keys()))
        self.category_dropdown.currentTextChanged.connect(self._update_macro_list)

        # Macro List
        self.macro_list = DraggableMacroList()
        self.macro_list.setObjectName("MacroPaletteList")

        # Add widgets
        layout.addWidget(self.title)
        layout.addWidget(self.category_dropdown)
        layout.addWidget(self.macro_list, stretch=1)

        # Load initial content
        self._update_macro_list(self.category_dropdown.currentText())

    # --------------------------------------------------------
    # Apply Theme
    # --------------------------------------------------------
    def apply_theme(self, theme):
        """
        Called by MainWindow each time the theme changes.
        """
        self.theme = theme

        # Frame background
        self.setStyleSheet(build_frame_styles(theme))

        # Dropdown
        self.category_dropdown.setStyleSheet(build_combo_styles(theme))

        # Macro list
        self.macro_list.apply_theme(theme)

        # Title inherits global theme via main stylesheet
        # No special styling needed.

    # --------------------------------------------------------
    # List Refresh
    # --------------------------------------------------------
    def _update_macro_list(self, category):
        self.macro_list.clear()
        for macro in MACRO_LIBRARY.get(category, []):
            item = QListWidgetItem(macro["name"])
            item.setData(Qt.ItemDataRole.UserRole, macro["id"])
            self.macro_list.addItem(item)
