import cv2 as cv
from ultralytics import YOLO
from ultralytics.engine.results import Results
import math

from poseEstimator.CameraProperties import CameraProperties
from poseEstimator.LiDARManager import LiDARManager, LiDARMeasurement

from util.Util import Util


class PoseEstimator:
    def __init__(self, rCameraProps: CameraProperties, lCameraProps: CameraProperties):
        self.rCameraProps = rCameraProps
        self.lCameraProps = lCameraProps
        self.baseline = abs(self.rCameraProps.x - self.lCameraProps.x)
        self.liDARManager = LiDARManager()
        print(f"Baseline: {self.baseline}")

    def update(self, rFrame: cv.Mat, lFrame: cv.Mat, rResults: list[Results], lResults: list[Results]):
        shouldUseLiDAR = False
        # print(f"LiDAR Timestamp: {measurement.timestamp}")
        rBoxes = rResults[0].boxes.xywh
        lBoxes = lResults[0].boxes.xywh

        rBox = rBoxes[0]
        lBox = lBoxes[0]

        ur = rBox[0]
        vr = rBox[1]
        ul = lBox[0]
        vl = lBox[1]
        disparity = abs(ul - ur)

        rVertFOV = self.rCameraProps.hfov * (480 / 640)
        # Frame is undistorted, so this should be accurate enough??
        rVertAngle = -((vr - (480 / 2)) / 480 * rVertFOV)
        rHorizAngle = (ur - (640 / 2)) / 640 * self.rCameraProps.hfov
        lHorizAngle = (ul - (640 / 2)) / 640 * self.lCameraProps.hfov
        print(f"rVertAngle: {rVertAngle}, rHorizAngle: {rHorizAngle}")

        if (-10 < rVertAngle < 10 and -15.5 < rHorizAngle < 13):
            shouldUseLiDAR = True

        print(f"ShouldUseLiDAR: {shouldUseLiDAR}")

        # x = (b(ul - ox)) / disparity
        # y = (b*fx(vl - oy)) / (fy*disparity)
        # z = b*fx / disparity

        # Override disparity if we want to use lidar
        if (shouldUseLiDAR):
            # Rough estimate abt where sign should be
            desiredAngle = (rHorizAngle + lHorizAngle) / 2
            # z = b*fx / disparity
            # disparity = b*fx / z
            measurement = self.liDARManager.getLatest()
            z = measurement.getDistAtAngle(desiredAngle)
            disparity = self.baseline * self.lCameraProps.calibrationMatrix[0][0] / z
        else:
            z = (self.baseline * self.lCameraProps.calibrationMatrix[0][0]) / disparity
        x = (self.baseline * (ul - self.lCameraProps.calibrationMatrix[0][2])) / disparity
        y = -(self.baseline * self.lCameraProps.calibrationMatrix[0][0] * (vl - self.lCameraProps.calibrationMatrix[1][2])) / (self.lCameraProps.calibrationMatrix[1][1] * disparity)


        x = x + self.lCameraProps.x
        y = y + self.lCameraProps.y
        z = z + self.lCameraProps.z

        return (x, y, z)
