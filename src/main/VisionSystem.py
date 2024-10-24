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
from src.main.VisionObject import VisionObject


class VisionSystem:
    def __init__(self, leftCamProps: CameraProperties, rightCampProps: CameraProperties, lidarDevice: str, modelPath: os.path):
        self.leftCamProps = leftCamProps
        self.rightCamProps = rightCampProps

        # init cameras
        self.rightCam = cv.VideoCapture(self.rightCamProps.port)
        self.leftCam = cv.VideoCapture(self.leftCamProps.port)

        self.poseEstimator = PoseEstimator(self.rightCamProps, self.leftCamProps, lidarDevice)

        # Load the trained model
        self.model = YOLO(modelPath)

    def start(self):
        # Performance statistics
        frames = 0
        startTimeSecs = time.perf_counter()

        while (True):
            frameStartTimeSecs = time.perf_counter()

            rRet, rFrame = rightCam.read()
            lRet, lFrame = leftCam.read()

            rFrame = cv.undistort(rFrame, self.rightCamProps.calibrationMatrix, self.rightCamProps.distortionCoefficients)
            lFrame = cv.undistort(lFrame, self.leftCamProps.calibrationMatrix, self.leftCamProps.distortionCoefficients)

            rResults = model.predict(rFrame, conf=0.70, verbose=False)
            lResults = model.predict(lFrame, conf=0.70, verbose=False)

            processedRFrame = rResults[0].plot()
            processedLFrame = lResults[0].plot()

            lObjects = VisionObject.fromResults(lResults)
            rObjects = VisionObject.fromResults(rResults)

            if (len(lObjects) != 0 and len(rObjects) != 0):
                x, y, z, = poseEstimator.update(rFrame, lFrame, rResults, lResults)

                print(f"POSE: ({Util.metersToInches(x)}, {Util.metersToInches(y)}, {Util.metersToInches(z)})")

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
