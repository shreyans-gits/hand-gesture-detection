import cv2
import numpy as np
import json
import math
from HandTracker import INDEX, GestureTracker
from tkinter import Tk, filedialog
from cubeeditor import CubeEditor

class Shapes3D:
    def __init__(self, screenW, screenH):
        self.screenW = screenW
        self.screenH = screenH

        self.model = None
        self.vertices = []
        self.edges = []
        self.angleX = 0
        self.angleY = 0
        self.scale = 50

        self.centerX = screenW // 2
        self.centerY = screenH // 2

        self.prevHandPos = None
        self.prevDist = None
        self.prevMovePos = None
        self.currentSubOption = -1
        self.cubeeditor = CubeEditor(screenW, screenH)

    def loadModel(self, filepath):
        if filepath.lower().endswith('.json'):
            self.loadBlockbenchJson(filepath)
        elif filepath.lower().endswith('.obj'):
            self.loadObjMesh(filepath)
            
        self.centerModel()

    def loadBlockbenchJson(self, filepath):
        with open(filepath, 'r') as f:
            self.model = json.load(f)

        self.vertices = []
        self.edges = []

        for element in self.model["elements"]:
            x1, y1, z1 = element["from"]
            x2, y2, z2 = element["to"]

            corners = [
                (x1,y1,z1),(x2,y1,z1),(x1,y2,z1),(x2,y2,z1),
                (x1,y1,z2),(x2,y1,z2),(x1,y2,z2),(x2,y2,z2)
            ]

            if "rotation" in element:
                rot = element["rotation"]
                angle = math.radians(rot["angle"])
                axis = rot["axis"]
                ox, oy, oz = rot["origin"]
                corners = [self.rotatePoint(p, angle, axis, (ox,oy,oz)) for p in corners]

            startIndex = len(self.vertices)
            self.vertices.extend(corners)

            box_edges = [
                (0,1),(1,3),(3,2),(2,0),
                (4,5),(5,7),(7,6),(6,4),
                (0,4),(1,5),(2,6),(3,7)
            ]
            for e in box_edges:
                self.edges.append((startIndex+e[0], startIndex+e[1]))

    def loadObjMesh(self, filepath):
        self.vertices = []
        self.edges = []
        unique_edges = set()

        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                prefix = parts[0]

                if prefix == 'v':
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    self.vertices.append((x, y, z))
                
                elif prefix == 'f':
                    indices = []
                    for part in parts[1:]:
                        idx = int(part.split('/')[0])
                        idx = idx - 1 if idx > 0 else len(self.vertices) + idx
                        indices.append(idx)
                    
                    num_v = len(indices)
                    for i in range(num_v):
                        v1 = indices[i]
                        v2 = indices[(i + 1) % num_v]
                        edge_pair = (min(v1, v2), max(v1, v2))
                        if edge_pair not in unique_edges:
                            unique_edges.add(edge_pair)
                            self.edges.append(edge_pair)

    def centerModel(self):
        if not self.vertices:
            return
        verts = np.array(self.vertices)
        center = verts.mean(axis=0)
        self.vertices = [tuple(v - center) for v in verts]

    def rotatePoint(self, point, angle, axis, origin):
        x,y,z = point
        ox,oy,oz = origin

        x -= ox; y -= oy; z -= oz

        if axis == "x":
            y,z = y*np.cos(angle)-z*np.sin(angle), y*np.sin(angle)+z*np.cos(angle)
        elif axis == "y":
            x,z = x*np.cos(angle)+z*np.sin(angle), -x*np.sin(angle)+z*np.cos(angle)
        elif axis == "z":
            x,y = x*np.cos(angle)-y*np.sin(angle), x*np.sin(angle)+y*np.cos(angle)

        return (x+ox, y+oy, z+oz)

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

    def project(self, point):
        p = np.array(point)
        p = self.getRotationY(self.angleY) @ p
        p = self.getRotationX(self.angleX) @ p
        p = p * self.scale
        x = int(p[0] + self.centerX)
        y = int(-p[1] + self.centerY)

        return (x,y)
    
    def openFileDialog(self):
        root = Tk()
        root.withdraw()

        filepath = filedialog.askopenfilename(
            title="Select 3D Asset File (.json / .obj)",
            filetypes=[("3D Files", "*.json *.obj"), ("Blockbench JSON", "*.json"), ("Wavefront OBJ", "*.obj")]
        )

        root.destroy()
        return filepath

    def update(self, img, rightHand, leftHand, currentSubOption):
        if currentSubOption != self.currentSubOption:
            self.vertices = []
            self.edges = []
            self.angleX = 0
            self.angleY = 0
            self.scale = 50
            self.centerX = self.screenW // 2
            self.centerY = self.screenH // 2
            self.currentSubOption = currentSubOption

        if currentSubOption == 0 and not self.vertices:
            img = self.cubeeditor.update(img, rightHand, leftHand)
            return img
        
        if currentSubOption == 1 and not self.vertices:
            self.vertices = []
            self.edges = []

            radius = 1
            stacks = 12
            slices = 24

            for i in range(stacks + 1):
                theta = np.pi * i / stacks

                for j in range(slices):
                    phi = 2 * np.pi * j / slices

                    x = radius * np.sin(theta) * np.cos(phi)
                    y = radius * np.cos(theta)
                    z = radius * np.sin(theta) * np.sin(phi)

                    self.vertices.append((x, y, z))

            for i in range(stacks + 1):
                for j in range(slices):

                    current = i * slices + j
                    next_slice = i * slices + (j + 1) % slices

                    self.edges.append((current, next_slice))

                    if i < stacks:
                        next_stack = (i + 1) * slices + j
                        self.edges.append((current, next_stack))
        
        if currentSubOption == 2 and not self.vertices:
            filepath = self.openFileDialog()

            if filepath:
                self.loadModel(filepath)
                self.scale = 20

        if rightHand and rightHand.isFingerUp(INDEX) and sum(rightHand.fingersUp()) == 1 and not rightHand.isPinching():
            cx, cy = rightHand.center()

            if self.prevHandPos:
                dx = cx - self.prevHandPos[0]
                dy = cy - self.prevHandPos[1]

                self.angleY += dx * 0.01
                self.angleX += dy * 0.01

            self.prevHandPos = (cx, cy)
        else:
            self.prevHandPos = None

        if rightHand and rightHand.isPinching():
            cx, cy = rightHand.center()

            if self.prevMovePos:
                dx = cx - self.prevMovePos[0]
                dy = cy - self.prevMovePos[1]

                self.centerX += dx * 0.8
                self.centerY += dy * 0.8

            self.prevMovePos = (cx, cy)

        elif rightHand and leftHand:
            cx1, cy1 = rightHand.center()
            cx2, cy2 = leftHand.center()

            dist = math.hypot(cx2-cx1, cy2-cy1)

            if self.prevDist:
                self.scale += (dist - self.prevDist) * 0.01
                self.scale = max(2, min(self.scale, 200))

            self.prevDist = dist

        else:
            self.prevDist = None
            self.prevMovePos = None

        for edge in self.edges:
            p1 = self.project(self.vertices[edge[0]])
            p2 = self.project(self.vertices[edge[1]])

            cv2.line(img, p1, p2, (255,255,255), 2)

        return img