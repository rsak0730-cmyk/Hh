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

        self.add_widget(Label(text="Mira Astra Agent", font_size='22sp', size_hint_y=0.10, bold=True))

        # API Key Input
        self.api_input = TextInput(
            hint_text="Enter Gemini API Key",
            multiline=False,
            size_hint_y=0.10,
            password=True
        )
        self.add_widget(self.api_input)

        # Goal Input
        self.goal_input = TextInput(
            hint_text="Enter Goal (e.g. Open YouTube and play lofi)",
            multiline=False,
            size_hint_y=0.10
        )
        self.add_widget(self.goal_input)

        # Action Buttons Layout (Start + Stop)
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.12)
        
        self.start_btn = Button(
            text="Start Agent",
            background_color=(0.1, 0.6, 0.9, 1),
            bold=True
        )
        self.start_btn.bind(on_press=self.on_start)
        btn_layout.add_widget(self.start_btn)

        self.stop_btn = Button(
            text="STOP",
            background_color=(0.9, 0.2, 0.2, 1),
            bold=True,
            disabled=True
        )
        self.stop_btn.bind(on_press=self.on_stop)
        btn_layout.add_widget(self.stop_btn)

        self.add_widget(btn_layout)

        # Real-time Status / Logs Display
        self.scroll = ScrollView(size_hint_y=0.58)
        self.status = Label(
            text="Ready. Enter API key and Goal to begin.",
            size_hint_y=None,
            halign="left",
            valign="top"
        )
        self.status.bind(texture_size=self.status.setter('size'))
        self.scroll.add_widget(self.status)
        self.add_widget(self.scroll)

    def on_start(self, instance):
        api_key = self.api_input.text.strip()
        goal = self.goal_input.text.strip()

        if not api_key:
            self.append_log("Error: Gemini API Key dalna zaroori hai!")
            return
        if not goal:
            self.append_log("Error: Goal enter karein!")
            return

        os.environ["GEMINI_API_KEY"] = api_key
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.append_log(f"Goal set: {goal}")

        threading.Thread(target=self._run_thread, args=(goal,), daemon=True).start()

    def on_stop(self, instance):
        from agent import stop_agent
        stop_agent()
        self.append_log("Sent STOP signal...")

    def _run_thread(self, goal):
        try:
            from agent import run_agent
            run_agent(goal, callback=self.append_log)
        except Exception as e:
            self.append_log(f"Runtime Exception: {str(e)}")
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
