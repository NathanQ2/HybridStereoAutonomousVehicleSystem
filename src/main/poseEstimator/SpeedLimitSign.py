from poseEstimator.PoseObject import PoseObject
from ObjectType import ObjectType


# Speed limit sign
class SpeedLimitSign(PoseObject):
    """Represents a speed limit sign"""
    def __init__(self, x: float, y: float, z: float, speed: int):
        super().__init__(x, y, z, ObjectType.Regulatory)
        self.speed = speed
