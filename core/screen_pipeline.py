import io
import subprocess
import numpy as np
from PIL import Image

class ScreenPipeline:
    @staticmethod
    def capture_stream(target_width=720):
        raw_bytes = None
        try:
            proc = subprocess.Popen(["screencap", "-p"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            raw_bytes, _ = proc.communicate()
        except Exception:
            pass

        if not raw_bytes or len(raw_bytes) < 100:
            try:
                proc = subprocess.Popen(["adb", "exec-out", "screencap", "-p"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                raw_bytes, _ = proc.communicate()
            except Exception:
                pass

        if not raw_bytes or len(raw_bytes) < 100:
            return None

        cleaned_bytes = raw_bytes.replace(b"\r\n", b"\n")
        try:
            img = Image.open(io.BytesIO(cleaned_bytes)).convert("RGB")
        except Exception:
            return None

        if target_width and img.width != target_width:
            ratio = target_width / float(img.width)
            target_height = int(float(img.height) * ratio)
            img = img.resize((target_width, target_height), Image.Resampling.BILINEAR)
        return img

    @staticmethod
    def compute_frame_diff(img1, img2):
        if img1 is None or img2 is None:
            return 1.0
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        if arr1.shape != arr2.shape:
            return 1.0
        diff = np.mean(np.abs(arr1.astype("float32") - arr2.astype("float32"))) / 255.0
        return float(diff)
