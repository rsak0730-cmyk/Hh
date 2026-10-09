import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from agent import run_agent

class MiraUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        
        self.add_widget(Label(text="Mira Astra Agent", font_size='24sp', size_hint_y=0.2))
        
        self.goal_input = TextInput(
            hint_text="Enter Goal (e.g. Open YouTube)",
            multiline=False,
            size_hint_y=0.2
        )
        self.add_widget(self.goal_input)
        
        self.btn = Button(text="Execute Goal", size_hint_y=0.2, background_color=(0, 0.7, 0.9, 1))
        self.btn.bind(on_press=self.start_agent)
        self.add_widget(self.btn)
        
        self.status = Label(text="Ready", size_hint_y=0.4)
        self.add_widget(self.status)

    def start_agent(self, instance):
        goal = self.goal_input.text.strip()
        if not goal:
            self.status.text = "Please enter a valid goal!"
            return
        
        self.status.text = f"Running: {goal}..."
        threading.Thread(target=run_agent, args=(goal,), daemon=True).start()

class MiraAstraApp(App):
    def build(self):
        return MiraUI()

if __name__ == "__main__":
    MiraAstraApp().run()
