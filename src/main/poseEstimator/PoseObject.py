from VisionObject import VisionObject
from ObjectType import ObjectType
import struct


# Represents object that has had its pose estimated
class PoseObject:
    def __init__(self, x: float, y: float, z: float, objectType: ObjectType):
        self.x = x
        self.y = y
        self.z = z
        self.type = objectType