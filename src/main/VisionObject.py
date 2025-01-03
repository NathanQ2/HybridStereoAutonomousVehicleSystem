from ultralytics import YOLO
from ultralytics.engine.results import Results

from src.main.ObjectType import ObjectType


class VisionObject:
    """Represents an object detected by a singular camera in 2d space"""
    def __init__(self, x: float, y: float, w: float, h: float, objectType: ObjectType, conf: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.objectType = objectType
        self.conf = conf

    @staticmethod
    def fromResults(results: Results):
        """Returns a VisionObject based of an Ultralytics Results object"""

        objects = []

        for box in results.boxes:
            pos = box.xywh[0]

            objects.append(
                VisionObject(
                    pos[0],
                    pos[1],
                    pos[2],
                    pos[3],
                    ObjectType.fromClassId(results.names, int(box.cls[0])),
                    box.conf[0]
                )
            )

        return objects
