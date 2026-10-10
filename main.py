import os
import json
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import mainthread

CONFIG_FILE = "mira_config.json"

def load_saved_key():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("api_key", "")
        except Exception:
            return ""
    return ""

def save_key(api_key):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"api_key": api_key}, f)
    except Exception:
        pass

class MiraUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, spacing=8, **kwargs)

        self.add_widget(Label(text="Mira Astra Agent", font_size='22sp', size_hint_y=0.08, bold=True))

        self.bridge_label = Label(text="Bridge: Checking...", size_hint_y=0.06, color=(0.8, 0.8, 0.2, 1))
        self.add_widget(self.bridge_label)

        saved_key = load_saved_key()
        self.api_input = TextInput(
            hint_text="Enter Gemini API Key",
            text=saved_key,
            multiline=False,
            size_hint_y=0.08,
            password=True
        )
        self.add_widget(self.api_input)

        # Goal Input with Voice Mic Button Row
        goal_row = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=0.08)
        self.goal_input = TextInput(
            hint_text="Enter Goal (e.g. Open YouTube and play lofi)",
            multiline=False
        )
        goal_row.add_widget(self.goal_input)

        self.mic_btn = Button(
            text="Mic",
            size_hint_x=0.25,
            background_color=(0.2, 0.7, 0.4, 1),
            bold=True
        )
        self.mic_btn.bind(on_press=self.on_voice_input)
        goal_row.add_widget(self.mic_btn)
        self.add_widget(goal_row)

        # Execution Controls
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.10)
        self.start_btn = Button(text="Start Agent", background_color=(0.1, 0.6, 0.9, 1), bold=True)
        self.start_btn.bind(on_press=self.on_start)
        btn_layout.add_widget(self.start_btn)

        self.stop_btn = Button(text="STOP", background_color=(0.9, 0.2, 0.2, 1), bold=True, disabled=True)
        self.stop_btn.bind(on_press=self.on_stop)
        btn_layout.add_widget(self.stop_btn)
        self.add_widget(btn_layout)

        # Real-time Event Terminal
        self.scroll = ScrollView(size_hint_y=0.60)
        self.status = Label(text="Ready.", size_hint_y=None, halign="left", valign="top")
        self.status.bind(texture_size=self.status.setter('size'))
        self.scroll.add_widget(self.status)
        self.add_widget(self.scroll)

        threading.Thread(target=self.verify_bridge, daemon=True).start()

    def on_voice_input(self, instance):
        try:
            from core.voice_engine import VoiceEngine
            VoiceEngine.trigger_speech_recognizer()
            self.append_log("Listening for voice input...")
        except Exception as e:
            self.append_log(f"Voice trigger error: {str(e)}")

    def verify_bridge(self):
        try:
            from core.device_profiler import DeviceProfiler
            p = DeviceProfiler()
            if p.check_bridge_alive():
                self.set_bridge_status("Bridge: Connected (ADB OK)", (0.2, 0.9, 0.2, 1))
            else:
                self.set_bridge_status("Bridge: Disconnected (Pair Wireless Debugging)", (0.9, 0.2, 0.2, 1))
        except Exception:
            self.set_bridge_status("Bridge: Not Available", (0.9, 0.2, 0.2, 1))

    @mainthread
    def set_bridge_status(self, text, color):
        self.bridge_label.text = text
        self.bridge_label.color = color

    def on_start(self, instance):
        api_key = self.api_input.text.strip()
        goal = self.goal_input.text.strip()
        if not api_key or not goal:
            self.append_log("Error: API Key and Goal are both required.")
            return

        save_key(api_key)
        os.environ["GEMINI_API_KEY"] = api_key
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.append_log(f"Goal set: {goal}")

        threading.Thread(target=self._run_thread, args=(goal,), daemon=True).start()

    def on_stop(self, instance):
        from agent import stop_agent
        stop_agent()
        self.append_log("Emergency STOP sent.")

    def _run_thread(self, goal):
        try:
            from agent import run_agent
            run_agent(goal, callback=self.append_log)
        except Exception as e:
            self.append_log(f"Execution Error: {str(e)}")
        finally:
            self.reset_buttons()

    @mainthread
    def append_log(self, text):
        self.status.text += f"\n{text}"

    @mainthread
    def reset_buttons(self):
        self.start_btn.disabled = False
        self.stop_btn.disabled = True

class MiraAstraApp(App):
    def build(self):
        return MiraUI()

if __name__ == "__main__":
    MiraAstraApp().run()
