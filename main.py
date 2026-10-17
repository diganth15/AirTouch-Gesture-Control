```python
import cv2
import mediapipe as mp
import serial
import time

# ESP32 connection
PORT = "COM5"
BAUD = 115200

try:
    esp32 = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("Connected to AirTouch ESP32 on", PORT)
except serial.SerialException as error:
    print("ESP32 connection failed:", error)
    print("Check COM5 and close Arduino Serial Monitor.")
    raise SystemExit(1)

# MediaPipe hand tracking
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.65,
    min_tracking_confidence=0.60
)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Cannot open webcam.")
    esp32.close()
    hands.close()
    raise SystemExit(1)


def send_command(command):
    esp32.write((command + "\n").encode("utf-8"))
    print("Sent:", command)


def detect_gesture(hand):
    lm = hand.landmark

    # Four non-thumb fingers
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    extended = [
        lm[tip].y < lm[pip].y
        for tip, pip in zip(tips, pips)
    ]

    index, middle, ring, pinky = extended
    count = sum(extended)

    # Approximate thumb extension for a right hand
    thumb = abs(lm[4].x - lm[2].x) > 0.06

    if count == 0 and not thumb:
        return "ALL_OFF", "FIST: ALL OFF"

    if count == 4 and thumb:
        return "ALL_ON", "OPEN PALM: ALL ON"

    if thumb and pinky and not index and not middle and not ring:
        return "LED5", "THUMB + PINKY: LED 5"

    if count == 1 and index:
        return "LED1", "ONE FINGER: LED 1"

    if count == 2 and index and middle:
        return "LED2", "TWO FINGERS: LED 2"

    if count == 3 and index and middle and ring:
        return "LED3", "THREE FINGERS: LED 3"

    if count == 4:
        return "LED4", "FOUR FINGERS: LED 4"

    return None, "GESTURE NOT RECOGNIZED"


previous_command = None

try:
    while True:
        success, frame = camera.read()

        if not success:
            print("Camera frame unavailable.")
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        label = "Show your hand"

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]

            mp_draw.draw_landmarks(
                frame, hand, mp_hands.HAND_CONNECTIONS
            )

            command, label = detect_gesture(hand)

            # Send only when the recognized command changes
            if command is not None and command != previous_command:
                send_command(command)
                previous_command = command

            elif command is None:
                previous_command = None

        else:
            previous_command = None

        cv2.putText(
            frame, "AirTouch Gesture Control",
            (20, 35), cv2.FONT_HERSHEY_SIMPLEX,
            0.8, (255, 255, 255), 2
        )

        cv2.putText(
            frame, label,
            (20, 75), cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 255, 0), 2
        )

        cv2.imshow("AirTouch", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    camera.release()
    cv2.destroyAllWindows()
    hands.close()
    esp32.close()
    print("AirTouch stopped.")
```
