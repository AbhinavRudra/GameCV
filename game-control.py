import cv2
from cvzone.HandTrackingModule import HandDetector
import pyautogui

# Track pressed keys to release them later
pressed_keys = set()

def hold_key(key):
    """Press and hold a key (if not already held)."""
    if key not in pressed_keys:
        pyautogui.keyDown(key)
        pressed_keys.add(key)

def release_key(key):
    """Release a key (if currently held)."""
    if key in pressed_keys:
        pyautogui.keyUp(key)
        pressed_keys.remove(key)

def release_all():
    """Release all currently held keys."""
    for key in list(pressed_keys):
        release_key(key)

detector = HandDetector(detectionCon=0.7, maxHands=2)
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)

    left_fingers = 0
    right_fingers = 0

    if hands:
        for hand in hands:
            fingers = detector.fingersUp(hand)
            totalFingers = fingers.count(1)
            hand_type = hand["type"]

            if hand_type == "Left":
                left_fingers = totalFingers
                cv2.putText(img, f'Left: {totalFingers}', (50, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

                # Left hand: Forward, Drift, Brake
                if totalFingers == 5:       # Forward
                    hold_key('up')
                else:
                    release_key('up')
                if totalFingers == 0:       # Brake
                    hold_key('down')
                else:
                    release_key('down')

                if totalFingers == 3:       # Drift (same as left hand)
                    pyautogui.hotkey('s','d')
                

            if hand_type == "Right":
                right_fingers = totalFingers
                cv2.putText(img, f'Right: {totalFingers}', (50, 100),
                            cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

                # Right hand: Left /Right
                if totalFingers == 1:       # Left turn
                    hold_key('left')
                else:
                    release_key('left')

                if totalFingers == 2:       # Right turn
                    hold_key('right')
                else:
                    release_key('right')


        # Both hands closed (0 fingers) = Pause
        if left_fingers == 5 and right_fingers == 5:
            pyautogui.press('escape')
        # if left_fingers == 0 and right_fingers == 0:
        #     pyautogui.press('space')
        #     pyautogui.press('space')
        
        

    else:
        # No hands detected → release all keys
        release_all()

    cv2.imshow('Dual Hand Control - Asphalt Legends', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

release_all()
cap.release()
cv2.destroyAllWindows()
