import base64
import io
import json
import os
import re
import time
import requests

SYS_P = """You are Mira Astra, an Android Mobile-Use Agent. Respond ONLY with valid JSON:
{"thought": "...", "action": "TAP"|"SWIPE"|"TYPE"|"KEY"|"DONE", "coordinates": [x,y], "swipe_coords": [[x1,y1],[x2,y2]], "text": "...", "key": "BACK"|"HOME"|"ENTER", "is_complete": false}"""

class VisionBrain:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "").strip()
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required.")
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"

    def decide_next_action(self, image, goal, history):
        # Convert image to Base64
        if isinstance(image, bytes):
            b64_img = base64.b64encode(image).decode("utf-8")
        elif isinstance(image, str):
            b64_img = image
        else:
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=75)
            b64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")

        prompt_text = f"Goal: {goal}\nHistory: {history[-3:] if history else 'None'}\nScreen attached."

        payload = {
            "system_instruction": {
                "parts": [{"text": SYS_P}]
            },
            "contents": [{
                "parts": [
                    {"text": prompt_text},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": b64_img
                        }
                    }
                ]
            }],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        }

        headers = {"Content-Type": "application/json"}
        max_retries = 3
        backoff = 2.0

        for attempt in range(max_retries):
            try:
                res = requests.post(self.url, headers=headers, json=payload, timeout=25)
                res.raise_for_status()
                data = res.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                clean = re.sub(r"^```(?:json)?\n|\n```$", "", raw_text.strip(), flags=re.MULTILINE)
                return json.loads(clean)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(backoff)
                    backoff *= 2.0
                else:
                    return {
                        "thought": f"API Request Failed: {str(e)}",
                        "action": "KEY",
                        "key": "BACK",
                        "is_complete": False
                    }
