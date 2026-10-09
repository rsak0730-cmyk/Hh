import argparse
import os
import signal
import sys
import time
from core.device_profiler import DeviceProfiler
from core.motor_controller import MotorController
from core.screen_pipeline import ScreenPipeline
from core.vision_brain import VisionBrain

def run_agent(goal: str, max_steps: int = 15):
    print("=" * 50)
    print("🚀 Initializing Mira Astra Autonomous Agent...")
    print("=" * 50)

    # 1. Device profiling
    try:
        profiler = DeviceProfiler()
        info = profiler.get_info()
        print(f"📱 Detected: {info['brand'].upper()} ({info['model']}) | Display: {info['width']}x{info['height']}")
    except Exception as e:
        print(f"❌ Device profiling failed. Ensure ADB is connected: {e}")
        sys.exit(1)

    # 2. Motor & Visual indicators setup
    motor = MotorController(info['width'], info['height'])
    motor.set_touch_visuals(True)
    print("✨ Hardware touch indicators enabled (Animated touch ripples active).")

    # Graceful exit handler on Ctrl+C
    def cleanup_and_exit(sig=None, frame=None):
        print("\n🔒 Restoring system touch visuals to default...")
        motor.set_touch_visuals(False)
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    # 3. Vision Brain & Pipeline setup
    try:
        brain = VisionBrain()
    except Exception as e:
        print(f"❌ Failed to initialize VisionBrain: {e}")
        motor.set_touch_visuals(False)
        sys.exit(1)

    pipeline = ScreenPipeline()
    history = []
    step = 0
    stuck_counter = 0

    try:
        while step < max_steps:
            step += 1
            print(f"\n[Step {step}/{max_steps}] Scanning screen state...")

            frame_before = pipeline.capture_stream()
            if frame_before is None:
                print("⚠️ Retrying screen capture in 1s...")
                time.sleep(1.0)
                continue

            decision = brain.decide_next_action(frame_before, goal, history)

            thought = decision.get("thought", "Executing step...")
            action = decision.get("action", "").upper()
            is_complete = decision.get("is_complete", False)

            print(f"🧠 Thought: {thought}")

            if is_complete or action == "DONE":
                print("🎯 Goal completed successfully!")
                break

            if action == "TAP":
                coords = decision.get("coordinates", [0.5, 0.5])
                print(f"👉 Executing Centered Tap at: {coords}")
                motor.tap(coords[0], coords[1])
            elif action == "SWIPE":
                sc = decision.get("swipe_coords", [[0.5, 0.7], [0.5, 0.3]])
                print(f"👆 Executing Natural Bezier Swipe from {sc[0]} to {sc[1]}")
                motor.bezier_swipe(sc[0], sc[1])
            elif action == "TYPE":
                txt = decision.get("text", "")
                print(f"⌨️ Virtual Typing on keyboard: '{txt}'")
                motor.type_text(txt)
            elif action == "KEY":
                k = decision.get("key", "BACK")
                print(f"🔘 Pressing System Key: {k}")
                motor.press_key(k)
            else:
                print(f"⚠️ Unknown action received: {action}. Defaulting to short wait.")
                time.sleep(0.5)

            # Settle wait & delta check
            time.sleep(0.5)
            frame_after = pipeline.capture_stream()
            if frame_after is not None:
                diff = pipeline.compute_frame_diff(frame_before, frame_after)
                if diff < 0.01 and action not in ["TYPE", "DONE"]:
                    stuck_counter += 1
                    print(f"⚠️ Visual delta low ({diff:.4f}). Screen did not change.")
                    if stuck_counter >= 2:
                        print("🔄 Stuck detected! Nudging screen via mild scroll...")
                        motor.bezier_swipe([0.5, 0.6], [0.5, 0.5], steps=3)
                        stuck_counter = 0
                else:
                    stuck_counter = 0

            history.append({
                "step": step,
                "action": action,
                "thought": thought
            })

    except Exception as err:
        print(f"\n❌ Runtime error: {err}")
    finally:
        cleanup_and_exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mira Astra Device-Use Agent")
    parser.add_argument("--goal", type=str, required=True, help="Command to execute")
    parser.add_argument("--max-steps", type=int, default=15, help="Maximum steps limit")
    args = parser.parse_args()

    run_agent(args.goal, args.max_steps)
