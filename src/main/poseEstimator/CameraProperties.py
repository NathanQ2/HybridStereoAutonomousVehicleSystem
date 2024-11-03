import cv2 as cv
import json

import numpy as np


class CameraProperties:
    """Represents all the constants of a single camera. Can be loaded from a json file."""

    def __init__(self, name: str, port, widthNative: int, heightNative: int, hfov: float, x: float, y: float, z: float,
                 calibrationMatrix: cv.Mat[3, 3], distortionCoefficients: cv.Mat[1, 5]):
        super().__init__()
        self.name = name
        self.port = port
        self.widthNative = widthNative
        self.heightNative = heightNative
        self.hfov = hfov
        self.x = x
        self.y = y
        self.z = z

        self.calibrationMatrix = calibrationMatrix
        self.distortionCoefficients = distortionCoefficients

    def getAspectRatio(self) -> float:
        """Returns the aspect ratio of this camera"""
        return self.widthNative / self.heightNative

    def asJson(self):
        """Serializes this object to json"""
        d = {
            "name": self.name,
            "port": self.port,
            "widthNative": self.widthNative,
            "heightNative": self.heightNative,
            "hfov": self.hfov,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "calibrationMatrix": [
                [float(self.calibrationMatrix[0][0]), float(self.calibrationMatrix[0][1]), float(self.calibrationMatrix[0][2])],
                [float(self.calibrationMatrix[1][0]), float(self.calibrationMatrix[1][1]), float(self.calibrationMatrix[1][2])],
                [float(self.calibrationMatrix[2][0]), float(self.calibrationMatrix[2][1]), float(self.calibrationMatrix[2][2])]
            ],
            "distortionCoefficients": [
                [float(self.distortionCoefficients[0])],
                [float(self.distortionCoefficients[1])],
                [float(self.distortionCoefficients[2])],
                [float(self.distortionCoefficients[3])],
                [float(self.distortionCoefficients[4])]
            ]
        }

        return json.dumps(d, indent=4)

    @staticmethod
    def fromJson(d):
        """Deserializes this object from a dict"""
        return CameraProperties(
            d["name"],
            d["port"],
            d["widthNative"],
            d["heightNative"],
            d["hfov"],
            d["x"],
            d["y"],
            d["z"],
            cv.Mat(np.array([
                [d["calibrationMatrix"][0][0], d["calibrationMatrix"][0][1], d["calibrationMatrix"][0][2]],
                [d["calibrationMatrix"][1][0], d["calibrationMatrix"][1][1], d["calibrationMatrix"][1][2]],
                [d["calibrationMatrix"][2][0], d["calibrationMatrix"][2][1], d["calibrationMatrix"][2][2]]
            ])),
            cv.Mat(np.array([
                [d["distortionCoefficients"][0]],
                [d["distortionCoefficients"][1]],
                [d["distortionCoefficients"][2]],
                [d["distortionCoefficients"][3]],
                [d["distortionCoefficients"][4]],
            ]))
        )
