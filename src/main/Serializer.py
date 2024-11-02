from poseEstimator.PoseObject import PoseObject
from poseEstimator.StopSign import StopSign
from poseEstimator.SpeedLimitSign import SpeedLimitSign
from poseEstimator.WarningSign import WarningSign
from ObjectType import ObjectType

import struct


# We can't define these inside Serializer because the serializer class needs these
# and python won't define these before they are referenced in code :(
class SerializerConstants:
    OBJECT_TYPE_SIZE_BYTES = 4
    INT_SIZE_BYTES = 4
    FLOAT_SIZE_BYTES = 4
    POSE_OBJECT_SIZE_BYTES = OBJECT_TYPE_SIZE_BYTES + FLOAT_SIZE_BYTES * 3


class Serializer:

    def __init__(self):
        raise Exception("This is a utility class!")

    @staticmethod
    def serializeStopSign(stopSign: StopSign) -> bytearray:
        buff = bytearray()

        buff += int.to_bytes(ObjectType.StopSign, 4, "little", signed=True)

        buff += struct.pack("f", stopSign.x)
        buff += struct.pack("f", stopSign.y)
        buff += struct.pack("f", stopSign.z)

        print(f"ObjSize: {len(buff)}")

        return buff

    @staticmethod
    def serializeRegulatorySign(speedLimit: SpeedLimitSign) -> bytearray:
        return bytearray()

    @staticmethod
    def serializeWarningSign(warningSign: WarningSign) -> bytearray:
        return bytearray()

    @staticmethod
    def serialize(poseObject: PoseObject) -> bytearray:
        match poseObject.type:
            case ObjectType.StopSign:
                return Serializer.serializeStopSign(poseObject)
            case ObjectType.Regulatory:
                return Serializer.serializeRegulatorySign(poseObject)
            case ObjectType.Warning:
                return Serializer.serializeWarningSign(poseObject)

    @staticmethod
    def getSizePoseObject(poseObject: PoseObject) -> int:
        match poseObject.type:
            case ObjectType.StopSign:
                return SerializerConstants.POSE_OBJECT_SIZE_BYTES
            case ObjectType.Regulatory:
                return SerializerConstants.POSE_OBJECT_SIZE_BYTES + SerializerConstants.INT_SIZE_BYTES
            case ObjectType.Warning:
                return SerializerConstants.POSE_OBJECT_SIZE_BYTES

    @staticmethod
    def getSizePoseObjects(poseObjects: list[PoseObject]) -> int:
        size = 0
        for poseObject in poseObjects:
            size += Serializer.getSizePoseObject(poseObject)

        return size
