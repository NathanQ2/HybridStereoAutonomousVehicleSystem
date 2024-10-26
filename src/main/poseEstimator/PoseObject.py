from VisionObject import VisionObject, VisionObjectType


# Represents object that has had its pose estimated
class PoseObject:
    def __init__(self, x: float, y: float, z: float, objectType: VisionObjectType):
        self.x = x
        self.y = y
        self.z = z
        self.objectType = objectType
