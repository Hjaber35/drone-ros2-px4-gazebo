import cv2
import mediapipe as mp
import pyfirmata
import time
import math

board = pyfirmata.Arduino("COM3")
it = pyfirmata.util.Iterator(board)
it.start()
time.sleep(1)

ENA = board.get_pin("d:6:p")
IN1 = board.get_pin("d:7:o")
IN2 = board.get_pin("d:8:o")

ENA.write(1.0)  # always ON (full speed)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hand = mp_hands.Hands(max_num_hands=1)

CLOSED_TH = 0.05
OPEN_TH   = 0.08
mode = "FORWARD"

try:
    while True:
        ok, frame = cap.read()
        if not ok:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hand.process(rgb)

        if result.multi_hand_landmarks:
            hl = result.multi_hand_landmarks[0]
            thumb = hl.landmark[4]
            index = hl.landmark[8]
            distance = math.sqrt((thumb.x-index.x)**2 + (thumb.y-index.y)**2)

            if distance <= CLOSED_TH:
                # REVERSE
                IN1.write(1)
                IN2.write(1)
                mode = "REVERSE"
            elif distance >= OPEN_TH:
                # FORWARD
                IN1.write(1)
                IN2.write(0)
                mode = "FORWARD"

            mp_drawing.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)
            print(f"dist={d:.4f} mode={mode}")

        cv2.imshow("Jaber Camera", frame)
        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            IN1.write(0)
            IN2.write(1)
            break

finally:
    ENA.write(0.0)
    IN1.write(0)
    IN2.write(0)
    cap.release()
    cv2.destroyAllWindows()
    board.exit()
