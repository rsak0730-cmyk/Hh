import json
import os
import random
import subprocess
import time

class MotorController:
    def __init__(self, screen_w, screen_h, keyboard_config=None):
        self.w, self.h = screen_w, screen_h
        if keyboard_config is None:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            keyboard_config = os.path.join(base, "config", "keyboard_matrix.json")
        try:
            with open(keyboard_config, "r", encoding="utf-8") as f:
                self.key_matrix = json.load(f)
        except Exception:
            self.key_matrix = {}

    def _exec(self, cmd):
        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except Exception:
            try:
                subprocess.run(["adb", "shell"] + cmd, capture_output=True, check=True)
            except Exception:
                pass

    def set_touch_visuals(self, enable=True):
        val = "1" if enable else "0"
        self._exec(["settings", "put", "system", "show_touches", val])

    def tap(self, norm_x, norm_y):
        px = int(norm_x * self.w)
        py = max(int(norm_y * self.h), int(0.05 * self.h))
        hold = random.randint(65, 85)
        self._exec(["input", "swipe", str(px), str(py), str(px), str(py), str(hold)])
        time.sleep(0.15)

    def bezier_swipe(self, start_norm, end_norm, steps=5):
        x0, y0 = int(start_norm[0] * self.w), int(start_norm[1] * self.h)
        x2, y2 = int(end_norm[0] * self.w), int(end_norm[1] * self.h)
        dur = random.randint(220, 280)
        self._exec(["input", "swipe", str(x0), str(y0), str(x2), str(y2), str(dur)])
        time.sleep(0.3)

    def type_text(self, text):
        # Keyboard focus delay
        time.sleep(0.35)
        # Escape spaces and quotes for direct input fallback
        escaped_text = text.replace(" ", "%s").replace("'", "\\'").replace('"', '\\"')
        try:
            self._exec(["input", "text", escaped_text])
            time.sleep(0.2)
        except Exception:
            # Fallback character tap if direct input fails
            for ch in text.lower():
                if ch in self.key_matrix:
                    c = self.key_matrix[ch]
                    self.tap(c[0] + random.uniform(-0.005, 0.005), c[1] + random.uniform(-0.005, 0.005))
                    time.sleep(random.uniform(0.08, 0.12))
                elif ch == " ":
                    self._exec(["input", "keyevent", "KEYCODE_SPACE"])
                    time.sleep(0.1)

    def press_key(self, key_name):
        m = {
            "BACK": "KEYCODE_BACK",
            "HOME": "KEYCODE_HOME",
            "ENTER": "KEYCODE_ENTER",
            "APP_SWITCH": "KEYCODE_APP_SWITCH"
        }
        if key_name in m:
            self._exec(["input", "keyevent", m[key_name]])
            time.sleep(0.2)
