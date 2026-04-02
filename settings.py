import json
import os

SETTINGS_FILE = "settings.json"

VALID_CONTROLS = ("mouse", "arrows", "ad")


class Settings:
    def __init__(self):
        self.fullscreen: bool = False
        self.paddle_control: str = "mouse"  # "mouse" | "arrows" | "ad"

    def load(self):
        """Load settings from settings.json. Uses defaults if file is missing or corrupt."""
        if not os.path.exists(SETTINGS_FILE):
            return
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            self.fullscreen = bool(data.get("fullscreen", False))
            control = data.get("paddle_control", "mouse")
            self.paddle_control = control if control in VALID_CONTROLS else "mouse"
        except (json.JSONDecodeError, OSError):
            pass  # Corrupt or unreadable — keep defaults

    def save(self):
        """Save current settings to settings.json."""
        data = {
            "fullscreen": self.fullscreen,
            "paddle_control": self.paddle_control,
        }
        try:
            tmp = SETTINGS_FILE + ".tmp"
            with open(tmp, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, SETTINGS_FILE)  # Atomic write
        except OSError:
            pass

    def next_control(self):
        """Cycle to the next paddle control scheme."""
        idx = VALID_CONTROLS.index(self.paddle_control)
        self.paddle_control = VALID_CONTROLS[(idx + 1) % len(VALID_CONTROLS)]

    def control_label(self) -> str:
        """Human-readable label for the current control scheme."""
        return {
            "mouse": "MOUSE",
            "arrows": "ARROW KEYS",
            "ad": "A / D KEYS",
        }[self.paddle_control]
