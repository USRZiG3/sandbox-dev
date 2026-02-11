import json, os

CONFIG_PATH = os.path.join("config", "macros.json")

def load_macros(profile="default"):
    """Load macro assignments for the given profile."""
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(profile, {})

def save_macros(profile="default", macros=None):
    """Save macro assignments for the given profile."""
    if macros is None:
        macros = {}
    data = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    data[profile] = macros
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

