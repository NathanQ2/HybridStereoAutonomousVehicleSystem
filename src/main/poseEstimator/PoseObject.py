from VisionObject import VisionObject
from ObjectType import ObjectType
import struct


class PoseObject:
    """Represents an object in 3d space"""
    def __init__(self, x: float, y: float, z: float, objectType: ObjectType):
        self.x = x
        self.y = y
        self.z = z
        self.type = objectType
