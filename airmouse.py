import pyautogui
import cv2
import numpy as np
from HandTracker import INDEX, MIDDLE, RING
import time
from collections import deque

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

class AirMouse:
    def __init__(self, camW, camH):
        self.camW = camW
        self.camH = camH
        self.screenW, self.screenH = pyautogui.size()
        self.lastClickTime = 0
        self.clickCooldown = 0.5
        self.scrollHistory = deque(maxlen=5)
        self.margin = 100
        self.smoothX, self.smoothY = 0, 0
        self.smoothening = 7
        self.padding = 50
        
    def update(self, img, rightHand):
        if rightHand:
            fingers = rightHand.fingersUp()
            x1, y1 = rightHand.points[8]
            self.scrollHistory.append((x1, y1))
            screenX = np.interp(x1, [self.margin, self.camW - self.margin], [0, self.screenW])
            screenY = np.interp(y1, [self.margin, self.camH - self.margin], [0, self.screenH])

            if fingers[INDEX] == 1 and fingers[MIDDLE] == 0 and fingers[RING] == 0:
                self.smoothX = self.smoothX + (screenX - self.smoothX) / self.smoothening
                self.smoothY = self.smoothY + (screenY - self.smoothY) / self.smoothening
                self.smoothX = max(0, min(self.screenW, self.smoothX))
                self.smoothY = max(0, min(self.screenH, self.smoothY))
                pyautogui.moveTo(self.smoothX, self.smoothY)

            if fingers[INDEX] == 1 and fingers[MIDDLE] == 1 and fingers[RING] == 0:
                if time.time() - self.lastClickTime > self.clickCooldown:
                    pyautogui.rightClick(self.smoothX, self.smoothY)
                    self.lastClickTime = time.time()

            if rightHand.isPinching():
                if time.time() - self.lastClickTime > self.clickCooldown:
                    pyautogui.click(self.smoothX, self.smoothY)
                    self.lastClickTime = time.time()

            if fingers[INDEX] == 1 and fingers[MIDDLE] == 1 and fingers[RING] == 1:
                if len(self.scrollHistory) >= 2:
                    diff = self.scrollHistory[-1][1] - self.scrollHistory[-2][1]
                    pyautogui.scroll(-int(diff / 5)*50)
        
        return img