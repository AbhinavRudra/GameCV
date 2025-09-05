# GameCV

GameCV is a Python-based project that leverages computer vision to enable gesture-based controls for games. Using a webcam, the program detects hand gestures and maps them to keyboard actions, allowing users to interact with games in a hands-free manner. This project is particularly suited for racing games like Asphalt Legends.

## Features

- **Hand Gesture Recognition**: Utilizes MediaPipe and OpenCV to detect and track hand gestures in real-time.
- **Dual-Hand Tracking**: Supports independent gesture recognition for both hands.
- **Customizable Controls**: Maps gestures to keyboard actions using PyAutoGUI.
- **Smooth Mouse Movement**: Implements smoothing for precise cursor control.
- **Game-Specific Actions**: Predefined gestures for actions like steering, accelerating, braking, and drifting.

## How It Works

1. **Hand Detection**: The program uses MediaPipe to detect hand landmarks and classify them as left or right hands.
2. **Gesture Mapping**: Specific gestures are mapped to actions:
   - **Left Hand**:
     - 5 fingers: Accelerate
     - 2 fingers: Brake
     - 0 fingers: Drift
   - **Right Hand**:
     - 2 fingers: Turn Left
     - 3 fingers: Turn Right
   - **Both Hands**:
     - 0 fingers on both: Pause
     - 5 fingers on both: Exit
3. **Mouse Control**: Single index finger movement controls the mouse cursor, while pinching gestures simulate mouse clicks.

## Video Demonstration

![Demo Video](demo.mp4)

## Requirements

- Python 3.11
- OpenCV
- MediaPipe
- PyAutoGUI
- NumPy

Install the dependencies using:
```bash
pip install -r requirements.txt
```

## Usage

1. Ensure your webcam is connected.
2. Run the script:
```bash
python game.py
```
3. Use the predefined gestures to control the game.
