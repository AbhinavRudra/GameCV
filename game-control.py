import cv2
import mediapipe as mp
from pynput.keyboard import Controller, Key

keyboard = Controller()
pressed_keys = set()

def hold_key(key):
    """Press and hold a key (if not already held)."""
    if key not in pressed_keys:
        keyboard.press(key)
        pressed_keys.add(key)

def release_key(key):
    """Release a key (if currently held)."""
    if key in pressed_keys:
        keyboard.release(key)
        pressed_keys.remove(key)

def release_all():
    """Release all currently held keys."""
    for key in list(pressed_keys):
        release_key(key)

# MediaPipe hands setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)
cap.set(3, 420)
cap.set(4, 340)

def fingers_up(hand_landmarks, hand_label):
    """Return a list of 5 values (0 or 1) for Thumb, Index, Middle, Ring, Pinky"""
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    if hand_label == "Right":
        fingers.append(1 if hand_landmarks.landmark[tip_ids[0]].x > hand_landmarks.landmark[tip_ids[0] - 1].x else 0)
    else:
        fingers.append(1 if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x else 0)

    # Other fingers
    for id in range(1, 5):
        fingers.append(1 if hand_landmarks.landmark[tip_ids[id]].y < hand_landmarks.landmark[tip_ids[id] - 2].y else 0)

    return fingers

while True:
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    left_fingers = 0
    right_fingers = 0

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            hand_label = handedness.classification[0].label  # "Left" or "Right"
            fingers = fingers_up(hand_landmarks, hand_label)
            totalFingers = fingers.count(1)

            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if hand_label == "Left":
                left_fingers = totalFingers
                cv2.putText(img, f'Left: {totalFingers}', (50, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

                # Left hand: Forward, Drift, Brake
                if totalFingers == 5:  # Forward
                    hold_key(Key.up)
                    release_key(Key.up)

                elif totalFingers == 4:  # Brake
                    hold_key(Key.down)
                    release_key(Key.down)

                elif totalFingers == 3:  # Drift
                    hold_key('s')
                    release_key('s')

            if hand_label == "Right":
                right_fingers = totalFingers
                cv2.putText(img, f'Right: {totalFingers}', (50, 100),
                            cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

                # Right hand: Left / Right
                if totalFingers == 4:
                    hold_key(Key.left)
                    release_key(Key.right)
                elif totalFingers == 5:
                    hold_key(Key.right)
                    release_key(Key.left)
                else:
                    release_key(Key.left)
                    release_key(Key.right)

            if hand_label == "Right" and hand_label == "Left":
                hold_key(Key.space)
                release_key(Key.space)

    else:
        # No hands detected → release all keys
        release_all()

    cv2.imshow('Dual Hand Control - Asphalt Legends', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

release_all()
cap.release()
cv2.destroyAllWindows()
