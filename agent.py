import os
import sys
import time
import subprocess
from core.device_profiler import DeviceProfiler
from core.screen_pipeline import ScreenPipeline
from core.motor_controller import MotorController
from core.vision_brain import VisionBrain

# Global emergency stop flag
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
    info = profiler.get_info()
    motor = MotorController(info["width"], info["height"])
    brain = VisionBrain()

    # Step 1: Self-Minimize & Visual Touches Activation
    log("Enabling visual touches and minimizing to background...")
    motor.set_touch_visuals(True)
    motor.press_key("HOME")
    time.sleep(1.0)

    # Step 2: Intent Fast Launch Shortcut
    if check_intent_shortcut(goal):
        log("Target app recognized. Launched via direct intent.")

    history = []
    prev_image = None
    stuck_counter = 0

    # Step 3: Main Autonomous Execution Loop
    for step in range(1, max_steps + 1):
        if STOP_REQUESTED:
            log("Emergency stop requested. Halting immediately.")
            break

        log(f"Step {step}/{max_steps}: Capturing screen...")
        current_image = ScreenPipeline.capture_stream(target_width=720)
        
        if current_image is None:
            log("Screen capture failed. Waiting 1.5s...")
            time.sleep(1.5)
            continue

        # Stuck Recovery (Visual Frame Diff Check)
        if prev_image is not None:
            diff = ScreenPipeline.compute_frame_diff(prev_image, current_image)
            if diff < 0.015:
                stuck_counter += 1
                log(f"Screen static detected (diff: {diff:.3f}). Stuck count: {stuck_counter}")
            else:
                stuck_counter = 0

        if stuck_counter >= 2:
            log("Screen loop detected! Executing recovery swipe up...")
            motor.bezier_swipe((0.5, 0.7), (0.5, 0.3))
            stuck_counter = 0
            time.sleep(1.0)
            continue

        prev_image = current_image

        # Query Gemini Vision Brain
        decision = brain.decide_next_action(current_image, goal, history)
        thought = decision.get("thought", "")
        action = decision.get("action", "DONE").upper()
        log(f"Reasoning: {thought}")
        log(f"Action: {action}")

        history.append({
            "step": step,
            "action": action,
            "coordinates": decision.get("coordinates"),
            "thought": thought
        })

        if decision.get("is_complete", False) or action == "DONE":
            log("Goal accomplished successfully!")
            break

        # Motor Execution
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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Mira Astra Agent")
    parser.add_argument("--goal", type=str, required=True, help="Task to perform")
    parser.add_argument("--steps", type=int, default=15, help="Max execution steps")
    args = parser.parse_args()

    run_agent(args.goal, args.steps)
