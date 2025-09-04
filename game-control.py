import cv2
from cvzone.HandTrackingModule import HandDetector
import pyautogui

detector = HandDetector(detectionCon=0.5, maxHands=2)
cap = cv2.VideoCapture(0) # default camera
cap.set(3, 640)  # Width    
cap.set(4, 480)  # Height  

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
            
            # Get hand type and position for display
            hand_type = hand["type"]
            x, y = hand["center"]
            
            if hand_type == "Left":
                left_fingers = totalFingers
                cv2.putText(img, f'Left: {totalFingers}', (50, 50), 
                           cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                
                # Left hand controls arrow keys
                if totalFingers == 2:
                    pyautogui.keyDown('right')
                    pyautogui.keyUp('left')
                elif totalFingers == 3:
                    pyautogui.hotkey('s','d')
               
            
            if hand_type == "Right":
                right_fingers = totalFingers
                cv2.putText(img, f'Right: {totalFingers}', (50, 100), 
                           cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                
                # Right hand controls WASD keys
                if totalFingers == 2:
                    pyautogui.keyDown('left')
                    pyautogui.keyUp('right')
                elif totalFingers == 3:
                    pyautogui.hotkey('s','d')
             
            if hand_type == "Right" and hand_type == "Left":
                if left_fingers == 0 and right_fingers == 0:
                    pyautogui.press('escape')
                

    
    cv2.imshow('Dual Hand Control', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()