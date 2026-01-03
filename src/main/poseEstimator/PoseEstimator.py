import math

from src.main.VisionObject import VisionObject
from src.main.poseEstimator.CameraProperties import CameraProperties
from src.main.poseEstimator.LiDARManager import LiDARManager
from src.main.util.Logger import Logger
from src.main.util.Util import Util


class PoseEstimator:
    def __init__(self, rCameraProps: CameraProperties, lCameraProps: CameraProperties, lidarDevice: str, logger: Logger):
        """Estimates the position of given VisionObjects"""

        self.logger = logger

        self.rCameraProps = rCameraProps
        self.lCameraProps = lCameraProps
        self.baseline = abs(self.rCameraProps.x - self.lCameraProps.x)
        self.logger.trace(f"Baseline: {self.baseline}")
        
        # Camera constants
        self.lfx = self.lCameraProps.calibrationMatrix[0][0]
        self.lfy = self.lCameraProps.calibrationMatrix[1][1]
        self.lox = self.lCameraProps.calibrationMatrix[0][2]
        self.loy = self.lCameraProps.calibrationMatrix[1][2]
        
        self.rfx = self.rCameraProps.calibrationMatrix[0][0]
        self.rfy = self.rCameraProps.calibrationMatrix[1][1]
        self.rox = self.rCameraProps.calibrationMatrix[0][2]
        self.roy = self.rCameraProps.calibrationMatrix[1][2]


        # Init LiDARManager
        self.liDARManager = LiDARManager(lidarDevice, self.logger.getChild("LiDARManager"))

    def estimate(self, lObject: VisionObject, rObject: VisionObject):
        """Returns the estimated position of the VisionObject in 3d space"""

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
            (ur - self.rox) / self.rfx,
            (vr - self.roy) / self.rfy
        )

        # 0 -> 1 space
        lNormalizedCoords = (
            (ul - self.lox) / self.lfx,
            (vl - self.loy) / self.lfy
        )

        # Determine the angle of this object in each camera (used for determining if lidar can be used)
        # This is not a great way of doing this
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
            self.logger.warn("Lidar latest measurement is 'None'")
            shouldUseLiDAR = False

        self.logger.trace(f"ShouldUseLiDAR: {shouldUseLiDAR}")
        if (shouldUseLiDAR):
            # z = b*fx / disparity
            # disparity = b*fx / z
            dist = measurement.getDistAtAngle(avgHorizAngle)
            self.logger.trace(f"Lidar Dist: {Util.metersToInches(dist)}")
            # Use lidar for depth measurement
            z = dist * math.cos(math.radians(avgHorizAngle))
            disparity = self.baseline * self.lfx / z
        else:
            # Fall back on stereo cameras
            z = (self.baseline * self.lfx) / disparity

        # Calculate x, y coords
        x = (self.baseline * (ul - self.lox)) / disparity
        y = -(self.baseline * self.lfx * (vl - self.loy)) / (self.lfy * disparity)

        # Offset the coords to put them in world system space (instead of left camera space)
        x = x + self.lCameraProps.x
        y = y + self.lCameraProps.y
        z = z + self.lCameraProps.z

        return (x, y, z)
