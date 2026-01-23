import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import json
import requests
import numpy as np
import time
import threading

# ---------------- CONFIG ----------------
ESP_IP = "http://10.239.49.98"  # replace with your ESP8266 IP
MODEL_PATH = r"C:\Users\91911\Desktop\BlinkTrackingApp\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000
BLOCKSIZE = 4000  # smaller = lower latency
DEBOUNCE_TIME = 1.2  # prevent repeated triggers
GRAMMAR = '["forward", "left", "right", "stop", "blink"]'
# ----------------------------------------

q = queue.Queue()
last_command_time = {}
last_command = None


def send_command(command):
    """Send command to ESP8266."""
    try:
        r = requests.get(f"{ESP_IP}/{command}", timeout=1.5)
        if r.status_code == 200:
            print(f"Sent: {command}")
    except requests.exceptions.RequestException:
        print("ESP not reachable, retrying...")
        time.sleep(0.5)


def voice_listener():
    """Capture and recognize voice with low latency."""
    print("Offline Voice Control Active! Say 'forward', 'left', 'right', or 'stop'.")
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE, GRAMMAR)

    last_detected_command = ""
    last_trigger_time = 0

    def callback(indata, frames, time_info, status):
        nonlocal last_detected_command, last_trigger_time
        try:
            data = (indata * 32768).astype(np.int16).tobytes()

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip().lower()
            else:
                partial = json.loads(recognizer.PartialResult()).get("partial", "").lower()
                text = partial.strip()

            # Check if command word is in recognized text
            if text:
                for word in ["forward", "left", "right", "stop", "blink"]:
                    if word in text:
                        now = time.time()
                        # Only trigger if new or enough time passed
                        if word != last_detected_command or (now - last_trigger_time) > DEBOUNCE_TIME:
                            q.put(word)
                            last_detected_command = word
                            last_trigger_time = now
                        break

        except Exception as e:
            print("Callback error:", e)

    with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=BLOCKSIZE, dtype="float32",
                        channels=1, callback=callback):
        print("Listening for offline voice commands...")
        while True:
            sd.sleep(100)


def process_commands():
    """Continuously process recognized commands."""
    global last_command, last_command_time
    while True:
        word = q.get().strip().lower()
        if not word:
            continue

        now = time.time()
        command = None

        if word == "forward":
            command = "FORWARD"
        elif word == "left":
            command = "LEFT"
        elif word == "right":
            command = "RIGHT"
        elif word in ["stop", "blink"]:
            command = "BLINK"

        if command:
            # Debounce repeated triggers
            if last_command == command and (now - last_command_time.get(command, 0)) < DEBOUNCE_TIME:
                continue

            send_command(command)
            last_command = command
            last_command_time[command] = now
        else:
            print("Unrecognized command")


if __name__ == "__main__":
    t1 = threading.Thread(target=voice_listener, daemon=True)
    t1.start()
    process_commands()
