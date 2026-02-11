"""
main_window.py
---------------
MNAV Macropad Configurator
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QSplitter, QStatusBar, QMenuBar
)
from PyQt6.QtCore import (
    Qt, QTimer
)

from src.utils.device_profile_manager import get_default_device_profile, match_device_profile
from src.data.macro_library import MACRO_LIBRARY

from src.utils.logger import setup_logger
from src.gui.sidebar import Sidebar
from src.gui.macro_palette import MacroPalette
from src.gui.macro_grid import MacroGrid
from src.gui.styles import THEME_PALETTES, get_theme, build_app_stylesheet
from src.utils.config_manager import load_macros, save_macros
from src.utils.profile_manager import display_to_id
from src.device import PicoSerialClient, DeviceScanner


from concurrent.futures import ThreadPoolExecutor
from src.utils.macro_executor import execute_macro_by_id
import time  



logger = setup_logger(__name__)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MNAV Macropad Configurator")
        self.setGeometry(200, 200, 1100, 600)

        self.theme_name = "Mocha"
        self.theme = get_theme(self.theme_name)

        self.current_profile = None
        self.selected_key = None
        self._bindings = {}
        self.device_profile = get_default_device_profile()  
        self.device = PicoSerialClient()
        self.device.connected.connect(self.on_device_connected)
        self.device.disconnected.connect(self.on_device_disconnected)
        self.device.hello.connect(self.on_device_hello)
        self.device.heartbeat.connect(self.on_device_hb)
        self.device.key_event.connect(self.on_device_key)
        self.device.encoder_event.connect(self.on_device_encoder)
        self.device.button_event.connect(self.on_device_button)

        self.device.parse_error.connect(self.on_device_parse_error)
        self.scanner = DeviceScanner(timeout_s=2.5)  # 2.5 is snappy and used to accomidate the encoder
#        self.scanner = DeviceScanner(timeout_s=7.0)  # 7.0 to ensure the device hb is detected in time
        self.scanner.found.connect(self._on_scan_found)
        self.scanner.not_found.connect(self._on_scan_not_found)
        self.scanner.error.connect(self._on_scan_error)
        self.scanner.scanning.connect(self._on_scanning_state)


        self._macro_workers = ThreadPoolExecutor(max_workers=2)

# Key cooldown tracking to prevent macro spam when holding down a key
        self._last_fire = {}          # dict[int, float]
        self._fire_cooldown_s = 0.15  # 150ms; tweak 0.10–0.25 to taste

# Encoder state tracking for better macro binding and to prevent spam when spinning
        self._enc_accum = 0
        self._enc_last_fire = 0.0
        self._enc_cooldown_s = 0.05   # limits fire rate while spinning
        self._enc_steps_per_action = 1  # set to 2 or 4 if your encoder reports multiple ticks per detent

        self._btn_last_fire = {}
        self._btn_cooldown_s = 0.15   # button debounce




        self._init_ui()
        # Auto-connect shortly after UI is ready (non-blocking)
        QTimer.singleShot(250, self.scanner.scan)

    # --------------------------------------------------------
    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Menu bar
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Exit", self.close)

        theme_menu = menu_bar.addMenu("Theme")
        for theme_name in THEME_PALETTES.keys():
            action = theme_menu.addAction(theme_name)
            action.triggered.connect(lambda _, t=theme_name: self._change_theme(t))

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sidebar
        self.sidebar = Sidebar()
        splitter.addWidget(self.sidebar)

        self.sidebar.set_macro_options(self._macro_options())
        self.sidebar.encoder_binding_changed.connect(self._on_encoder_binding_changed)


        self.sidebar.connect_clicked.connect(self._on_connect)
        self.sidebar.disconnect_clicked.connect(self._on_disconnect)

        self.sidebar.profile_changed.connect(self._on_profile_changed)
        self.sidebar.save_button.clicked.connect(self.save_macros)
        self.sidebar.load_button.clicked.connect(self.load_macros)
        self.sidebar.clear_key_clicked.connect(self._clear_selected_key)

        self.sidebar.set_encoder_visible(len(self.device_profile.ui_encoders) > 0)


        # Macro Palette
        self.palette = MacroPalette()
        splitter.addWidget(self.palette)

        # Grid
        self.grid = MacroGrid(
            key_names=self.device_profile.ui_keys,
            encoders=self.device_profile.ui_encoders
        )
        splitter.addWidget(self.grid)




        # Key selection from the grid
        self.grid.button_selected.connect(self._on_key_selected)

        splitter.setSizes([240, 240, 600])
        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Apply theme
        self._apply_theme()

        # Set default profile
        self.current_profile = self.sidebar.get_current_profile()
        self.load_macros()

    # ---------------------------
    # Event Handlers
    # ---------------------------
    def _on_connect(self):
        self.status_bar.showMessage("Searching for device...")
        self.scanner.scan()



    def _on_disconnect(self):
        self.device.stop()
        self.status_bar.showMessage("Disconnected.")
        logger.info("Device disconnected by user.")


    def _auto_connect_device(self, manual: bool = False):
        # Non-blocking: runs scan in background thread
        self.status_bar.showMessage("Searching for device...")
        self.scanner.scan()




    # ---------------------------
    # Profile Handling
    # ---------------------------
    def _on_profile_changed(self, profile_name):
        self.current_profile = profile_name
        self.status_bar.showMessage(f"Active profile: {profile_name}")
        self.load_macros()



    # ---------------------------
    # Device Scan Handlers (background scan)
    # ---------------------------
    def _on_scanning_state(self, scanning: bool):
        # Optional: disable connect button while scanning
        try:
            self.sidebar.connect_btn.setEnabled(not scanning)
        except Exception:
            pass

    def _on_scan_found(self, port: str):
        self.status_bar.showMessage(f"Device found on {port} — connecting...")
        logger.info(f"Device scan found: {port}")
        self.device.start(port)

    def _on_scan_not_found(self):
        self.status_bar.showMessage("No device found.")
        logger.warning("No device found.")

    def _on_scan_error(self, text: str):
        self.status_bar.showMessage(f"Scan error: {text}")
        logger.error(f"Scan error: {text}")




    # ---------------------------
    # Device Callbacks (PicoSerialClient signals)
    # ---------------------------
    def on_device_connected(self, port: str):
        self.sidebar.set_connected(True)
        self.status_bar.showMessage(f"Device connected: {port}")
        logger.info(f"Device connected on {port}")

    def on_device_disconnected(self):
        self.sidebar.set_connected(False)
        self.status_bar.showMessage("Device disconnected.")
        logger.warning("Device disconnected")


    def on_device_hello(self, info):
        # info is HelloInfo (from src/device/protocol.py)
        self.status_bar.showMessage(
            f"{info.type} | FW {info.fw_version} | keys={info.keys} | pins={info.pins}"
        )
        logger.info(f"HELLO: {info}")

        # BEST PRACTICE: treat HELLO as a clean slate moment
        # This avoids stale UI state (your earlier bug: previous profile still displayed)
        self.grid.reset_grid()

        # Load macros for current profile (UI-side bindings)
        # This will populate labels/colors/etc based on saved assignments
        self.load_macros()

    def on_device_hb(self, ts: float):
        # Optional: could update an "alive" indicator in sidebar later
        pass

    def on_device_key(self, ev):
        ui_key_id = int(ev.k) + 1  # device 0-based -> UI 1-based

        btn = self.grid.key_buttons.get(ui_key_id)
        if not btn:
            return

        if ev.edge == "down":
            btn.setChecked(True)

            # --- Cooldown / debounce to prevent spam ---
            now = time.monotonic()
            last = float(self._last_fire.get(ui_key_id, 0.0))
            if (now - last) < self._fire_cooldown_s:
                return
            self._last_fire[ui_key_id] = now

            macro_id = btn.property("macro_id") or ""
            # Execute in worker thread so UI never freezes
            if macro_id:
                self._macro_workers.submit(execute_macro_by_id, macro_id)

        elif ev.edge == "up":
            btn.setChecked(False)

    def on_device_encoder(self, ev):
        d = int(ev.d)
        if d == 0:
            return

        # Accumulate deltas so we can "quantize" into actions
        self._enc_accum += d

        # Throttle so fast spins don't flood the executor
        now = time.monotonic()
        if (now - self._enc_last_fire) < self._enc_cooldown_s:
            return

        # Determine how many actions to fire based on accumulated steps
        step = int(self._enc_steps_per_action)
        if step <= 0:
            step = 1

        actions = 0
        binding_key = None

        if self._enc_accum >= step:
            actions = self._enc_accum // step
            self._enc_accum = self._enc_accum % step
            binding_key = "E0_CW"

        elif self._enc_accum <= -step:
            actions = (-self._enc_accum) // step
            self._enc_accum = -((-self._enc_accum) % step)
            binding_key = "E0_CCW"

        else:
            return

        # ✅ unified bindings dict (keys + encoder + future inputs)
        macro_id = (self._bindings.get(binding_key) or "").strip()
        if not macro_id:
            return

        self._enc_last_fire = now
        self.grid.pulse_encoder(ev.id, ms=60)

        # Fire once per "action" so a fast spin can trigger multiple steps,
        # but still limited by cooldown above.
        for _ in range(actions):
            self._macro_workers.submit(execute_macro_by_id, macro_id)




    def on_device_button(self, ev):
        if ev.edge != "down":
            return

        now = time.monotonic()
        last = float(self._btn_last_fire.get(ev.id, 0.0))
        if (now - last) < self._btn_cooldown_s:
            return
        self._btn_last_fire[ev.id] = now
        self.grid.pulse_encoder(ev.id, ms=90)

        macro_id = (self._bindings.get("E0_BTN") or "").strip()
        if macro_id:
            self._macro_workers.submit(execute_macro_by_id, macro_id)



    



    def on_device_parse_error(self, text: str):
        # Useful while stabilizing the protocol
        logger.warning(f"Device parse error: {text}")


    # ---------------------------
    # Key Selection + Clearing
    # ---------------------------
    def _on_key_selected(self, key_id):
        self.selected_key = key_id
        self.sidebar.clear_key_btn.setEnabled(True)
        self.status_bar.showMessage(f"Selected key: K{key_id}")
        
    def _on_encoder_binding_changed(self, binding_key: str, macro_id: str):
        self._bindings[binding_key] = macro_id or ""
        # persist immediately (simple + safe)
        profile_id = display_to_id(self.current_profile)
        save_macros(profile=profile_id, macros=self._bindings)
        self.status_bar.showMessage(f"Updated {binding_key} binding.")


    def _clear_selected_key(self):
        if self.selected_key is None:
            return
        btn = self.grid.key_buttons[self.selected_key]
        btn.setText(f"K{self.selected_key}")
        btn.setChecked(False)
        self.sidebar.clear_key_btn.setEnabled(False)
        self.status_bar.showMessage(f"Cleared macro from K{self.selected_key}")

        self.selected_key = None


    #---------------------------
    # Macro Options for Sidebar Dropdown
    # ---------------------------
    def _macro_options(self):
        opts = [("— Unassigned —", "")]
        for group, macros in MACRO_LIBRARY.items():
            for m in macros:
                opts.append((f"{group}: {m['name']}", m["id"]))
        return opts
    

    # ---------------------------
    # Macro Save/Load
    # ---------------------------
    def save_macros(self):
        profile_id = display_to_id(self.current_profile)

        # Start with existing bindings (so E0_* survives)
        merged = dict(self._bindings or {})

        # Overwrite only the K* entries from the grid
        merged.update(self.grid.get_macro_assignments())

        self._bindings = merged
        save_macros(profile=profile_id, macros=merged)

        self.status_bar.showMessage(f"Saved macros for profile: {self.current_profile}")


    def load_macros(self):
        profile_id = display_to_id(self.current_profile)
        macros = load_macros(profile=profile_id) or {}

        # Always store the full profile binding map (K1.., E0_CW.. etc.)
        self._bindings = macros

        # Only apply the K* keys to the grid
        self.grid.load_macro_assignments(macros)

        # Apply encoder bindings to sidebar dropdowns (if you added them)
        try:
            self.sidebar.set_encoder_bindings(self._bindings)
        except Exception:
            pass

        self.status_bar.showMessage(f"Loaded macros for profile: {self.current_profile}")





    # ---------------------------
    # Qt Lifecycle Overrides
    # ---------------------------
    def closeEvent(self, event):
        try:
            self.device.stop()
        except Exception:
            pass
        try:
            self.scanner.shutdown()
        except Exception:
            pass
        try:
            self._macro_workers.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass
        super().closeEvent(event)




    # ---------------------------
    # Theme Handling
    # ---------------------------
    def _apply_theme(self):
        self.setStyleSheet(build_app_stylesheet(self.theme))

        self.sidebar.apply_theme(self.theme)
        self.palette.apply_theme(self.theme)
        self.grid.apply_theme(self.theme)

    def _change_theme(self, theme_name):
        self.theme_name = theme_name
        self.theme = get_theme(theme_name)
        self._apply_theme()
        self.status_bar.showMessage(f"Theme switched to {theme_name}")


def run_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()

