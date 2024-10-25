
# Speed limit sign
class SpeedLimitSign(PoseObject):
    def __init__(self, x: float, y: float, z: float, objectType: VisionObjectType, speed: int):
        super().__init__(x, y, z, objectType)
        self.speed = speed
