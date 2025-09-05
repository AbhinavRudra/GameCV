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
cap.set(3, 640)
cap.set(4, 480)

def fingers_up(hand_landmarks, hand_label):
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

while True:
    success, img = cap.read()
    if not success:
        continue
        
    img = cv2.flip(img, 1)  # Mirror the image for better user experience
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    # FIXED: Reset finger counts each frame and track which hands are detected
    left_fingers = None
    right_fingers = None
    hands_detected = {"Left": False, "Right": False}

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            hand_label = handedness.classification[0].label  # "Left" or "Right"
            hands_detected[hand_label] = True  # Mark this hand as detected
            
            fingers = fingers_up(hand_landmarks, hand_label)
            totalFingers = fingers.count(1)

            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if hand_label == "Left":
                left_fingers = totalFingers
                cv2.putText(img, f'Left: {totalFingers} fingers', (50, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                # Show individual finger states
                finger_states = ''.join(['1' if f else '0' for f in fingers])
                cv2.putText(img, f'L fingers: {finger_states}', (50, 80),
                            cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)

            if hand_label == "Right":
                right_fingers = totalFingers
                cv2.putText(img, f'Right: {totalFingers} fingers', (50, 120),
                            cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                # Show individual finger states
                finger_states = ''.join(['1' if f else '0' for f in fingers])
                cv2.putText(img, f'R fingers: {finger_states}', (50, 150),
                            cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)

    # FIXED: Process control logic with proper None checking
    action_text = ""
    
    # Left hand controls: Forward, Brake, Drift
    if hands_detected["Left"] and left_fingers is not None:
        if left_fingers == 5:  # Forward
            hold_key(Key.up)
            action_text += "Forward "
        elif left_fingers == 4:  # Brake
            hold_key(Key.down)
            action_text += "Brake "
        elif left_fingers == 3:  # Drift
            hold_key(Key.down)
            action_text += "Drift "
        else:
            # Left hand detected but no matching gesture - release left hand keys
            release_key(Key.up)
            release_key(Key.down)
            release_key('s')
    else:
        # Left hand not detected - release all left hand keys
        release_key(Key.up)
        release_key(Key.down)
        release_key('s')

    # Right hand controls: Left/Right steering
    if hands_detected["Right"] and right_fingers is not None:
        if right_fingers == 4:  # Turn left
            hold_key(Key.left)
            release_key(Key.right)
            action_text += "Left "
        elif right_fingers == 5:  # Turn right
            hold_key(Key.right)
            release_key(Key.left)
            action_text += "Right "
        else:
            # Right hand detected but no matching gesture - release steering keys
            release_key(Key.left)
            release_key(Key.right)
    else:
        # Right hand not detected - release all steering keys
        release_key(Key.left)
        release_key(Key.right)
    
    if hands_detected["Right"] and hands_detected["Left"] and right_fingers is not None and left_fingers is not None:
        if left_fingers == 5 and right_fingers == 5:
            hold_key(Key.esc)
            release_key(Key.esc)

    # Display current action
    if action_text:
        cv2.putText(img, f'Action: {action_text}', (50, 250),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

    # Special action when both hands detected
    if hands_detected["Left"] and hands_detected["Right"]:
        cv2.putText(img, 'Both Hands Detected', (50, 200),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)

    # FIXED: Show status when no hands detected
    if not hands_detected["Left"] and not hands_detected["Right"]:
        cv2.putText(img, 'No Hands Detected', (50, 200),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

    cv2.imshow('Dual Hand Control - Asphalt Legends', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

release_all()
cap.release()
cv2.destroyAllWindows()