import json
import os
import re
import time
from google import genai
from google.genai import types

SYS_P = """You are Mira Astra, an Android Mobile-Use Agent. Respond ONLY with valid JSON:
{"thought": "...", "action": "TAP"|"SWIPE"|"TYPE"|"KEY"|"DONE", "coordinates": [x,y], "swipe_coords": [[x1,y1],[x2,y2]], "text": "...", "key": "BACK"|"HOME"|"ENTER", "is_complete": false}"""

class VisionBrain:
    def __init__(self, api_key=None):
        k = api_key or os.environ.get("GEMINI_API_KEY")
        if not k:
            raise ValueError("GEMINI_API_KEY environment variable is required.")
        self.client = genai.Client(api_key=k)

    def decide_next_action(self, image, goal, history):
        p = f"Goal: {goal}\nHistory: {history[-3:] if history else 'None'}\nScreen attached."
        
        # 3x Retry loop with exponential backoff
        max_retries = 3
        backoff = 2.0
        
        for attempt in range(max_retries):
            try:
                res = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[image, p],
                    config=types.GenerateContentConfig(
                        system_instruction=SYS_P, 
                        response_mime_type="application/json", 
                        temperature=0.1
                    )
                )
                clean = re.sub(r"^```(?:json)?\n|\n```$", "", res.text.strip(), flags=re.MULTILINE)
                return json.loads(clean)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(backoff)
                    backoff *= 2.0
                else:
                    return {"thought": f"API Error after retries: {str(e)}", "action": "KEY", "key": "BACK", "is_complete": False}
