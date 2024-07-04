import cv2 as cv


class CameraProperties:
    def __init__(self, name: str, width: int, height: int, hfov: float, x: float, y: float, z: float, calibrationMatrix: cv.Mat[3, 3],
                 distortionCoefficients: cv.Mat[1, 5]):
        self.name = name
        self.width = width
        self.height = height
        self.hfov = hfov
        self.x = x
        self.y = y
        self.z = z

        self.calibrationMatrix = calibrationMatrix
        self.distortionCoefficients = distortionCoefficients
