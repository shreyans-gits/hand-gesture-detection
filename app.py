import cv2
from HandTracker import HandDetector, GestureTracker, THUMB, INDEX, MIDDLE, RING, PINKY
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import time

# Screen and app state
SCREEN_W, SCREEN_H = 1280, 720
FONT_PATH = "GUI/open_sans.ttf"
notification = ""
notificationTimer = 0

# Mode management
modes = ["Whiteboard", "Air Mouse", "3D Shapes"]
subOptions = {
    "Whiteboard": ["Red", "Green", "Blue", "Yellow", "White", "Eraser"],
    "Air Mouse": [],
    "3D Shapes": ["Sphere", "Cube"]
}

currentMode = 0
currentSubOption = 0
PANEL_W = 160
PANEL_TAB_W = 20
BUTTON_H = 85
BUTTON_PADDING = 40

panelOpen = False
panelX = SCREEN_W - PANEL_TAB_W  # starts as just the tab

#GUI 
panelImgs = [
    cv2.imread("GUI/panel0.png"),
    cv2.imread("GUI/panel1.png"),
    cv2.imread("GUI/panel2.png")
]

# Scale down from 2x to 1x
panelImgs = [cv2.resize(img, (PANEL_W, SCREEN_H)) for img in panelImgs]

# Initialize
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_H)
SCREEN_W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
SCREEN_H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

detector = HandDetector(maxHands=2)

gestureTrackerR = GestureTracker()
gestureTrackerL = GestureTracker()

def drawText(img, text, pos, fontPath, fontSize, color=(255, 255, 255)):
    imgPil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(imgPil)
    font = ImageFont.truetype(fontPath, fontSize)
    
    # Calculate text width for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    textW = bbox[2] - bbox[0]
    x = pos[0] - textW // 2
    y = pos[1]
    
    draw.text((x, y), text, font=font, fill=(color[2], color[1], color[0]))
    return cv2.cvtColor(np.array(imgPil), cv2.COLOR_RGB2BGR)

def drawPanel(img, panelOpen, currentMode, modes, panelImgs, hoveredBtn=-1):
    h, w = SCREEN_H, SCREEN_W
    buttons = []
    if panelOpen:
        panelX = w - PANEL_W
        panelImg = panelImgs[currentMode]
        overlay = img.copy()
        overlay[0:h, panelX:panelX + PANEL_W] = panelImg
        cv2.addWeighted(overlay, 0.90, img, 0.10, 0, img)
    else:
        # Draw tab
        overlay = img.copy()
        cv2.rectangle(overlay, (w - PANEL_TAB_W, h//4), (w, 3*h//4), (30, 30, 30), -1)
        cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
        cv2.putText(img, "<", (w - PANEL_TAB_W + 2, h//2),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    return img

def getButtonRects(modes):
    buttons = []
    totalHeight = len(modes) * BUTTON_H + (len(modes) - 1) * BUTTON_PADDING
    startY = (SCREEN_H - totalHeight) // 2
    for i in range(len(modes)):
        btnY = startY + i * (BUTTON_H + BUTTON_PADDING)
        btnX = SCREEN_W - PANEL_W + 10
        buttons.append((btnX, btnY, SCREEN_W - 10, btnY + BUTTON_H))
    return buttons

hoverTracker = GestureTracker()
buttons = getButtonRects(modes)
while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, draw=True, flip=True)

    rightHand = None
    leftHand = None

    for hand in hands:
        if hand.handedness == "Right":
            rightHand = hand
        else:
            leftHand = hand

    gestureTrackerR.update(rightHand)
    gestureTrackerL.update(leftHand)

    if rightHand:
        swipe = gestureTrackerR.detectSwipe(img.shape)
        if swipe == "LEFT":
            panelOpen = True
        if swipe == "RIGHT":
            panelOpen = False
    else:
        gestureTrackerR.update(None)

    hoveredBtn = -1
    if panelOpen and rightHand:
        cx, cy = rightHand.center()
        cv2.circle(img, (cx, cy), 10, (0, 255, 255), cv2.FILLED)
        
        hovering = False
        for i, (x1, y1, x2, y2) in enumerate(buttons):
            print(f"cx:{cx} cy:{cy} | btn{i}: {x1},{y1},{x2},{y2}")
            if x1 < cx < x2 and y1 < cy < y2:
                hoveredBtn = i
                hovering = True
                result = hoverTracker.detectHover(rightHand)
                if result:
                    currentMode = i
                    panelOpen = False
                    notification = f"Selected: {modes[i]}"
                    notificationTimer = time.time()
                break
        # print(f"hovering: {hovering}")
        if not hovering:
            hoverTracker.detectHover(None)
    img = drawPanel(img, panelOpen, currentMode, modes, panelImgs, hoveredBtn)

    if notification and time.time() - notificationTimer < 1.5:
        img = drawText(img, notification, (SCREEN_W // 2, 30), FONT_PATH, 36)
    cv2.imshow("Gesture Lab", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
detector.detector.close()