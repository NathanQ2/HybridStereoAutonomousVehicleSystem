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

from src.main.poseEstimator.PoseEstimator import PoseEstimator
from src.main.poseEstimator.CameraProperties import CameraProperties
from src.main.poseEstimator.PoseObject import PoseObject
from src.main.poseEstimator.StopSign import StopSign
from src.main.poseEstimator.SpeedLimitSign import SpeedLimitSign
from src.main.poseEstimator.WarningSign import WarningSign
from src.main.VisionObject import VisionObject, ObjectType
from src.main.VisualizerManager import VisualizerManager
from src.main.Config import Config
from src.main.util.Logger import Logger
from src.main.util.Util import Util


class VisionSystem:
    """Represents the entire camera / lidar system"""

    def __init__(self, config: Config, logger: Logger):
        self.logger = logger

        self.leftCamProps = config.leftCameraProperties
        self.rightCamProps = config.rightCameraProperties

        # Init cameras
        self.rightCam = cv.VideoCapture(self.rightCamProps.port)
        self.leftCam = cv.VideoCapture(self.leftCamProps.port)

        # Init PoseEstimator
        self.poseEstimator = PoseEstimator(
            self.rightCamProps,
            self.leftCamProps,
            config.lidarDevice,
            self.logger.getChild("PoseEstimator")
        )

        # Load the trained model
        self.model = YOLO(config.modelPath)

        self.visualizer = VisualizerManager(config.visualizerPath if (config.visualizerPath != "None") else None,
                                            self.logger.getChild("VisualizerManager"))

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

    async def update(self) -> bool:
        frameStartTimeSecs = time.perf_counter()

        # Read frames from cameras
        rRet, rFrame = self.rightCam.read()
        lRet, lFrame = self.leftCam.read()

        # Undistorted camera frames
        rFrame = cv.undistort(
            rFrame,
            self.rightCamProps.calibrationMatrix,
            self.rightCamProps.distortionCoefficients,
            None,
        )

        lFrame = cv.undistort(
            lFrame,
            self.leftCamProps.calibrationMatrix,
            self.leftCamProps.distortionCoefficients,
            None,
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
            self.logger.trace(
                f"POSE OBJECT ({obj.type}): ({Util.metersToInches(obj.x)}in, {Util.metersToInches(obj.y)}in, {Util.metersToInches(obj.z)}in)")

        cv.imshow("Processed Right Frame", processedRFrame)
        cv.imshow("Processed Left Frame", processedLFrame)

        if (cv.waitKey(1) & 0xFF == ord('q')):
            return True

        frameEndTimeSecs = time.perf_counter()
        self.logger.record("FrameTime", frameEndTimeSecs - frameStartTimeSecs)

        return False

    def __del__(self):
        self.logger.trace("Stopping")
        # Clean up
        self.rightCam.release()
        self.leftCam.release()

        cv.destroyAllWindows()
