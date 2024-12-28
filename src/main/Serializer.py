import struct

from src.main.poseEstimator.PoseObject import PoseObject
from src.main.poseEstimator.StopSign import StopSign
from src.main.poseEstimator.SpeedLimitSign import SpeedLimitSign
from src.main.poseEstimator.WarningSign import WarningSign
from src.main.ObjectType import ObjectType


# TODO: I'm pretty sure we can define inside Serializer, we just have to use self.
# We can't define these inside Serializer because the serializer class needs these
# and python won't define these before they are referenced in code :(
class SerializerConstants:
    OBJECT_TYPE_SIZE_BYTES = 4
    INT_SIZE_BYTES = 4
    FLOAT_SIZE_BYTES = 4
    POSE_OBJECT_SIZE_BYTES = OBJECT_TYPE_SIZE_BYTES + FLOAT_SIZE_BYTES * 3


class Serializer:
    """Responsible for serializing objects (usually PoseObjects) into binary"""

    def __init__(self):
        raise Exception("This is a utility class!")

    @staticmethod
    def serializeStopSign(stopSign: StopSign) -> bytearray:
        """Serializes a stop sign. Returns a bytearray that can be sent over the network."""
        buff = bytearray()

        buff += int.to_bytes(ObjectType.StopSign, 4, "little", signed=True)

        buff += struct.pack("f", stopSign.x)
        buff += struct.pack("f", stopSign.y)
        buff += struct.pack("f", stopSign.z)

        return buff

    @staticmethod
    def serializeRegulatorySign(speedLimit: SpeedLimitSign) -> bytearray:
        """Serializes a speed limit sign. Returns a bytearray that can be sent over the network."""
        buff = bytearray()

        buff += int.to_bytes(ObjectType.Regulatory, 4, "little", signed=True)

        buff += struct.pack("f", speedLimit.x)
        buff += struct.pack("f", speedLimit.y)
        buff += struct.pack("f", speedLimit.z)

        buff += int.to_bytes(speedLimit.speed, 4, "little", signed=False)

        return buff

    @staticmethod
    def serializeWarningSign(warningSign: WarningSign) -> bytearray:
        """Serializes a warning sign. Returns a bytearray that can be sent over the network."""
        buff = bytearray()

        buff += int.to_bytes(ObjectType.Warning, 4, "little", signed=True)

        buff += struct.pack("f", warningSign.x)
        buff += struct.pack("f", warningSign.y)
        buff += struct.pack("f", warningSign.z)

        return buff

    @staticmethod
    def serialize(poseObject: PoseObject) -> bytearray:
        """Serializes a PoseObject"""
        match poseObject.type:
            case ObjectType.StopSign:
                return Serializer.serializeStopSign(poseObject)
            case ObjectType.Regulatory:
                return Serializer.serializeRegulatorySign(poseObject)
            case ObjectType.Warning:
                return Serializer.serializeWarningSign(poseObject)

    @staticmethod
    def getSizePoseObject(poseObject: PoseObject) -> int:
        """Returns the size (in bytes) of a PoseObject. PoseObject's are not fixed size because some child classes have more fields than others."""
        match poseObject.type:
            case ObjectType.StopSign:
                return SerializerConstants.POSE_OBJECT_SIZE_BYTES
            case ObjectType.Regulatory:
                return SerializerConstants.POSE_OBJECT_SIZE_BYTES + SerializerConstants.INT_SIZE_BYTES
            case ObjectType.Warning:
                return SerializerConstants.POSE_OBJECT_SIZE_BYTES

    @staticmethod
    def getSizePoseObjects(poseObjects: list[PoseObject]) -> int:
        """Returns the size of a list of PoseObjects (in bytes)"""

        size = 0
        for poseObject in poseObjects:
            size += Serializer.getSizePoseObject(poseObject)

        return size
