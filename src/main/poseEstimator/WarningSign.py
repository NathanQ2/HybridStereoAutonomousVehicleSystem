from src.main.ObjectType import ObjectType
from src.main.poseEstimator.PoseObject import PoseObject


class WarningSign(PoseObject):
    def __init__(self, x: float, y: float, z: float):
        super().__init__(x, y, z, ObjectType.Warning)
