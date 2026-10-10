import json
import os
import subprocess

class DeviceProfiler:
    def __init__(self, config_path=None):
        if config_path is None:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base, "config", "brand_profiles.json")
        self.brand = self._get_prop("ro.product.brand").lower()
        self.model = self._get_prop("ro.product.model")
        self.width, self.height = self.get_current_dimensions()
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.profile = data.get(self.brand, data.get("default", {}))
        except Exception:
            self.profile = {
                "app_drawer_scroll": "vertical",
                "search_bar_pos": "bottom",
                "back_button_ratio": [0.2, 0.97],
                "recents_button_ratio": [0.8, 0.97],
                "status_bar_height_ratio": 0.04
            }

    def _run_cmd(self, cmd):
        try:
            return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()
        except Exception:
            try:
                return subprocess.run(["adb", "shell"] + cmd, capture_output=True, text=True, check=True).stdout.strip()
            except Exception:
                return ""

    def check_bridge_alive(self):
        res = self._run_cmd(["echo", "bridge_ok"])
        return "bridge_ok" in res

    def _get_prop(self, prop_name):
        res = self._run_cmd(["getprop", prop_name])
        return res if res else "default"

    def get_current_dimensions(self):
        res = self._run_cmd(["wm", "size"])
        try:
            parts = res.split()[-1].split("x")
            self.width = int(parts[0])
            self.height = int(parts[1])
            return self.width, self.height
        except Exception:
            return 1080, 2400

    def get_info(self):
        w, h = self.get_current_dimensions()
        return {
            "brand": self.brand,
            "model": self.model,
            "width": w,
            "height": h,
            "profile": self.profile
        }
