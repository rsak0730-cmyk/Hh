import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import mainthread

class MiraUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, spacing=10, **kwargs)

        self.add_widget(Label(text="Mira Astra Agent", font_size='22sp', size_hint_y=0.12, bold=True))

        # API Key Input
        self.api_input = TextInput(
            hint_text="Enter Gemini API Key",
            multiline=False,
            size_hint_y=0.12,
            password=True
        )
        self.add_widget(self.api_input)

        # Goal Input
        self.goal_input = TextInput(
            hint_text="Enter Goal (e.g. Open YouTube)",
            multiline=False,
            size_hint_y=0.12
        )
        self.add_widget(self.goal_input)

        # Execute Button
        self.btn = Button(
            text="Start Agent",
            size_hint_y=0.12,
            background_color=(0.1, 0.6, 0.9, 1)
        )
        self.btn.bind(on_press=self.start_thread)
        self.add_widget(self.btn)

        # Scrollable Status / Logs
        self.scroll = ScrollView(size_hint_y=0.52)
        self.status = Label(
            text="Ready. Enter API key and Goal to begin.",
            size_hint_y=None,
            halign="left",
            valign="top"
        )
        self.status.bind(texture_size=self.status.setter('size'))
        self.scroll.add_widget(self.status)
        self.add_widget(self.scroll)

    def start_thread(self, instance):
        api_key = self.api_input.text.strip()
        goal = self.goal_input.text.strip()

        if not api_key:
            self.update_log("Error: Gemini API Key dalna zaroori hai!")
            return
        if not goal:
            self.update_log("Error: Please enter a goal!")
            return

        os.environ["GEMINI_API_KEY"] = api_key
        self.update_log(f"Starting goal: {goal}...")
        self.btn.disabled = True

        threading.Thread(target=self._run_safe_agent, args=(goal,), daemon=True).start()

    def _run_safe_agent(self, goal):
        try:
            # Lazy import taaki launch par crash na ho
            from agent import run_agent
            run_agent(goal)
            self.update_log("Completed successfully!")
        except Exception as e:
            self.update_log(f"Agent Crash/Error: {str(e)}")
        finally:
            self.enable_btn()

    @mainthread
    def update_log(self, text):
        self.status.text += f"\n{text}"

    @mainthread
    def enable_btn(self):
        self.btn.disabled = False

class MiraAstraApp(App):
    def build(self):
        return MiraUI()

if __name__ == "__main__":
    MiraAstraApp().run()
