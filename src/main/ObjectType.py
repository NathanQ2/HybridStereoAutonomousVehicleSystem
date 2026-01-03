from enum import IntEnum


class ObjectType(IntEnum):
    """Type of object recognized by vision system"""

    StopSign = 0
    Warning = 1
    Regulatory = 2

    @staticmethod
    def fromClassId(names: dict[int, str], id: int):
        return ObjectType.fromClassName(names[id])

    @staticmethod
    def fromClassName(className: str):
        match className:
            case "stop":
                return ObjectType.StopSign
            case "warning":
                return ObjectType.Warning
            case "regulatory":
                return ObjectType.Regulatory
        return None
