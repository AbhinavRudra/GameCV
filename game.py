from init import GameCV
import cv2
import mediapipe as mp
import numpy as np
import autopy

init = GameCV()

while True:
    success, img = init.cap.read()
        
    # Mirror the image for better user experience
    imgf = cv2.flip(img, 1)

    img_rgb = cv2.cvtColor(imgf, cv2.COLOR_BGR2RGB)
    results = init.hands.process(img_rgb)

    # FIXED: Reset finger counts each frame and track which hands are detected
    left_fingers = None
    right_fingers = None
    hands_detected = {"Left": False, "Right": False}

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            hand_label = handedness.classification[0].label  # "Left" or "Right"
            hands_detected[hand_label] = True  # Mark this hand as detected
            init.mp_draw.draw_landmarks(img, hand_landmarks, init.mp_hands.HAND_CONNECTIONS)

            # Get the tip of the index and middle fingers
            # Convert normalized coordinates to pixel coordinates
            lmList = []
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
            
            if len(lmList) != 0:
                x1, y1 = lmList[8][1:]  # Index finger tip
                x2, y2 = lmList[12][1:]  # Middle finger tip
            
            # Check which fingers are up
            fingers = init.fingers_up(hand_landmarks, hand_label)
            totalFingers = fingers.count(1)
            
            # Only Index Finger : Moving Mode
            if fingers[1] == 1 and fingers[2] == 0:
                # Convert Coordinates
                x3 = np.interp(x1, (init.frameR, init.wCam - init.frameR), (0, init.wScr))
                y3 = np.interp(y1, (init.frameR, init.hCam - init.frameR), (0, init.hScr))
                
                # Smoothen Values
                clocX = init.plocX + (x3 - init.plocX) / init.smoothening
                clocY = init.plocY + (y3 - init.plocY) / init.smoothening
                
                # Move Mouse
                autopy.mouse.move(init.wScr - clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                init.plocX, init.plocY = clocX, clocY
            
            # Both Index and middle fingers are up : Clicking Mode
            if fingers[1] == 1 and fingers[2] == 1:
                # Find distance between fingers
                length, img, lineInfo = init.find_distance(8, 12, hand_landmarks, img)
                # print(length)
                # Click mouse if distance short
                if length < 40:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]),
                              15, (0, 255, 0), cv2.FILLED)
                    autopy.mouse.click()
            
            # Left hand finger count and states
            if hand_label == "Left":
                left_fingers = totalFingers
                cv2.putText(imgf, f'Left: {totalFingers} fingers', (50, 50),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                # Show individual finger states
                finger_states = ''.join(['1' if f else '0' for f in fingers])
                cv2.putText(imgf, f'L fingers: {finger_states}', (50, 80),
                            cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)

            # Right hand finger count and states
            if hand_label == "Right":
                right_fingers = totalFingers
                cv2.putText(imgf, f'Right: {totalFingers} fingers', (50, 120),
                            cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                # Show individual finger states
                finger_states = ''.join(['1' if f else '0' for f in fingers])
                cv2.putText(imgf, f'R fingers: {finger_states}', (50, 150),
                            cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)



    action_text = ""
    
    # Left hand controls: Forward, Brake, Drift
    if hands_detected["Left"] and left_fingers is not None:
        if left_fingers == 5:  # Forward
            init.hold_key(init.key.up)
            action_text += "Forward "
        elif left_fingers == 2:  # Brake
            init.hold_key(init.key.down)
            action_text += "Brake "
        elif left_fingers == 0:  # Drift
            init.hold_key('s')
            action_text += "Drift "
        else:
            # Left hand detected but no matching gesture - release left hand keys
            init.release_key(init.key.up)
            init.release_key(init.key.down)
            init.release_key('s')
    else:
        # Left hand not detected - release all left hand keys
        init.release_key(init.key.up)
        init.release_key(init.key.down)
        init.release_key('s')

    # Right hand controls: Left/Right steering
    if hands_detected["Right"] and right_fingers is not None:
        if right_fingers == 2:  # Turn left
            init.hold_key(init.key.left)
            init.release_key(init.key.right)
            action_text += "Left "  
        elif right_fingers == 3:  # Turn right
            init.hold_key(init.key.right)
            init.release_key(init.key.left)
            action_text += "Right "
        else:
            # Right hand detected but no matching gesture - release steering keys
            init.release_key(init.key.left)
            init.release_key(init.key.right)
    else:
        # Right hand not detected - release all steering keys
        init.release_key(init.key.left)
        init.release_key(init.key.right)

    # Both hands detected: Pause/Exit
    if hands_detected["Right"] and hands_detected["Left"] and right_fingers is not None and left_fingers is not None:
        if left_fingers == 0 and right_fingers == 0:
            init.hold_key(init.key.esc)
            init.release_key(init.key.esc)
        elif left_fingers == 5 and right_fingers == 5:
            init.hold_key(init.key.space)
            init.release_key(init.key.space)
            init.hold_key(init.key.space)
            init.release_key(init.key.space)


    # # Display current action
    if action_text:
        cv2.putText(imgf, f'Action: {action_text}', (50, 250),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

    # Special action when both hands detected
    if hands_detected["Left"] and hands_detected["Right"]:
        cv2.putText(imgf, 'Both Hands Detected', (50, 200),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)

    # FIXED: Show status when no hands detected
    if not hands_detected["Left"] and not hands_detected["Right"]:
        cv2.putText(imgf, 'No Hands Detected', (50, 200),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

    cv2.imshow('Hand Control - Asphalt Legends', imgf)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

init.release_all()
init.cap.release()
cv2.destroyAllWindows()