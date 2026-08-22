import cv2
import mediapipe as mp
import pyfirmata
import time
import math
import traceback

board = pyfirmata.Arduino("COM5")
motorPin = board.get_pin("d:3:p")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hand = mp_hands.Hands(max_num_hands=1)


while True:
    try:
        success, frame = cap.read()
        if not success:
            continue

        RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hand.process(RGB_frame)

        if result.multi_hand_landmarks:
            handLandmarks = result.multi_hand_landmarks[0]
            thumbTip = handLandmarks.landmark[4]
            indexTip = handLandmarks.landmark[8]

            distance = math.sqrt(
                (thumbTip.x - indexTip.x) ** 2 +
                (thumbTip.y - indexTip.y) ** 2
            )

            MIN_D = 0.018
            MAX_D = 0.4
            speed = (distance - MIN_D) / (MAX_D - MIN_D)

            motorPin.write(speed)

            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            print("distance:", distance, "speed:", speed)

        else:
            motorPin.write(0)
            print("no hand detected")

        cv2.imshow("Jaber Camera", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    except Exception:
        # THIS is what stops the window from closing suddenly
        print("\n--- ERROR (script would have closed here) ---")
        traceback.print_exc()
        print("--- continuing ---\n")
        time.sleep(0.2)
        continue

cap.release()
cv2.destroyAllWindows()
