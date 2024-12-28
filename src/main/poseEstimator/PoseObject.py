import struct

from src.main.VisionObject import VisionObject
from src.main.ObjectType import ObjectType


class PoseObject:
    """Represents an object in 3d space"""
    def __init__(self, x: float, y: float, z: float, objectType: ObjectType):
        self.x = x
        self.y = y
        self.z = z
        self.type = objectType
