import os
import sys
import time
import subprocess
from core.device_profiler import DeviceProfiler
from core.screen_pipeline import ScreenPipeline
from core.motor_controller import MotorController
from core.vision_brain import VisionBrain
from core.voice_engine import VoiceEngine

STOP_REQUESTED = False

COMMON_APPS = {
    "youtube": "com.google.android.youtube",
    "spotify": "com.spotify.music",
    "whatsapp": "com.whatsapp",
    "chrome": "com.android.chrome",
    "settings": "com.android.settings",
    "camera": "com.android.camera2",
    "play store": "com.android.vending",
    "instagram": "com.instagram.android"
}

def stop_agent():
    global STOP_REQUESTED
    STOP_REQUESTED = True

def launch_package_directly(package_name):
    cmd = ["monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"]
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except Exception:
        try:
            subprocess.run(["adb", "shell"] + cmd, capture_output=True, check=True)
        except Exception:
            pass

def check_intent_shortcut(goal):
    lower_goal = goal.lower()
    for app_name, pkg in COMMON_APPS.items():
        if f"open {app_name}" in lower_goal or f"launch {app_name}" in lower_goal:
            launch_package_directly(pkg)
            time.sleep(1.5)
            return True
    return False

def run_agent(goal, max_steps=15, callback=None):
    global STOP_REQUESTED
    STOP_REQUESTED = False

    def log(msg):
        if callback:
            callback(msg)
        else:
            print(f"[Mira Agent] {msg}")

    profiler = DeviceProfiler()
    if not profiler.check_bridge_alive():
        log("Warning: ADB/Shell Bridge unresponsive. Check pairing/Shizuku.")

    info = profiler.get_info()
    motor = MotorController(info["width"], info["height"])
    brain = VisionBrain()

    log("Starting task execution...")
    VoiceEngine.speak("Starting your task.")
    motor.set_touch_visuals(True)
    motor.press_key("HOME")
    time.sleep(1.0)

    if check_intent_shortcut(goal):
        log("Target app opened directly.")

    history = []
    prev_image = None
    stuck_counter = 0

    for step in range(1, max_steps + 1):
        if STOP_REQUESTED:
            log("Emergency stop requested. Halting.")
            VoiceEngine.speak("Task stopped.")
            break

        cur_w, cur_h = profiler.get_current_dimensions()
        motor.w, motor.h = cur_w, cur_h

        log(f"Step {step}/{max_steps}: Analyzing screen...")
        current_image = ScreenPipeline.capture_stream(target_width=720)
        
        if current_image is None:
            time.sleep(1.2)
            continue

        if prev_image is not None:
            diff = ScreenPipeline.compute_frame_diff(prev_image, current_image)
            if diff < 0.015:
                stuck_counter += 1
                log(f"Screen static detected. Recovery count: {stuck_counter}")
            else:
                stuck_counter = 0

        if stuck_counter >= 2:
            log("Anti-loop recovery triggered.")
            motor.bezier_swipe((0.5, 0.7), (0.5, 0.3))
            stuck_counter = 0
            time.sleep(1.0)
            continue

        prev_image = current_image

        decision = brain.decide_next_action(current_image, goal, history)
        thought = decision.get("thought", "")
        action = decision.get("action", "DONE").upper()
        log(f"Brain: {thought}")
        log(f"Action: {action}")

        history.append({
            "step": step,
            "action": action,
            "coordinates": decision.get("coordinates"),
            "thought": thought
        })

        if decision.get("is_complete", False) or action == "DONE":
            log("Goal accomplished successfully!")
            VoiceEngine.speak("Task complete.")
            break

        if action == "TAP":
            coords = decision.get("coordinates", [0.5, 0.5])
            motor.tap(coords[0], coords[1])
        elif action == "SWIPE":
            scoords = decision.get("swipe_coords", [[0.5, 0.7], [0.5, 0.3]])
            motor.bezier_swipe(scoords[0], scoords[1])
        elif action == "TYPE":
            text = decision.get("text", "")
            motor.type_text(text)
        elif action == "KEY":
            key = decision.get("key", "BACK")
            motor.press_key(key)

        time.sleep(1.2)

    log("Session ended.")
