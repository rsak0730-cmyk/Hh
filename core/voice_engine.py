import subprocess
import threading

class VoiceEngine:
    @staticmethod
    def speak(text):
        def _run_tts():
            clean_text = text.replace('"', '\\"').replace("'", "\\'")
            # Intent call to Android default TTS Engine
            tts_cmd = [
                "am", "start", "-a", "android.intent.action.QUICK_VIEW",
                "-e", "tts_text", clean_text
            ]
            try:
                subprocess.run(tts_cmd, capture_output=True)
            except Exception:
                try:
                    subprocess.run(["adb", "shell"] + tts_cmd, capture_output=True)
                except Exception:
                    pass

        threading.Thread(target=_run_tts, daemon=True).start()

    @staticmethod
    def trigger_speech_recognizer():
        # Triggers Android native Google Voice Input overlay directly into foreground
        voice_cmd = [
            "am", "start", "-a", "android.speech.action.RECOGNIZE_SPEECH",
            "--es", "android.speech.extra.LANGUAGE_MODEL", "free_form"
        ]
        try:
            subprocess.run(voice_cmd, capture_output=True)
        except Exception:
            try:
                subprocess.run(["adb", "shell"] + voice_cmd, capture_output=True)
            except Exception:
                pass
