from src.main.poseEstimator.PoseObject import PoseObject
from src.main.VisionObject import VisionObject
from src.main.ObjectType import ObjectType


class WarningSign(PoseObject):
    def __init__(self, x: float, y: float, z: float):
        super().__init__(x, y, z, ObjectType.Warning)
