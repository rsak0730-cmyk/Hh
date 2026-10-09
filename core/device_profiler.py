import json
import os
import subprocess

class DeviceProfiler:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config", "brand_profiles.json")
        self.brand = self._get_prop("ro.product.brand").lower()
        self.model = self._get_prop("ro.product.model")
        self.width, self.height = self._get_screen_dimensions()
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                profiles = json.load(f)
            self.profile = profiles.get(self.brand, profiles.get("default", {}))
        except Exception:
            self.profile = {"app_drawer_scroll": "vertical", "search_bar_pos": "bottom", "back_button_ratio": [0.2, 0.97], "recents_button_ratio": [0.8, 0.97], "status_bar_height_ratio": 0.04}

    def _run_cmd(self, cmd_list):
        try:
            res = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
            return res.stdout.strip()
        except Exception:
            try:
                res = subprocess.run(["adb", "shell"] + cmd_list, capture_output=True, text=True, check=True)
                return res.stdout.strip()
            except Exception:
                return ""

    def _get_prop(self, prop_name):
        out = self._run_cmd(["getprop", prop_name])
        return out if out else "default"

    def _get_screen_dimensions(self):
        out = self._run_cmd(["wm", "size"])
        try:
            dimensions = out.split()[-1]
            w, h = dimensions.split("x")
            return int(w), int(h)
        except Exception:
            return 1080, 2400

    def get_info(self):
        return {"brand": self.brand, "model": self.model, "width": self.width, "height": self.height, "profile": self.profile}
