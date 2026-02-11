"""
styles.py
----------
Theme palettes and stylesheet builders for MNAV Macropad Configurator.

- Provides Catppuccin palettes + additional dark themes.
- Exposes a small "theme engine" API for building consistent QSS.
"""

# -------------------------------------------------------------------
# Theme Palettes
# -------------------------------------------------------------------
THEME_PALETTES = {
    # Catppuccin palettes
    "Mocha": {
        "base": "#1E1E2E", "mantle": "#181825", "crust": "#11111B",
        "text": "#CDD6F4", "subtext": "#A6ADC8", "overlay": "#6C7086",
        "blue": "#89B4FA", "green": "#A6E3A1", "peach": "#FAB387",
        "mauve": "#CBA6F7", "rosewater": "#F5E0DC", "accent": "#89B4FA"
    },
    "Latte": {
        "base": "#EFF1F5", "mantle": "#E6E9EF", "crust": "#DCE0E8",
        "text": "#4C4F69", "subtext": "#5C5F77", "overlay": "#9CA0B0",
        "blue": "#1E66F5", "green": "#40A02B", "peach": "#FE640B",
        "mauve": "#8839EF", "rosewater": "#DC8A78", "accent": "#1E66F5"
    },
    "Frappé": {
        "base": "#303446", "mantle": "#292C3C", "crust": "#232634",
        "text": "#C6D0F5", "subtext": "#A5ADCE", "overlay": "#737994",
        "blue": "#8CAAEE", "green": "#A6D189", "peach": "#EF9F76",
        "mauve": "#CA9EE6", "rosewater": "#F2D5CF", "accent": "#8CAAEE"
    },
    "Macchiato": {
        "base": "#24273A", "mantle": "#1E2030", "crust": "#181926",
        "text": "#CAD3F5", "subtext": "#A5ADCB", "overlay": "#5B6078",
        "blue": "#8AADF4", "green": "#A6DA95", "peach": "#F5A97F",
        "mauve": "#C6A0F6", "rosewater": "#F4DBD6", "accent": "#8AADF4"
    },


    # Additional dark-mode palettes
    "Dracula": {
        "base": "#282a36", "mantle": "#44475a", "crust": "#1e1f29",
        "text": "#f8f8f2", "subtext": "#6272a4", "overlay": "#6272a4",
        "blue": "#8be9fd", "green": "#50fa7b", "peach": "#ffb86c",
        "mauve": "#bd93f9", "rosewater": "#f5e0dc", "accent": "#ff79c6"
    },
    "SolarizedDark": {
        "base": "#002b36", "mantle": "#073642", "crust": "#001f26",
        "text": "#839496", "subtext": "#657b83", "overlay": "#586e75",
        "blue": "#268bd2", "green": "#859900", "peach": "#cb4b16",
        "mauve": "#d33682", "rosewater": "#eee8d5", "accent": "#b58900"
    },
    "MidnightShadows": {
        "base": "#0b1b2b", "mantle": "#102a43", "crust": "#0b1830",
        "text": "#cbd5e1", "subtext": "#94a3b8", "overlay": "#1e293b",
        "blue": "#1e66f5", "green": "#40a02b", "peach": "#f5a97f",
        "mauve": "#8839ef", "rosewater": "#e0e7ff", "accent": "#1e66f5"
    },
    "ObsidianDepths": {
        "base": "#101214", "mantle": "#1c1e20", "crust": "#0d0e10",
        "text": "#e4e6eb", "subtext": "#adb5bd", "overlay": "#6c757d",
        "blue": "#00b8d9", "green": "#00c691", "peach": "#ffab00",
        "mauve": "#be00ff", "rosewater": "#f9fafb", "accent": "#00b8d9"
    },
    "StormyNight": {
        "base": "#2f3640", "mantle": "#353b48", "crust": "#272d3d",
        "text": "#f5f6fa", "subtext": "#dcdde1", "overlay": "#718093",
        "blue": "#00bfff", "green": "#00d084", "peach": "#ff715b",
        "mauve": "#9c88ff", "rosewater": "#f0f0f0", "accent": "#00bfff"
    },
    "DeepSeaAbyss": {
        "base": "#001f3f", "mantle": "#002a5e", "crust": "#00172e",
        "text": "#e0e6f2", "subtext": "#a3b8d0", "overlay": "#005f99",
        "blue": "#007acc", "green": "#28c940", "peach": "#ffa737",
        "mauve": "#7c3ae9", "rosewater": "#f5f6fa", "accent": "#007acc"
    },
    "CharcoalDreams": {
        "base": "#3b3b3b", "mantle": "#2c2c2c", "crust": "#1e1e1e",
        "text": "#dcdcdc", "subtext": "#ababab", "overlay": "#5a5a5a",
        "blue": "#7aa2f7", "green": "#6edb8c", "peach": "#feb971",
        "mauve": "#bf88ff", "rosewater": "#f4f5f7", "accent": "#7aa2f7"
    },
    "MoodyBerry": {
        "base": "#2c2d32", "mantle": "#263437", "crust": "#1b4b4b",
        "text": "#d0d6d6", "subtext": "#79858c", "overlay": "#5e7d7d",
        "blue": "#4c7273", "green": "#86b9b0", "peach": "#e86726",
        "mauve": "#b62779", "rosewater": "#c08b57", "accent": "#b62779"
    },
    "NeonHighlightsDark": {
        "base": "#0d0d0d", "mantle": "#1a1a1a", "crust": "#111111",
        "text": "#f7f7f7", "subtext": "#bbbbbb", "overlay": "#888888",
        "blue": "#1e90ff", "green": "#00ff85", "peach": "#ff0099",
        "mauve": "#ff00cc", "rosewater": "#ffeb3b", "accent": "#1e90ff"
    }
}


