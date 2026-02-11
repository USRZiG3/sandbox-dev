"""
sidebar.py
-----------
Sidebar Component with:
- Connect/Disconnect
- Profile selection
- Macro save/load
- NEW: Clear Key button
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QPushButton, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.gui.styles import (
    build_button_styles,
    build_combo_styles,
    build_frame_styles
)
from src.utils.profile_manager import get_default_profiles


class Sidebar(QFrame):

    connect_clicked = pyqtSignal()
    disconnect_clicked = pyqtSignal()
    profile_changed = pyqtSignal(str)
    encoder_binding_changed = pyqtSignal(str, str)  
    # (binding_key, macro_id) e.g. ("E0_CW", "macro_vol_up")


    clear_key_clicked = pyqtSignal()  # NEW: signal to clear selected key

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self._build_ui()

    # --------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(14, 14, 14, 14)

    # Header
        self.header_label = QLabel("Device Control")

        self.status_label = QLabel("Status: Disconnected")

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self._on_connect_clicked)

    # Profiles
        self.profile_label = QLabel("Profile:")

        self.profile_dropdown = QComboBox()
        self.profile_dropdown.addItems(get_default_profiles())
        self.profile_dropdown.currentTextChanged.connect(
            lambda val: self.profile_changed.emit(val)
        )

        self.add_profile_btn = QPushButton("＋ Add Profile")
        self.remove_profile_btn = QPushButton("－ Remove Profile")

    # Macro controls
        self.macro_header = QLabel("Macro Management")

        self.save_button = QPushButton("💾 Save Macros")
        self.load_button = QPushButton("📂 Load Macros")

    # Encoder bindings (minimal)
        self.encoder_header = QLabel("Encoder 0")
        self.encoder_header.setVisible(False)

        self.enc_cw_label = QLabel("CW:")
        self.enc_cw_label.setVisible(False)
        self.enc_cw_dropdown = QComboBox()
        self.enc_cw_dropdown.setVisible(False)

        self.enc_ccw_label = QLabel("CCW:")
        self.enc_ccw_label.setVisible(False)
        self.enc_ccw_dropdown = QComboBox()
        self.enc_ccw_dropdown.setVisible(False)

        self.enc_btn_label = QLabel("Button:")
        self.enc_btn_label.setVisible(False)
        self.enc_btn_dropdown = QComboBox()
        self.enc_btn_dropdown.setVisible(False)

    # Wire change events
        self.enc_cw_dropdown.currentTextChanged.connect(
            lambda _: self._emit_encoder_binding("E0_CW", self.enc_cw_dropdown)
        )
        self.enc_ccw_dropdown.currentTextChanged.connect(
            lambda _: self._emit_encoder_binding("E0_CCW", self.enc_ccw_dropdown)
        )
        self.enc_btn_dropdown.currentTextChanged.connect(
            lambda _: self._emit_encoder_binding("E0_BTN", self.enc_btn_dropdown)
        )


    # NEW: Clear Key button
        self.clear_key_btn = QPushButton("🧹 Clear Selected Key")
        self.clear_key_btn.setEnabled(False)
        self.clear_key_btn.clicked.connect(self.clear_key_clicked)

    # Layout
        layout.addWidget(self.header_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.connect_btn)
        layout.addSpacing(10)

        layout.addWidget(self.profile_label)
        layout.addWidget(self.profile_dropdown)
        layout.addWidget(self.add_profile_btn)
        layout.addWidget(self.remove_profile_btn)
        layout.addSpacing(10)

        layout.addWidget(self.macro_header)
        layout.addWidget(self.save_button)
        layout.addWidget(self.load_button)

        layout.addSpacing(10)
        layout.addWidget(self.encoder_header)
        layout.addWidget(self.enc_cw_label)
        layout.addWidget(self.enc_cw_dropdown)
        layout.addWidget(self.enc_ccw_label)
        layout.addWidget(self.enc_ccw_dropdown)
        layout.addWidget(self.enc_btn_label)
        layout.addWidget(self.enc_btn_dropdown)


        layout.addWidget(self.clear_key_btn)
        layout.addStretch()


    # --------------------------------------------------------
    def set_encoder_visible(self, visible: bool):
        for w in [
            self.encoder_header,
            self.enc_cw_label, self.enc_cw_dropdown,
            self.enc_ccw_label, self.enc_ccw_dropdown,
            self.enc_btn_label, self.enc_btn_dropdown,
        ]:
            w.setVisible(visible)

    def set_macro_options(self, options: list[tuple[str, str]]):
        """
        options: list of (display_name, macro_id)
        Example: [("— Unassigned —", ""), ("Copy", "macro_copy"), ...]
        """
        def fill(combo: QComboBox):
            combo.blockSignals(True)
            combo.clear()
            for name, mid in options:
                combo.addItem(name, mid)
            combo.blockSignals(False)

        fill(self.enc_cw_dropdown)
        fill(self.enc_ccw_dropdown)
        fill(self.enc_btn_dropdown)

    def set_encoder_bindings(self, bindings: dict):
        """
        bindings contains keys like E0_CW/E0_CCW/E0_BTN -> macro_id
        """
        self._select_by_macro_id(self.enc_cw_dropdown, bindings.get("E0_CW", ""))
        self._select_by_macro_id(self.enc_ccw_dropdown, bindings.get("E0_CCW", ""))
        self._select_by_macro_id(self.enc_btn_dropdown, bindings.get("E0_BTN", ""))

    def _select_by_macro_id(self, combo: QComboBox, macro_id: str):
        macro_id = (macro_id or "").strip()
        combo.blockSignals(True)
        # Find item with matching userData
        for i in range(combo.count()):
            if (combo.itemData(i) or "") == macro_id:
                combo.setCurrentIndex(i)
                break
        else:
            # fallback to first item
            combo.setCurrentIndex(0)
        combo.blockSignals(False)

    def _emit_encoder_binding(self, binding_key: str, combo: QComboBox):
        mid = combo.currentData() or ""
        self.encoder_binding_changed.emit(binding_key, str(mid))
    

    # --------------------------------------------------------
    def apply_theme(self, theme):
        frame_qss = build_frame_styles(theme)
        button_qss = build_button_styles(theme)
        combo_qss = build_combo_styles(theme)

        self.setStyleSheet(frame_qss)

        for btn in [
            self.connect_btn,
            self.add_profile_btn,
            self.remove_profile_btn,
            self.save_button,
            self.load_button,
            self.clear_key_btn,
        ]:
            btn.setStyleSheet(button_qss)
            
        for combo in [
            self.profile_dropdown, 
            self.enc_cw_dropdown, 
            self.enc_ccw_dropdown, 
            self.enc_btn_dropdown,
        ]:
            combo.setStyleSheet(combo_qss)
    

        self.profile_dropdown.setStyleSheet(combo_qss)

    # --------------------------------------------------------
    def _on_connect_clicked(self):
        if "Connect" in self.connect_btn.text():
            self.connect_clicked.emit()
        else:
            self.disconnect_clicked.emit()


    # --------------------------------------------------------
    def get_current_profile(self):
        return self.profile_dropdown.currentText()
    
    def set_connected(self, connected: bool):
        if connected:
            self.status_label.setText("Status: Connected")
            self.connect_btn.setText("Disconnect")
        else:
            self.status_label.setText("Status: Disconnected")
            self.connect_btn.setText("Connect")

    def set_scanning(self, scanning: bool):
        if scanning:
            self.status_label.setText("Status: Scanning...")
            self.connect_btn.setEnabled(False)
        else:
            self.connect_btn.setEnabled(True)



