import cv2 as cv
from ultralytics import YOLO
from ultralytics.engine.results import Results
import math

from poseEstimator.CameraProperties import CameraProperties
from poseEstimator.LiDARManager import LiDARManager, LiDARMeasurement

from util.Util import Util

from src.main.VisionObject import VisionObject


class PoseEstimator:
    def __init__(self, rCameraProps: CameraProperties, lCameraProps: CameraProperties, lidarDevice: str):
        self.rCameraProps = rCameraProps
        self.lCameraProps = lCameraProps
        self.baseline = abs(self.rCameraProps.x - self.lCameraProps.x)
        self.liDARManager = LiDARManager(lidarDevice)
        self.previousTimestamp = 0.0
        print(f"Baseline: {self.baseline}")

    def getPoseFromObject(self, lObject: VisionObject, rObject: VisionObject):
        shouldUseLiDAR = False
        # print(f"LiDAR Timestamp: {measurement.timestamp}")

        ur = rObject.x
        vr = rObject.y
        ul = lObject.x
        vl = lObject.y

        disparity = abs(ul - ur)

        rNormalizedCoords = (
            (ur - self.rCameraProps.calibrationMatrix[0][2]) / self.rCameraProps.calibrationMatrix[0][0],
            (vr - self.rCameraProps.calibrationMatrix[1][2]) / self.rCameraProps.calibrationMatrix[1][1]
        )

        lNormalizedCoords = (
            (ul - self.lCameraProps.calibrationMatrix[0][2]) / self.lCameraProps.calibrationMatrix[0][0],
            (vl - self.lCameraProps.calibrationMatrix[1][2]) / self.lCameraProps.calibrationMatrix[1][1]
        )

        rVertAngle = math.degrees(math.atan(-rNormalizedCoords[1]))
        rHorizAngle = math.degrees(math.atan(rNormalizedCoords[0]))
        lHorizAngle = math.degrees(math.atan(lNormalizedCoords[0]))
        avgHorizAngle = (rHorizAngle + lHorizAngle) / 2
        # print(f"rVertAngle: {rVertAngle}, rHorizAngle: {rHorizAngle}, lHorizAngle: {lHorizAngle}, avgHoriz: {(rHorizAngle + lHorizAngle) / 2}")

        if (-10 < rVertAngle < 10 and -19.2 < avgHorizAngle < 19.2):
            shouldUseLiDAR = True


        # STEREO FORMULAS
        # x = (b(ul - ox)) / disparity
        # y = (b*fx(vl - oy)) / (fy*disparity)
        # z = b*fx / disparity

        # Override disparity if we want to use lidar
        measurement = self.liDARManager.getLatest()
        # z = b*fx / disparity
        # disparity = b*fx / z
        lidarZ = measurement.getDistAtAngle(avgHorizAngle)
        print(f"Lidar Z: {Util.metersToInches(lidarZ)}")
        # Since lidar is pretty buggy, if we get a measurement from (0, 2.54), assume the data is trash
        if (lidarZ == 0 or lidarZ >= 2.54):
            shouldUseLiDAR = False

        print(f"ShouldUseLiDAR: {shouldUseLiDAR}")
        if (shouldUseLiDAR):
            # Use lidar for depth measurement
            z = lidarZ
            disparity = self.baseline * self.lCameraProps.calibrationMatrix[0][0] / z
        else:
            # Fall back on stereo cameras
            z = (self.baseline * self.lCameraProps.calibrationMatrix[0][0]) / disparity

        # Calculate x, y, and z
        x = (self.baseline * (ul - self.lCameraProps.calibrationMatrix[0][2])) / disparity
        y = -(self.baseline * self.lCameraProps.calibrationMatrix[0][0] * (
                vl - self.lCameraProps.calibrationMatrix[1][2])) / (
                    self.lCameraProps.calibrationMatrix[1][1] * disparity)

        x = x + self.lCameraProps.x
        y = y + self.lCameraProps.y
        z = z + self.lCameraProps.z

        return (x, y, z)

    def estimate(self, lObject: VisionObject, rObject: VisionObject):
        return self.getPoseFromObject(lObject, rObject)
