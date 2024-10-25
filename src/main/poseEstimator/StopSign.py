
class StopSign(PoseObject):
    def __init__(self, x: float, y: float, z: float):
        super().__init__(x, y, z, VisionObjectType.StopSign)
