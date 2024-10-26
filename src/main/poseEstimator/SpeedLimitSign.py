from poseEstimator.PoseObject import PoseObject
from VisionObject import VisionObjectType


# Speed limit sign
class SpeedLimitSign(PoseObject):
    def __init__(self, x: float, y: float, z: float, speed: int):
        super().__init__(x, y, z, VisionObjectType.Regulatory)
        self.speed = speed
