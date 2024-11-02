from poseEstimator.PoseObject import PoseObject
from VisionObject import VisionObject
from ObjectType import ObjectType


class WarningSign(PoseObject):
    def __init__(self, x: float, y: float, z: float):
        super().__init__(x, y, z, ObjectType.Warning)
