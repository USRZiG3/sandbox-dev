"""
profile_manager.py
------------------
Basic profile utilities for MNAV Macropad Configurator.

Phase 1:
- Provide default profile names for the UI.
- Map between display names and internal profile IDs used by config_manager.
"""

DEFAULT_PROFILES = ["Default", "Gaming", "Editing"]


def get_default_profiles():
    """Return the default list of profile display names."""
    return list(DEFAULT_PROFILES)


def display_to_id(display_name: str) -> str:
    """
    Convert a human-readable profile name into a stable internal ID.

    Examples:
        "Default" -> "default"
        "Gaming"  -> "gaming"
        "Video Editing" -> "video_editing"
    """
    if not display_name:
        return "default"
    slug = display_name.strip().lower().replace(" ", "_")
    return slug
