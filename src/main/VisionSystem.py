import time
import numpy as np
import cv2 as cv
from ultralytics import YOLO
import json
import os
import sys
import subprocess
import platform
import asyncio

from poseEstimator.PoseEstimator import PoseEstimator
from poseEstimator.CameraProperties import CameraProperties
from poseEstimator.PoseObject import PoseObject
from poseEstimator.StopSign import StopSign
from poseEstimator.SpeedLimitSign import SpeedLimitSign
from poseEstimator.WarningSign import WarningSign
from VisionObject import VisionObject, ObjectType
from VisualizerManager import VisualizerManager
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

        # self.visualizer = VisualizerManager("/Users/nathanquartaro/DevLocal/GodotProjects/hybridstereoautonomousvehiclesystemvisualizer/builds/mac/HybridStereoAutonomousVehicleSystemVisualizer.app/Contents/MacOS/HybridStereoAutonomousVehicleSystemVisualizer")
        self.visualizer = VisualizerManager(None)

    def toPoseObjects(self, lObjects: list[VisionObject], rObjects: list[VisionObject]) -> list[PoseObject]:
        # Link left and right vision objects
        linkedObjects: dict[int, tuple[VisionObject, VisionObject]] = {}

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
                # if (not Util.isSimilar(rObject.x, lObject.x, POSITION_TOLERANCE * boxAreaAvg)):
                #     print("x pos out of tolerance")
                #     continue
                # if (not Util.isSimilar(rObject.y, lObject.y, POSITION_TOLERANCE * boxAreaAvg)):
                #     print("y pos out of tolerance")
                #     continue

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
                case ObjectType.StopSign:
                    poseObjects.append(StopSign(x, y, z))
                case ObjectType.Regulatory:
                    poseObjects.append(SpeedLimitSign(x, y, z, 55))
                case ObjectType.Warning:
                    poseObjects.append(WarningSign(x, y, z))

        return poseObjects

    async def start(self):
        # Performance statistics
        frames = 0
        startTimeSecs = time.perf_counter()

        while (True):
            frameStartTimeSecs = time.perf_counter()

            rRet, rFrame = self.rightCam.read()
            lRet, lFrame = self.leftCam.read()

            # Image dimensions to use instead of native camera resolution
            FRAME_SIZE = (640, 480)

            rFrame = cv.resize(rFrame, FRAME_SIZE)
            lFrame = cv.resize(lFrame, FRAME_SIZE)

            # Get new camera matrix scaled for correct aspect ratio
            rNewMatrix, rRoi = cv.getOptimalNewCameraMatrix(
                self.rightCamProps.calibrationMatrix,
                self.rightCamProps.distortionCoefficients.reshape(-1, 1),
                (self.rightCamProps.widthNative, self.rightCamProps.heightNative),
                1,
                FRAME_SIZE,
                True
            )

            lNewMatrix, lRoi = cv.getOptimalNewCameraMatrix(
                self.leftCamProps.calibrationMatrix,
                self.leftCamProps.distortionCoefficients.reshape(-1, 1),
                (self.leftCamProps.widthNative, self.leftCamProps.heightNative),
                1,
                FRAME_SIZE,
                True
            )

            rFrame = cv.undistort(
                rFrame,
                self.rightCamProps.calibrationMatrix,
                self.rightCamProps.distortionCoefficients,
                None,
                rNewMatrix
            )

            lFrame = cv.undistort(
                lFrame,
                self.leftCamProps.calibrationMatrix,
                self.leftCamProps.distortionCoefficients,
                None,
                lNewMatrix
            )

            MIN_CONFIDENCE = 0.55

            rResults = self.model.predict(rFrame, conf=MIN_CONFIDENCE, verbose=False)
            lResults = self.model.predict(lFrame, conf=MIN_CONFIDENCE, verbose=False)

            # Debug drawing
            processedRFrame = rResults[0].plot()
            processedLFrame = lResults[0].plot()
            # processedLFrame = cv.resize(lResults[0].plot(), (640, 480))
            # processedRFrame = cv.resize(rResults[0].plot(), (640, 480))

            # Generate vision objects from model results
            lObjects = VisionObject.fromResults(lResults[0])
            rObjects = VisionObject.fromResults(rResults[0])

            objects = self.toPoseObjects(lObjects, rObjects)
            # Update visualizer
            await self.visualizer.update(objects)

            for obj in objects:
                print(f"POSE OBJECT ({obj.type}): ({Util.metersToInches(obj.x)}in, {Util.metersToInches(obj.y)}in, {Util.metersToInches(obj.z)}in)")

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
