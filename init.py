import cv2
import mediapipe as mp
from pynput.keyboard import Controller, Key
import numpy as np
import autopy

class init:
    def __init__(self):
        self.keyboard = Controller()
        self.key = Key
        self.pressed_keys = set()
        self.wCam, self.hCam = 640, 480
        self.frameR = 100  # Frame Reduction
        self.smoothening = 7
        # MediaPipe hands setup
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.pTime, self.plocX, self.plocY, self.clocX, self.clocY = 0, 0, 0, 0, 0


        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
    )

        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.wScr, self.hScr = autopy.screen.size()

    def hold_key(self, key):
        """Press and hold a key (if not already held)."""
        if key not in self.pressed_keys:
            self.keyboard.press(key)
            self.pressed_keys.add(key)

    def release_key(self, key):
        """Release a key (if currently held)."""
        if key in self.pressed_keys:
            self.keyboard.release(key)
            self.pressed_keys.remove(key)

    def release_all(self):
        """Release all currently held keys."""
        for key in list(self.pressed_keys):
            self.release_key(key)

    def fingers_up(self, hand_landmarks, hand_label):
        """Return a list of 5 values (0 or 1) for Thumb, Index, Middle, Ring, Pinky"""
        tip_ids = [4, 8, 12, 16, 20]
        pip_ids = [3, 6, 10, 14, 18]  # PIP joints for better finger detection
        fingers = []

        # Thumb - check both x and y coordinates for better detection
        thumb_tip = hand_landmarks.landmark[tip_ids[0]]
        thumb_pip = hand_landmarks.landmark[pip_ids[0]]
        
        # MediaPipe labels are from camera's perspective, so they're flipped
        if hand_label == "Right":
            # Camera sees "Right" but it's actually user's left hand - thumb points left when up
            thumb_up = thumb_tip.x < thumb_pip.x
        else:
            # Camera sees "Left" but it's actually user's right hand - thumb points right when up
            thumb_up = thumb_tip.x > thumb_pip.x
        
        fingers.append(1 if thumb_up else 0)

        # Other fingers - check if tip is above PIP joint
        for id in range(1, 5):
            finger_tip = hand_landmarks.landmark[tip_ids[id]]
            finger_pip = hand_landmarks.landmark[pip_ids[id]]
            fingers.append(1 if finger_tip.y < finger_pip.y else 0)

        return fingers

    def find_distance(self, p1, p2, hand_landmarks, img):
        """Find distance between two landmarks"""
        x1, y1 = int(hand_landmarks.landmark[p1].x * self.wCam), int(hand_landmarks.landmark[p1].y * self.hCam)
        x2, y2 = int(hand_landmarks.landmark[p2].x * self.wCam), int(hand_landmarks.landmark[p2].y * self.hCam)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        # Draw line and points
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
        
        length = np.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

