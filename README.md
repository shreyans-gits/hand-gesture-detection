# 🖐️ Gesture Lab

A hand gesture-controlled application built with Python, MediaPipe, and OpenCV. Control a whiteboard, your mouse, and a 3D voxel editor — all with just your hands.

---

## 📦 Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

You also need the MediaPipe hand landmarker model file:
- Download `hand_landmarker.task` from the [MediaPipe Models page](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)
- Place it in the root project directory alongside `app.py`

---

## 🚀 Running the App

```bash
python app.py
```

Press `Q` to quit.

---

## 🗂️ Project Structure

```
gesture-lab/
│
├── app.py              # Main application loop
├── HandTracker.py      # Hand detection, landmark tracking, gesture recognition
├── whiteboard.py       # Whiteboard mode
├── airmouse.py         # Air Mouse mode
├── shapes3d.py         # 3D Shapes mode (sphere, model import)
├── cubeeditor.py       # Voxel cube editor (3D Shapes → Cube sub-option)
├── hand_landmarker.task
│
└── GUI/
    ├── open_sans.ttf
    ├── panel0.png
    ├── panel1.png
    ├── panel2.png
    ├── Wpanel0-4.png   # Whiteboard sub-option panels
    └── Dpanel0-2.png   # 3D Shapes sub-option panels
```

---

## 🧭 Navigation

### Opening the Side Panel (Mode Selector)
| Gesture | Action |
|---|---|
| Right hand swipe LEFT + left hand index & middle up | Open side panel |
| Right hand swipe RIGHT + left hand index & middle up | Close side panel |
| Hover index + middle fingertip midpoint over a button for 2s | Select mode |

### Opening the Sub-Option Panel
| Gesture | Action |
|---|---|
| Right hand swipe DOWN | Open sub-option panel |
| Right hand swipe UP | Close sub-option panel |
| Hover index + middle fingertip midpoint over a button for 2s | Select sub-option |

---

## ✏️ Mode 1 — Whiteboard

Draw on screen using hand gestures. The drawing persists on a canvas overlaid on the camera feed.

### Sub-options
- **Red, Blue, Yellow, Green** — select brush color
- **Eraser** — erase parts of the drawing

### Gestures
| Gesture | Action |
|---|---|
| Right hand index finger only | Draw on canvas |
| Right hand index + middle finger up | Lift pen (move without drawing) |
| Left hand thumb + index pinch distance | Control brush thickness (stabilizes after ~1 second) |
| Right hand closed fist + left hand open (all 5 fingers) | Fill entire canvas with selected color / erase all |

---

## 🖱️ Mode 2 — Air Mouse

Control your computer's mouse cursor using hand gestures. Maps your hand position within a control zone to screen coordinates.

### Gestures
| Gesture | Action |
|---|---|
| Index finger only | Move cursor |
| Pinch (thumb + index) | Left click |
| Index + middle fingers up | Right click |
| Index + middle + ring fingers up, move up/down | Scroll |

> The control zone has a 100px margin on all sides of the camera frame.

---

## 🧊 Mode 3 — 3D Shapes

Render and interact with 3D wireframe models.

### Sub-options

#### Cube — Voxel Editor
Build 3D structures by placing and extending cubes using hand gestures.

| Gesture | Action |
|---|---|
| Single hand pinch | Place the first cube at center |
| Index + middle cursor hover over a cube | Select that cube (green = right hand anchor, orange = left hand anchor) |
| Both hands pinching, move extender hand away | Extend cubes in that direction |
| Both hands pinching, move extender hand closer | Remove cubes |
| Release either pinch | Lock in the extended cubes |
| Index finger only, move hand | Rotate the entire structure |

> Only X (left/right) and Y (up/down) axis extension is supported.  
> The hand that selects a cube becomes the anchor. The other hand is the extender.

#### Sphere
Displays a mathematically generated UV sphere wireframe.

| Gesture | Action |
|---|---|
| Index finger only | Rotate sphere |
| Both hands open, move apart/together | Scale sphere |
| Both hands open, move together | Translate sphere |

#### Import
Load a Blockbench `.json` model file and render it as a 3D wireframe.

| Gesture | Action |
|---|---|
| (File dialog opens automatically) | Select a `.json` Blockbench model |
| Index finger only | Rotate model |
| Both hands open, move apart/together | Scale model |
| Both hands open, move together | Translate model |

---

## 🛠️ Built With

- [Python 3.10+](https://www.python.org/)
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://developers.google.com/mediapipe)
- [PyAutoGUI](https://pyautogui.readthedocs.io/)
- [Pillow](https://pillow.readthedocs.io/)
- [NumPy](https://numpy.org/)