# -------------------------------------------------------------------
# Theme Access
# -------------------------------------------------------------------
def get_theme(theme_name: str = "Mocha") -> dict:
    """
    Safely return a theme dict by name.

    Falls back to 'Mocha' if the requested theme does not exist.
    """
    return THEME_PALETTES.get(theme_name, THEME_PALETTES["Mocha"])


# -------------------------------------------------------------------
# Core Stylesheet Builders
# -------------------------------------------------------------------
def build_app_stylesheet(theme: dict) -> str:
    """
    Build the global application stylesheet for high-level widgets.

    This is intended to be applied once at the QMainWindow level:
        window.setStyleSheet(build_app_stylesheet(theme))

    Component-specific overrides can be layered on top if needed.
    """
    base = theme["base"]
    mantle = theme["mantle"]
    crust = theme["crust"]
    text = theme["text"]
    overlay = theme["overlay"]
    blue = theme["blue"]
    green = theme["green"]

    # NOTE: Radius and gaps should stay consistent across widgets.
    # If we adjust the radius standard later, we do it HERE.
    radius = 6

    return f"""
    /* Base window + background */
    QMainWindow {{
        background-color: {base};
        color: {text};
    }}

    QStatusBar {{
        background-color: {mantle};
        color: {text};
    }}

    /* Generic container frames (can be refined with objectName later) */
    QFrame {{
        background-color: {mantle};
        color: {text};
        border: 0px solid {overlay};
        border-radius: {radius}px;
    }}

    QLabel {{
        color: {text};
    }}

    /* Buttons */
    QPushButton {{
        background-color: {mantle};
        color: {text};
        border: 1px solid {overlay};
        border-radius: {radius}px;
        padding: 6px;
    }}
    QPushButton:hover {{
        border-color: {green};
    }}
    QPushButton:checked {{
        background-color: {blue};
        color: {crust};
    }}

    /* Lists */
    QListWidget {{
        background-color: {mantle};
        border: 1px solid {overlay};
        border-radius: {radius}px;
        color: {text};
    }}
    QListWidget::item:hover {{
        background-color: {mantle};
    }}
    QListWidget::item:selected {{
        background-color: {blue};
        color: {crust};
    }}

    /* Combo boxes */
    QComboBox {{
        background-color: {mantle};
        border: 1px solid {overlay};
        border-radius: {radius}px;
        color: {text};
        padding: 4px 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {mantle};
        selection-background-color: {blue};
        selection-color: {crust};
        border: 1px solid {overlay};
        border-radius: {radius}px;
    }}
    """


# -------------------------------------------------------------------
# Component-Level Helpers (for future refinement)
# -------------------------------------------------------------------
def build_button_styles(theme: dict) -> str:
    """Return a reusable QSS block for buttons based on the theme."""
    overlay = theme["overlay"]
    mantle = theme["mantle"]
    text = theme["text"]
    blue = theme["blue"]
    crust = theme["crust"]
    green = theme["green"]
    radius = 6

    return f"""
    QPushButton {{
        background-color: {mantle};
        color: {text};
        border: 1px solid {overlay};
        border-radius: {radius}px;
        padding: 6px;
    }}
    QPushButton:hover {{
        border-color: {green};
    }}
    QPushButton:checked {{
        background-color: {blue};
        color: {crust};
    }}
    """


def build_list_styles(theme: dict) -> str:
    """Return a reusable QSS block for list widgets."""
    mantle = theme["mantle"]
    overlay = theme["overlay"]
    text = theme["text"]
    blue = theme["blue"]
    crust = theme["crust"]
    radius = 6

    return f"""
    QListWidget {{
        background-color: {mantle};
        border: 1px solid {overlay};
        border-radius: {radius}px;
        color: {text};
        padding: 4px;
    }}
    QListWidget::item:hover {{
        background-color: {mantle};
    }}
    QListWidget::item:selected {{
        background-color: {blue};
        color: {crust};
    }}
    """


def build_combo_styles(theme: dict) -> str:
    """Return a reusable QSS block for combo boxes."""
    mantle = theme["mantle"]
    overlay = theme["overlay"]
    text = theme["text"]
    blue = theme["blue"]
    crust = theme["crust"]
    radius = 6

    return f"""
    QComboBox {{
        background-color: {mantle};
        border: 1px solid {overlay};
        border-radius: {radius}px;
        color: {text};
        padding: 4px 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {mantle};
        selection-background-color: {blue};
        selection-color: {crust};
        border: 1px solid {overlay};
        border-radius: {radius}px;
    }}
    """


def build_frame_styles(theme: dict) -> str:
    """Return a reusable QSS block for generic frames/containers."""
    mantle = theme["mantle"]
    text = theme["text"]
    overlay = theme["overlay"]
    radius = 6

    return f"""
    QFrame {{
        background-color: {mantle};
        color: {text};
        border: 0px solid {overlay};
        border-radius: {radius}px;
    }}
    """

