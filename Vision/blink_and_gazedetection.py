import cv2
import mediapipe as mp
import numpy as np
import requests
import time
import threading

# ====================== CONFIG ======================
ESP_IP = "http://10.239.49.98"   # ESP8266 IP (keep this as your current static IP)
DOUBLE_BLINK_TIME = 1.0          # Max gap between two blinks for "double blink"
LONG_BLINK_TIME = 0.8            # Duration threshold for "long blink" (STOP)

# ====================== MEDIAPIPE SETUP ======================
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)

# Landmark indices
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
LEFT_IRIS = [468, 469, 470, 471]
RIGHT_IRIS = [473, 474, 475, 476]

# ====================== STATE VARIABLES ======================
blink_state = False
blink_duration_start = 0.0
last_blink_time = 0.0

CALIBRATION_DONE = False
CENTER_RATIO = 0.5

# ====================== UTILITY FUNCTIONS ======================
def euclidean_distance(p1, p2):
    return np.linalg.norm(p1 - p2)

def blink_ratio(eye_points, landmarks):
    """Compute blink ratio for one eye."""
    top = (landmarks[eye_points[1]] + landmarks[eye_points[2]]) / 2
    bottom = (landmarks[eye_points[4]] + landmarks[eye_points[5]]) / 2
    vertical = euclidean_distance(top, bottom)
    horizontal = euclidean_distance(landmarks[eye_points[0]], landmarks[eye_points[3]])
    return horizontal / vertical if vertical != 0 else 0

def iris_position(iris_center, eye_left, eye_right):
    """Classify gaze as LEFT / RIGHT / CENTER using calibrated CENTER_RATIO."""
    width = np.linalg.norm(eye_right - eye_left)
    if width == 0:
        return "CENTER", 0.5
    ratio = (iris_center[0] - eye_left[0]) / width

    if ratio < CENTER_RATIO - 0.05:
        return "RIGHT", ratio
    elif ratio > CENTER_RATIO + 0.05:
        return "LEFT", ratio
    else:
        return "CENTER", ratio

# ====================== NETWORK FUNCTIONS ======================
def send_command(command):
    """Single, fast HTTP send to ESP8266 (blocking, but very short)."""
    try:
        r = requests.get(f"{ESP_IP}/{command}", timeout=0.4)
        if r.status_code == 200:
            print("Sent command:", command)
        else:
            print("ESP responded with status:", r.status_code)
    except requests.exceptions.RequestException:
        # Do NOT block the main thread with retries
        print("ESP not reachable (single attempt). Command:", command)

def send_command_async(command):
    """Run send_command in a separate thread so vision loop never stalls."""
    threading.Thread(target=send_command, args=(command,), daemon=True).start()

# ====================== MAIN LOOP ======================
cap = cv2.VideoCapture(0)

# Optional: lower resolution for smoother FPS on weaker laptops
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Press 'c' to calibrate center gaze once the window opens.")
print("Press ESC to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera not detected.")
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    h, w, _ = frame.shape

    gaze = "CALIBRATE"
    ratio_val = 0.5

    if results.multi_face_landmarks:
        mesh_points = np.array(
            [[int(p.x * w), int(p.y * h)] for p in results.multi_face_landmarks[0].landmark]
        )

        # ===== Blink Detection =====
        left_ratio = blink_ratio(LEFT_EYE, mesh_points)
        right_ratio = blink_ratio(RIGHT_EYE, mesh_points)
        blink_avg = (left_ratio + right_ratio) / 2

        current_time = time.time()

        # Eye landmarks for gaze
        left_eye_left = mesh_points[33]
        left_eye_right = mesh_points[133]
        left_iris_center = mesh_points[LEFT_IRIS].mean(axis=0).astype(int)

        if CALIBRATION_DONE:
            gaze, ratio_val = iris_position(left_iris_center, left_eye_left, left_eye_right)
        else:
            gaze, ratio_val = "CALIBRATE", 0.5

        # ---- Blink state machine ----
        if blink_avg > 5.0 and not blink_state:
            # Blink started
            blink_state = True
            blink_duration_start = current_time

        elif blink_avg <= 5.0 and blink_state:
            # Blink ended
            blink_state = False
            blink_duration = current_time - blink_duration_start

            # 1) Long blink → STOP (highest priority)
            if blink_duration >= LONG_BLINK_TIME:
                print("Long Blink -> STOP")
                send_command_async("BLINK")

            # 2) Double blink → FORWARD
            elif current_time - last_blink_time <= DOUBLE_BLINK_TIME:
                print("Double Blink -> FORWARD")
                send_command_async("FORWARD")
                last_blink_time = 0  # reset

            # 3) Single blink + gaze → LEFT / RIGHT
            else:
                if gaze == "LEFT":
                    print("Blink + LEFT -> Turn LEFT")
                    send_command_async("LEFT")
                elif gaze == "RIGHT":
                    print("Blink + RIGHT -> Turn RIGHT")
                    send_command_async("RIGHT")
                else:
                    print("Single Blink (ignored)")
                last_blink_time = current_time

        # ===== Display Info =====
        cv2.putText(frame, "Gaze: " + gaze, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(frame, "Ratio: {:.2f}".format(ratio_val), (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.circle(frame, tuple(left_iris_center), 3, (0, 0, 255), -1)
    else:
        cv2.putText(frame, "Face not detected", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Eye Gesture Control", frame)
    key = cv2.waitKey(1) & 0xFF

    # ===== Center Calibration =====
    if key == ord('c') and results.multi_face_landmarks:
        mesh_points = np.array(
            [[int(p.x * w), int(p.y * h)] for p in results.multi_face_landmarks[0].landmark]
        )
        left_eye_left = mesh_points[33]
        left_eye_right = mesh_points[133]
        left_iris_center = mesh_points[LEFT_IRIS].mean(axis=0).astype(int)
        CENTER_RATIO = (left_iris_center[0] - left_eye_left[0]) / np.linalg.norm(left_eye_right - left_eye_left)
        CALIBRATION_DONE = True
        print("Calibrated CENTER_RATIO: {:.3f}".format(CENTER_RATIO))

    elif key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
