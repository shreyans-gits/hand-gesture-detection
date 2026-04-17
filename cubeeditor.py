import cv2
import numpy as np
import math
from HandTracker import INDEX, THUMB, MIDDLE, PINKY, RING

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

        self.selectedCube = None

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
                color = (255, 255, 255)
                if cube == self.selectedCube:
                    color = (0, 255, 0)  # green highlight

                if cube in self.tempCubes:
                    color = (0, 0, 255)  # red preview

                cv2.line(img, p1, p2, color, 2)
        return img
    
    def projectPoint(self, point):
        Rx = self.getRotationX(self.angleX)
        Ry = self.getRotationY(self.angleY)

        p = np.array(point)
        p = Ry @ (Rx @ p)

        px = int(p[0] * self.scale + self.centerX)
        py = int(-p[1] * self.scale + self.centerY)

        return (px, py)

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

        cursor = None
        if rightHand:
            cursor = rightHand.selectionCursor()

        if cursor and self.state == "PLACED" and len(self.cubes) > 0:
            minDist = float("inf")
            closestCube = None

            for cube in self.cubes:
                gx, gy, gz = cube

                # cube center (important!)
                cx = gx + 0.5
                cy = gy + 0.5
                cz = gz + 0.5

                px, py = self.projectPoint((cx, cy, cz))

                dist = math.hypot(cursor[0] - px, cursor[1] - py)

                if dist < minDist:
                    minDist = dist
                    closestCube = cube

            # selection threshold
            if minDist < 50:
                self.selectedCube = closestCube
        


        if (
            self.state == "PLACED"
            and rightHand is not None
            and leftHand is not None
            and rightHand.isPinching()
            and leftHand.isPinching()
        ):
            self.state = "EXTENDING"
            if self.selectedCube:
                self.extendBase = self.selectedCube
            else:
                self.extendBase = self.cubes[-1]
            self.tempCubes = []

            # decide extender
            if self.anchorHand == "Right":
                extender = leftHand
            else:
                extender = rightHand

            if extender is not None:
                self.baseExtendPos = extender.center()
                print("Entered EXTENDING")
            else:
                print("Extender is None (skipping)")

        if self.state == "EXTENDING":
            if self.anchorHand == "Right" and leftHand is not None:
                extender = leftHand
            elif self.anchorHand == "Left" and rightHand is not None:
                extender = rightHand
            else:
                return img

            cx, cy = extender.center()
            bx, by = self.baseExtendPos
            
            dx = cx - bx
            dy = cy - by

            deadzone = 15  # pixels

            if self.extendAxis is None:
                if abs(dx) < deadzone and abs(dy) < deadzone:
                    return img  # ignore tiny movement

                if abs(dx) > abs(dy):
                    self.extendAxis = "X"
                    self.extendDir = 1 if dx > 0 else -1
                else:
                    self.extendAxis = "Y"
                    self.extendDir = -1 if dy > 0 else 1

            print("dx:", dx, "dy:", dy, "axis:", self.extendAxis)

            threshold = 30
            if self.extendAxis == "X":
                distance = abs(dx)
            else:
                distance = abs(dy)
            count = max(0, int(distance / threshold))

            self.tempCubes = []
            gx, gy, gz = self.extendBase

            for i in range(1, count + 1):
                if self.extendAxis == "X":
                    newCube = (gx + i * self.extendDir, gy, gz)
                else:
                    newCube = (gx, gy + i * self.extendDir, gz)

                self.tempCubes.append(newCube)
            
            if not (rightHand and leftHand and rightHand.isPinching() and leftHand.isPinching()):
                self.cubes += self.tempCubes
                self.tempCubes = []

                self.extendAxis = None
                self.extendDir = None
                self.baseExtendPos = None

                self.state = "PLACED"

        if rightHand and rightHand.isFingerUp(INDEX) and not rightHand.isFingerUp(THUMB) and not rightHand.isFingerUp(MIDDLE) and not rightHand.isFingerUp(RING) and not rightHand.isFingerUp(PINKY) and not rightHand.isPinching() and self.state == "PLACED":
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