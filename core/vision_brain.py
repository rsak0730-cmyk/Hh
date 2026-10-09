import json
import os
import re
from google import genai
from google.genai import types

SYSTEM_PROMPT = """You are Mira Astra, an autonomous Android Mobile-Use Agent. Respond ONLY with valid JSON:
{"thought": "...", "action": "TAP" | "SWIPE" | "TYPE" | "KEY" | "DONE", "coordinates": [norm_x, norm_y], "swipe_coords": [[start_x, start_y], [end_x, end_y]], "text": "...", "key": "BACK" | "HOME" | "ENTER", "is_complete": false}"""

class VisionBrain:
    def __init__(self, api_key=None):
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY environment variable is required.")
        self.client = genai.Client(api_key=key)

    def decide_next_action(self, image, goal, history):
        prompt = f"Goal: {goal}\nPrevious Action History: {history[-3:] if history else 'None'}\nAnalyze the attached screen and return the next action in JSON."
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[image, prompt],
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, response_mime_type="application/json", temperature=0.1)
            )
            raw_text = response.text.strip()
            clean_json = re.sub(r"^```(?:json)?\n|\n```$", "", raw_text, flags=re.MULTILINE)
            return json.loads(clean_json)
        except Exception as e:
            return {"thought": str(e), "action": "KEY", "key": "BACK", "is_complete": False}
