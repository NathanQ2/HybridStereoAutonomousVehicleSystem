import time
import numpy as np
import cv2 as cv
from ultralytics import YOLO
import json
import os
import sys
import subprocess
import platform

from poseEstimator.PoseEstimator import PoseEstimator
from poseEstimator.CameraProperties import CameraProperties
from poseEstimator.PoseObject import PoseObject
from poseEstimator.StopSign import StopSign
from poseEstimator.SpeedLimitSign import SpeedLimitSign
from poseEstimator.WarningSign import WarningSign
from VisionObject import VisionObject, VisionObjectType
from util.Util import Util


class VisionSystem:
    def __init__(self, leftCamProps: CameraProperties, rightCampProps: CameraProperties, lidarDevice: str,
                 modelPath: os.path):
        self.leftCamProps = leftCamProps
        self.rightCamProps = rightCampProps

        # init cameras
        self.rightCam = cv.VideoCapture(self.rightCamProps.port)
        self.leftCam = cv.VideoCapture(self.leftCamProps.port)

        self.poseEstimator = PoseEstimator(self.rightCamProps, self.leftCamProps, lidarDevice)

        # Load the trained model
        self.model = YOLO(modelPath)

    def toPoseObjects(self, lObjects: list[VisionObject], rObjects: list[VisionObject]) -> list[PoseObject]:
        # Link left and right vision objects
        linkedObjects: dict[int, tuple[VisionObject, VisionObject]] = {}

        # TODO: Tune these
        # Tolerance for box dimensions (in pixels)
        DIMENSION_TOLERANCE = 200
        # Tolerance for position
        # (multiplied by box area b/c we want this to scale based off distance away from camera system)
        POSITION_TOLERANCE = 1000 / 128935

        # print(len(lObjects))

        for i in range(len(lObjects)):
            lObject = lObjects[i]
            for rObject in rObjects:
                if (rObject.objectType != lObject.objectType):
                    continue

                # If the width/height of the two objects are not similar these two objects are probably not the same
                # if (not Util.isSimilar(rObject.w, lObject.w, DIMENSION_TOLERANCE)):
                #     print("w dimension out of tolerance")
                #     continue
                # if (not Util.isSimilar(rObject.h, lObject.h, DIMENSION_TOLERANCE)):
                #     print("h dimension out of tolerance")
                #     continue

                rBoxArea = rObject.w * rObject.h
                lBoxArea = lObject.w * lObject.h
                boxAreaAvg = (rBoxArea + lBoxArea) / 2

                # print(f"Dimension delta w: {abs(rObject.w - lObject.w)}")
                # print(f"Dimension delta h: {abs(rObject.h - lObject.h)}")
                # print(f"Position delta x: {abs(rObject.x - lObject.x)}")
                # print(f"Position delta y: {abs(rObject.y - lObject.y)}")
                # print(f"Box Area: {boxAreaAvg}")

                # If the position of the two objects are not similar these two objects are probably not the same
                if (not Util.isSimilar(rObject.x, lObject.x, POSITION_TOLERANCE * boxAreaAvg)):
                    print("x pos out of tolerance")
                    continue
                if (not Util.isSimilar(rObject.y, lObject.y, POSITION_TOLERANCE * boxAreaAvg)):
                    print("y pos out of tolerance")
                    continue

                # These two objects are probably the same
                linkedObjects[i] = (lObject, rObject)
                break

        # print(f"LINKED: {linkedObjects}")

        poseObjects: list[PoseObject] = []
        for i in linkedObjects:
            lObject = linkedObjects[i][0]
            rObject = linkedObjects[i][1]
            x, y, z = self.poseEstimator.estimate(lObject, rObject)

            match rObject.objectType:
                case VisionObjectType.StopSign:
                    poseObjects.append(StopSign(x, y, z))
                case VisionObjectType.Regulatory:
                    poseObjects.append(SpeedLimitSign(x, y, z, 55))
                case VisionObjectType.Warning:
                    poseObjects.append(WarningSign(x, y, z))
                # TODO: Add more signs

        return poseObjects

    def start(self):
        # Performance statistics
        frames = 0
        startTimeSecs = time.perf_counter()

        while (True):
            frameStartTimeSecs = time.perf_counter()

            rRet, rFrame = self.rightCam.read()
            lRet, lFrame = self.leftCam.read()

            # Get new camera matrix scaled for correct aspect ratio
            rNewMatrix, rRoi = cv.getOptimalNewCameraMatrix(
                self.rightCamProps.calibrationMatrix,
                self.rightCamProps.distortionCoefficients.reshape(-1, 1),
                (self.rightCamProps.widthNative, self.rightCamProps.heightNative),
                1,
                (self.rightCamProps.widthNative, self.rightCamProps.heightNative)
            )

            lNewMatrix, lRoi = cv.getOptimalNewCameraMatrix(
                self.leftCamProps.calibrationMatrix,
                self.leftCamProps.distortionCoefficients.reshape(-1, 1),
                (self.leftCamProps.widthNative, self.leftCamProps.heightNative),
                1,
                (self.leftCamProps.widthNative, self.leftCamProps.heightNative)
            )

            rFrame = cv.undistort(
                rFrame,
                self.rightCamProps.calibrationMatrix,
                self.rightCamProps.distortionCoefficients,
            )

            lFrame = cv.undistort(
                lFrame,
                self.leftCamProps.calibrationMatrix,
                self.leftCamProps.distortionCoefficients,
            )

            MIN_CONFIDENCE = 0.70

            rResults = self.model.predict(rFrame, conf=MIN_CONFIDENCE, verbose=False)
            lResults = self.model.predict(lFrame, conf=MIN_CONFIDENCE, verbose=False)

            # Debug drawing
            processedRFrame = rResults[0].plot()
            processedLFrame = lResults[0].plot()

            # Generate vision objects from model results
            lObjects = VisionObject.fromResults(lResults[0])
            rObjects = VisionObject.fromResults(rResults[0])

            objects = self.toPoseObjects(lObjects, rObjects)
            print(objects)

            for obj in objects:
                print(f"POSE OBJECT ({obj.objectType}): ({Util.metersToInches(obj.x)}in, {Util.metersToInches(obj.y)}in, {Util.metersToInches(obj.z)}in)")

            cv.imshow("Processed Right Frame", processedRFrame)
            cv.imshow("Processed Left Frame", processedLFrame)

            if (cv.waitKey(1) & 0xFF == ord('q')):
                break

            frameEndTimeSecs = time.perf_counter()
            frames += 1

            # print(f"Frame time: {(frameEndTimeSecs - frameStartTimeSecs) * 1000}ms")
            # print(f"FPS: {frames / (frameEndTimeSecs - startTimeSecs)}")

    def __del__(self):
        # Clean up
        self.rightCam.release()
        self.leftCam.release()

        cv.destroyAllWindows()
