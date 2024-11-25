import cv2 as cv
from ultralytics import YOLO
from ultralytics.engine.results import Results
import math
import asyncio

from poseEstimator.CameraProperties import CameraProperties
from poseEstimator.LiDARManager import LiDARManager, LiDARMeasurement

from util.Util import Util

from src.main.VisionObject import VisionObject
from src.main.util.Logger import Logger


class PoseEstimator:
    def __init__(self, rCameraProps: CameraProperties, lCameraProps: CameraProperties, lidarDevice: str):
        """Estimates the position of given VisionObjects"""

        self.logger = Logger("PoseEstimator")

        self.rCameraProps = rCameraProps
        self.lCameraProps = lCameraProps
        self.baseline = abs(self.rCameraProps.x - self.lCameraProps.x)
        self.logger.trace(f"Baseline: {self.baseline}")

        # Init LiDARManager
        self.liDARManager = LiDARManager(lidarDevice)

    def getPoseFromObject(self, lObject: VisionObject, rObject: VisionObject):
        """Estimates the position of the given VisionObject in 3d space"""

        # Use LiDAR for more accurate depth measurements
        shouldUseLiDAR = False

        # Get coordinates of object (in pixel space)
        ur = rObject.x
        vr = rObject.y
        ul = lObject.x
        vl = lObject.y

        disparity = abs(ul - ur)

        # 0 -> 1 space
        rNormalizedCoords = (
            (ur - self.rCameraProps.calibrationMatrix[0][2]) / self.rCameraProps.calibrationMatrix[0][0],
            (vr - self.rCameraProps.calibrationMatrix[1][2]) / self.rCameraProps.calibrationMatrix[1][1]
        )

        # 0 -> 1 space
        lNormalizedCoords = (
            (ul - self.lCameraProps.calibrationMatrix[0][2]) / self.lCameraProps.calibrationMatrix[0][0],
            (vl - self.lCameraProps.calibrationMatrix[1][2]) / self.lCameraProps.calibrationMatrix[1][1]
        )

        # Determine the angle of this object in each camera (used for determining if lidar can be used)
        rVertAngle = math.degrees(math.atan(-rNormalizedCoords[1]))
        rHorizAngle = math.degrees(math.atan(rNormalizedCoords[0]))
        lHorizAngle = math.degrees(math.atan(lNormalizedCoords[0]))
        # Should be close enough to actual angle from lidar -> object
        avgHorizAngle = (rHorizAngle + lHorizAngle) / 2
        self.logger.trace(f"rVertAngle: {rVertAngle}, rHorizAngle: {rHorizAngle}, lHorizAngle: {lHorizAngle}, avgHoriz: {(rHorizAngle + lHorizAngle) / 2}")

        # If the object is within bounds to use lidar
        if (-10 < rVertAngle < 10 and -9.5 < avgHorizAngle < 19.2):
            shouldUseLiDAR = True

        # STEREO FORMULAS
        # x = (b(ul - ox)) / disparity
        # y = (b*fx(vl - oy)) / (fy*disparity)
        # z = b*fx / disparity

        # Get latest measurement from LiDAR
        measurement = self.liDARManager.getLatest()
        if (measurement is None):
            self.logger.warning("Lidar latest measurement is 'None'")
            shouldUseLiDAR = False

        self.logger.trace(f"ShouldUseLiDAR: {shouldUseLiDAR}")
        if (shouldUseLiDAR):
            # z = b*fx / disparity
            # disparity = b*fx / z
            lidarZ = measurement.getDistAtAngle(avgHorizAngle)
            self.logger.trace(f"Lidar Z: {Util.metersToInches(lidarZ)}")
            # Use lidar for depth measurement
            z = lidarZ
            disparity = self.baseline * self.lCameraProps.calibrationMatrix[0][0] / z
        else:
            # Fall back on stereo cameras
            z = (self.baseline * self.lCameraProps.calibrationMatrix[0][0]) / disparity

        # Calculate x, y coords
        x = (self.baseline * (ul - self.lCameraProps.calibrationMatrix[0][2])) / disparity
        y = -(self.baseline * self.lCameraProps.calibrationMatrix[0][0] * (
                vl - self.lCameraProps.calibrationMatrix[1][2])) / (
                    self.lCameraProps.calibrationMatrix[1][1] * disparity)

        # offset the coords to put them in world system space (instead of left camera space)
        x = x + self.lCameraProps.x
        y = y + self.lCameraProps.y
        z = z + self.lCameraProps.z

        return (x, y, z)

    def estimate(self, lObject: VisionObject, rObject: VisionObject):
        """Returns the estimated position of the VisionObject in 3d space"""
        return self.getPoseFromObject(lObject, rObject)
