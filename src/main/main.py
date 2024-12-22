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


from util.Util import Util
from util.Logger import Logger
from VisionSystem import VisionSystem
from poseEstimator.CameraProperties import CameraProperties

# TODO: Add one config file support
# TODO: Update README.md
# TODO: Add text recognition for speed signs
# TODO: Dog


async def main():
    logger = Logger("Main")
    if (len(sys.argv) != 3):
        logger.error(f"ERR: Invalid number of arguments, expected 3 but got {len(sys.argv)}.")

        return 1

    # Load camera properties json files
    rightCamPropsJson = None
    leftCamPropsJson = None
    with open(f"{os.getcwd()}/cameraCalib/rightCameraProperties.json", "r") as f:
        rightCamPropsJson = f.read()

    with open(f"{os.getcwd()}/cameraCalib/leftCameraProperties.json", "r") as f:
        leftCamPropsJson = f.read()

    rightCamProps = CameraProperties.fromJson(json.loads(rightCamPropsJson))
    leftCamProps = CameraProperties.fromJson(json.loads(leftCamPropsJson))

    # Initialize vision system
    vision = VisionSystem(leftCamProps, rightCamProps, sys.argv[1], sys.argv[2])

    # Start vision system
    await vision.start()


if (__name__ == "__main__"):
    asyncio.run(main())
