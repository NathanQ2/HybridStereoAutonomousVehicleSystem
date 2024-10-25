from scipy.special import cases
from ultralytics import YOLO
from ultralytics.engine.results import Results


# Type of object recognized by vision
class VisionObjectType(Enum):
    StopSign = 0
    Warning = 1
    Regulatory = 2

    @staticmethod
    def fromClassId(names: Dict[int, str], id: int) -> VisionObjectType:
        return VisionObjectType.fromClassName(names[id])

    @staticmethod
    def fromClassName(className: str):
        match className:
            case "stop":
                return VisionObjectType.StopSign
            case "warning":
                return VisionObjectType.Warning
            case "regulatory":
                return VisionObjectType.Regulatory


# Represents an object detected by a singular camera
class VisionObject:
    def __init__(self, x: float, y: float, w: float, h: float, objectType: VisionObjectType, conf: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.objectType = objectType
        self.conf = conf

    @staticmethod
    def fromResults(results: Results) -> list[VisionObject]:
        objects = []
        print(f"Classes Dict: {results.names}")

        for box in results.Boxes:
            pos = box.xywh

            objects.append(
                VisionObject(
                    pos[0],
                    pos[1],
                    pos[2],
                    pos[3],
                    VisionObjectType.fromClassId(results.names, box.id),
                    box.conf[0]
                )
            )

        return objects
