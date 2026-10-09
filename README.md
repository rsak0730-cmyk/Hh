# Mira Astra - Autonomous Mobile GUI Agent

Mira Astra is a high-speed, vision-grounded Android device-use agent inspired by desktop computer-use models. It performs human mimicry via direct gesture primitives (natural taps, Bezier curved swiping, and on-screen virtual typing) with real-time visual touch ripples.

## Key Features
- **Visual Touches & Animations:** Automatically enables Android hardware touch indicators so every action is visible on screen.
- **Brand Auto-Profiling:** Dynamically detects Samsung, Xiaomi, or Stock ROM to adjust back button coordinates and app drawer flows.
- **Human-Grade Motor Engine:** Sub-pixel center locking and non-linear touch hold/drag timing.
- **In-Memory Streaming:** Captures raw framebuffer via pipe streams (zero flash memory writes).
- **Virtual Key Matrix:** Character-by-character typing with natural finger jitter.

## Prerequisites
- Android device with **Wireless Debugging** / **Shizuku** enabled.
- Termux with Python 3.10+.
- Gemini API Key.

## Setup & Running
```bash
git clone [https://github.com/](https://github.com/)<your-username>/mira-mobile-agent.git
cd mira-mobile-agent
pip install -r requirements.txt
export GEMINI_API_KEY="your_api_key_here"

# Execute a goal
python agent.py --goal "Open Spotify and search for Arijit Singh"
