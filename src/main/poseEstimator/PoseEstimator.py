import cv2 as cv
from ultralytics import YOLO
from ultralytics.engine.results import Results
import math

from poseEstimator.CameraProperties import CameraProperties

from src.main.util.Util import Util


class PoseEstimator:
    def __init__(self, rCameraProps: CameraProperties, lCameraProps: CameraProperties):
        self.rCameraProps = rCameraProps
        self.lCameraProps = lCameraProps
        self.baseline = abs(self.rCameraProps.x - self.lCameraProps.x)
        print(f"Baseline: {self.baseline}")

    def update(self, rFrame: cv.Mat, lFrame: cv.Mat, rResults: list[Results], lResults: list[Results]):
        rBoxes = rResults[0].boxes.xywh
        lBoxes = lResults[0].boxes.xywh

        rBox = rBoxes[0]
        lBox = lBoxes[0]

        ur = rBox[0]
        vr = rBox[1]
        ul = lBox[0]
        vl = lBox[1]
        disparity = abs(ul - ur)

        # x = (b(ul - ox)) / disparity
        # y = (b*fx(vl - oy)) / (fy*disparity)
        # z = b*fx / disparity

        x = (self.baseline * (ul - self.lCameraProps.calibrationMatrix[0][2])) / disparity
        y = -(self.baseline * self.lCameraProps.calibrationMatrix[0][0] * (vl - self.lCameraProps.calibrationMatrix[1][2])) / (self.lCameraProps.calibrationMatrix[1][1] * disparity)
        z = (self.baseline * self.lCameraProps.calibrationMatrix[0][0]) / disparity

        x = x + self.lCameraProps.x
        y = y + self.lCameraProps.y
        z = z + self.lCameraProps.z

        return (x, y, z)
