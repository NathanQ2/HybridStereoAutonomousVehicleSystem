from ultralytics import YOLO
from ultralytics.engine.results import Results

from ObjectType import ObjectType


# Represents an object detected by a singular camera
class VisionObject:
    def __init__(self, x: float, y: float, w: float, h: float, objectType: ObjectType, conf: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.objectType = objectType
        self.conf = conf

    @staticmethod
    def fromResults(results: Results):
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
