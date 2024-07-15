import time
import numpy as np
import cv2 as cv
from ultralytics import YOLO
import json
import os
import subprocess
import platform

from poseEstimator.PoseEstimator import PoseEstimator
from poseEstimator.CameraProperties import CameraProperties
from util.Util import Util


def startLiDARInterface():
    currentPlatform = platform.system()
    if (currentPlatform == "Windows"):
        path = f"{os.path.dirname(os.path.realpath(__file__))}/../../vendor/RP_LiDAR_Interface_Cpp/build/Debug/RP_LiDAR_Interface_Cpp.exe"
    else:
        path = f"{os.path.dirname(os.path.realpath(__file__))}/../../vendor/RP_LiDAR_Interface_Cpp/build/Debug/RP_LiDAR_Interface_Cpp"

    print(f"-- INFO -- Starting LiDAR Interface... PATH: {path}")
    p = subprocess.Popen(
        [path],
        stdout=subprocess.PIPE,
        text=True
    )


def main():
    # startLiDARInterface()

    # Load camera properties json file
    rightCamPropsJson = None
    leftCamPropsJson = None
    with open(f"{os.getcwd()}/cameraCalib/rightCameraProperties.json", "r") as f:
        rightCamPropsJson = f.read()

    with open(f"{os.getcwd()}/cameraCalib/leftCameraProperties.json", "r") as f:
        leftCamPropsJson = f.read()

    rightCamProps = CameraProperties.fromJson(json.loads(rightCamPropsJson))
    leftCamProps = CameraProperties.fromJson(json.loads(leftCamPropsJson))

    # init cameras
    rightCam = cv.VideoCapture(rightCamProps.port)
    leftCam = cv.VideoCapture(leftCamProps.port)

    poseEstimator = PoseEstimator(rightCamProps, leftCamProps)

    # Load the trained model
    model = YOLO(f"{os.path.dirname(os.path.realpath(__file__))}/../../runs/detect/train/weights/best.pt")

    # Performance statistics
    frames = 0
    startTimeSecs = time.perf_counter()

    while (True):
        frameStartTimeSecs = time.perf_counter()

        rRet, rFrame = rightCam.read()
        lRet, lFrame = leftCam.read()

        rFrame = cv.undistort(rFrame, rightCamProps.calibrationMatrix, rightCamProps.distortionCoefficients)
        lFrame = cv.undistort(lFrame, leftCamProps.calibrationMatrix, leftCamProps.distortionCoefficients)

        rResults = model.predict(rFrame, conf=0.70, verbose=False)
        lResults = model.predict(lFrame, conf=0.70, verbose=False)

        processedRFrame = rResults[0].plot()
        processedLFrame = lResults[0].plot()

        if (len(rResults[0].boxes) != 0 and len(lResults[0].boxes) != 0):
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

    # Clean up
    rightCam.release()
    leftCam.release()

    cv.destroyAllWindows()


if (__name__ == "__main__"):
    main()
