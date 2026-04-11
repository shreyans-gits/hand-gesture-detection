# gesture-lab 🖐️

A collection of hand gesture-controlled applications built using a custom MediaPipe-based hand tracking module. Interact with your computer using nothing but your hands.

---

## Core Module — `HandTracker.py`

A clean, reusable hand tracking module built on top of MediaPipe's Hand Landmarker. It abstracts all the complexity of landmark detection into simple, intuitive objects.

### Features
- Detects up to 2 hands simultaneously
- Returns `Hand` objects with built-in methods
- Correct left/right hand detection (with optional mirror flip)
- Finger state detection (up/down) with proper thumb handling
- Distance measurement between any two landmarks
- Skeleton, bounding box, and handedness label drawing

### Usage

```python
from HandTracker import HandDetector, INDEX, THUMB

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=2)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flip=True)

    if hands:
        hand = hands[0]
        fingers = hand.fingersUp()      # [thumb, index, middle, ring, pinky]
        print(fingers)

        if hand.isFingerUp(INDEX):
            print("Index finger is up!")

        length, p1, p2, mid = hand.findDistance(4, 8)  # thumb tip to index tip
        print(f"Pinch distance: {length}")
```

### `Hand` Object Methods

| Method | Description |
|---|---|
| `fingersUp()` | Returns `[1,0,1,0,0]` style list for all 5 fingers |
| `isFingerUp(fingerId)` | Returns `True/False` for a single finger |
| `findDistance(p1, p2)` | Distance in pixels between any two landmarks |

### Landmark Reference

```
0  - Wrist
4  - Thumb tip
8  - Index tip
12 - Middle tip
16 - Ring tip
20 - Pinky tip
```

---

<!-- ## Projects

### ✏️ Air Whiteboard
Draw on screen using your index finger in the air. Switch colors, clear the canvas, all with hand gestures.

### 🖼️ Image Mover
Open images and drag them around the screen using a pinch gesture. Resize using two hands.

### 🧊 3D Object Interaction *(coming soon)*
Manipulate 3D wireframe objects in real time using hand movements — rotate, scale, and move with gestures.

--- -->

## Requirements

```
opencv-python
mediapipe
```

Install with:

```bash
pip install opencv-python mediapipe
```

You also need the MediaPipe hand landmark model:
- Download `hand_landmarker.task` from the [MediaPipe Models page](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)
- Place it in the same directory as `HandTracker.py`

---

<!-- ## Structure

```
gesture-lab/
│
├── HandTracker.py           # Core hand tracking module
├── hand_landmarker.task     # MediaPipe model file
│
├── air-whiteboard/
│   └── whiteboard.py
│
├── image-mover/
│   └── mover.py
│
└── 3d-object/
    └── object.py
```

--- -->