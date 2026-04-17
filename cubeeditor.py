import cv2
import numpy as np
import math
from HandTracker import INDEX

class CubeEditor:
    def __init__(self, screenW, screenH):
        self.screenW = screenW
        self.screenH = screenH

        self.cubes = []     # list of (gx, gy, gz)
        self.tempCubes = []     
        self.anchorHand = None   # "Right" or "Left"
        self.state = "IDLE"
        self.extendAxis = None   # "X" or "Y"
        self.extendDir = None    # +1 or -1
        self.extendBase = None   # (gx, gy, gz) cube being extended from
        self.baseExtendPos = None # screen pos when extending started

        self.angleX = 0
        self.angleY = 0
        self.scale = 50
        self.centerX = screenW // 2
        self.centerY = screenH // 2

        self.prevHandPos = None
        self.prevDist = None

    def getRotationX(self, angle):
        return np.array([
            [1,0,0],
            [0,np.cos(angle),-np.sin(angle)],
            [0,np.sin(angle), np.cos(angle)]
        ])

    def getRotationY(self, angle):
        return np.array([
            [np.cos(angle),0,np.sin(angle)],
            [0,1,0],
            [-np.sin(angle),0,np.cos(angle)]
        ])

    def renderCubes(self, img):
        allCubes = self.cubes + self.tempCubes
        Rx = self.getRotationX(self.angleX)
        Ry = self.getRotationY(self.angleY)
        
        for cube in allCubes:
            gx, gy, gz = cube
            offsets = [
                (0,0,0),(1,0,0),(1,1,0),(0,1,0),
                (0,0,1),(1,0,1),(1,1,1),(0,1,1)
            ]
            vertices = [
                [gx + ox, gy + oy, gz + oz]
                for ox, oy, oz in offsets
            ]
            projected = []
            for v in vertices:
                point = np.array(v)
                rotated = Ry @ (Rx @ point)
                px = int(rotated[0] * self.scale + self.centerX)
                py = int(-rotated[1] * self.scale + self.centerY)
                projected.append((px, py))

            edges = [
                (0,1),(1,2),(2,3),(3,0),
                (4,5),(5,6),(6,7),(7,4),
                (0,4),(1,5),(2,6),(3,7)
            ]
            for edge in edges:
                p1 = projected[edge[0]]
                p2 = projected[edge[1]]
                cv2.line(img, p1, p2, (255,255,255), 2)
        return img

    def update(self, img, rightHand, leftHand):
        if self.state == "IDLE":
            if rightHand and rightHand.isPinching():
                self.cubes.append((0, 0, 0))
                self.anchorHand = "Right"
                self.state = "PLACED"

            elif leftHand and leftHand.isPinching():
                self.cubes.append((0, 0, 0))
                self.anchorHand = "Left"
                self.state = "PLACED"

        if (
            self.state == "PLACED"
            and rightHand is not None
            and leftHand is not None
            and rightHand.isPinching()
            and leftHand.isPinching()
        ):
            self.state = "EXTENDING"
            self.extendBase = self.cubes[-1]
            self.tempCubes = []

            # decide extender
            if self.anchorHand == "Right":
                extender = leftHand
            else:
                extender = rightHand

            print("Right:", rightHand)
            print("Left:", leftHand)
            print("Anchor:", self.anchorHand)
            
            # SAFETY CHECK
            if extender is not None:
                self.baseExtendPos = extender.center()
                print("Entered EXTENDING")
            else:
                print("Extender is None (skipping)")

        if rightHand and rightHand.isFingerUp(INDEX) and not rightHand.isPinching() and self.state == "PLACED":
            cx, cy = rightHand.center()

            if self.prevHandPos:
                dx = cx - self.prevHandPos[0]
                dy = cy - self.prevHandPos[1]

                self.angleY += dx * 0.01
                self.angleX += dy * 0.01

            self.prevHandPos = (cx, cy)
        else:
            self.prevHandPos = None
        img = self.renderCubes(img)
        return img