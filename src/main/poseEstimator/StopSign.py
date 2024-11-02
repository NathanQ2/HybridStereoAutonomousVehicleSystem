import struct
from ObjectType import ObjectType
from poseEstimator.PoseObject import PoseObject


class StopSign(PoseObject):
    def __init__(self, x: float, y: float, z: float):
        super().__init__(x, y, z, ObjectType.StopSign)
