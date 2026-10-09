import json
import os
import random
import subprocess
import time

class MotorController:
    def __init__(self, screen_w, screen_h, keyboard_config=None):
        self.w = screen_w
        self.h = screen_h
        if keyboard_config is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            keyboard_config = os.path.join(base_dir, "config", "keyboard_matrix.json")
        try:
            with open(keyboard_config, "r", encoding="utf-8") as f:
                self.key_matrix = json.load(f)
        except Exception:
            self.key_matrix = {}

    def _exec(self, cmd_args):
        try:
            subprocess.run(cmd_args, capture_output=True, check=True)
        except Exception:
            try:
                subprocess.run(["adb", "shell"] + cmd_args, capture_output=True, check=True)
            except Exception:
                pass

    def set_touch_visuals(self, enable=True):
        val = "1" if enable else "0"
        self._exec(["settings", "put", "system", "show_touches", val])

    def tap(self, norm_x, norm_y):
        px = int(norm_x * self.w)
        py = int(norm_y * self.h)
        if py < int(0.045 * self.h):
            py = int(0.05 * self.h)
        hold_time = random.randint(65, 85)
        self._exec(["input", "swipe", str(px), str(py), str(px), str(py), str(hold_time)])
        time.sleep(0.15)

    def bezier_swipe(self, start_norm, end_norm, steps=5):
        x0 = int(start_norm[0] * self.w)
        y0 = int(start_norm[1] * self.h)
        x2 = int(end_norm[0] * self.w)
        y2 = int(end_norm[1] * self.h)
        duration = random.randint(220, 280)
        self._exec(["input", "swipe", str(x0), str(y0), str(x2), str(y2), str(duration)])
        time.sleep(0.3)

    def type_text(self, text):
        for char in text.lower():
            if char in self.key_matrix:
                coord = self.key_matrix[char]
                jx = coord[0] + random.uniform(-0.005, 0.005)
                jy = coord[1] + random.uniform(-0.005, 0.005)
                self.tap(jx, jy)
                time.sleep(random.uniform(0.08, 0.13))
            elif char == " ":
                self._exec(["input", "keyevent", "KEYCODE_SPACE"])
                time.sleep(0.1)
            else:
                self._exec(["input", "text", char])
                time.sleep(0.1)

    def press_key(self, key_name):
        mapping = {"BACK": "KEYCODE_BACK", "HOME": "KEYCODE_HOME", "ENTER": "KEYCODE_ENTER", "APP_SWITCH": "KEYCODE_APP_SWITCH"}
        if key_name in mapping:
            self._exec(["input", "keyevent", mapping[key_name]])
            time.sleep(0.2)
