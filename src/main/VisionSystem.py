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
from src.main.util.Logger import Logger
from util.Util import Util


class VisionSystem:
    """Represents the entire camera / lidar system"""

    def __init__(self, leftCamProps: CameraProperties, rightCampProps: CameraProperties, lidarDevice: str,
                 modelPath: os.path):
        self.logger = Logger("VisionSystem")

        self.leftCamProps = leftCamProps
        self.rightCamProps = rightCampProps

        # Init cameras
        self.rightCam = cv.VideoCapture(self.rightCamProps.port)
        self.leftCam = cv.VideoCapture(self.leftCamProps.port)

        # Init PoseEstimator
        self.poseEstimator = PoseEstimator(self.rightCamProps, self.leftCamProps, lidarDevice)

        # Load the trained model
        self.model = YOLO(modelPath)

        self.visualizer = VisualizerManager("/Users/nathanquartaro/DevLocal/GodotProjects/hybridstereoautonomousvehiclesystemvisualizer/builds/mac/HybridStereoAutonomousVehicleSystemVisualizer.app/Contents/MacOS/HybridStereoAutonomousVehicleSystemVisualizer")
        # self.visualizer = VisualizerManager(None)

    def toPoseObjects(self, lObjects: list[VisionObject], rObjects: list[VisionObject]) -> list[PoseObject]:
        """Converts a list of VisionObjects from the left and right cameras to a list of PoseObjects"""

        # Link left and right vision objects
        linkedObjects: dict[int, tuple[VisionObject, VisionObject]] = {}

        # Loop through every object and determine it's corresponding partner in the right camera
        for i in range(len(lObjects)):
            lObject = lObjects[i]
            for rObject in rObjects:
                if (rObject.objectType != lObject.objectType):
                    continue

                # These two objects are probably the same
                linkedObjects[i] = (lObject, rObject)
                break

        # Create a list of PoseObjects
        poseObjects: list[PoseObject] = []
        for i in linkedObjects:
            lObject = linkedObjects[i][0]
            rObject = linkedObjects[i][1]
            # Estimate the position of this object
            x, y, z = self.poseEstimator.estimate(lObject, rObject)

            # Append the correct sign depending on its type
            match rObject.objectType:
                case ObjectType.StopSign:
                    poseObjects.append(StopSign(x, y, z))
                case ObjectType.Regulatory:
                    poseObjects.append(SpeedLimitSign(x, y, z, 55))
                case ObjectType.Warning:
                    poseObjects.append(WarningSign(x, y, z))

        return poseObjects

    async def start(self):
        """Starts the vision system"""

        # Performance statistics
        frames = 0
        startTimeSecs = time.perf_counter()

        while (True):
            frameStartTimeSecs = time.perf_counter()

            # Read frames from cameras
            rRet, rFrame = self.rightCam.read()
            lRet, lFrame = self.leftCam.read()

            # Undistort the camera frames
            rFrame = cv.undistort(
                rFrame,
                self.rightCamProps.calibrationMatrix,
                self.rightCamProps.distortionCoefficients,
                None,
                # rNewMatrix
            )

            lFrame = cv.undistort(
                lFrame,
                self.leftCamProps.calibrationMatrix,
                self.leftCamProps.distortionCoefficients,
                None,
                # lNewMatrix
            )

            # Define minimum confidence
            # TODO: Up this?
            MIN_CONFIDENCE = 0.35

            # Run the model on the right and left cameras
            rResults = self.model.predict(rFrame, conf=MIN_CONFIDENCE, verbose=False)
            lResults = self.model.predict(lFrame, conf=MIN_CONFIDENCE, verbose=False)

            # Debug drawing
            processedLFrame = cv.resize(lResults[0].plot(), (640, 480))
            processedRFrame = cv.resize(rResults[0].plot(), (640, 480))

            # Generate vision objects from model results
            lObjects = VisionObject.fromResults(lResults[0])
            rObjects = VisionObject.fromResults(rResults[0])

            # Estimate the position of these objects
            objects = self.toPoseObjects(lObjects, rObjects)

            # Update visualizer
            await self.visualizer.update(objects)

            for obj in objects:
                self.logger.trace(f"POSE OBJECT ({obj.type}): ({Util.metersToInches(obj.x)}in, {Util.metersToInches(obj.y)}in, {Util.metersToInches(obj.z)}in)")

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
