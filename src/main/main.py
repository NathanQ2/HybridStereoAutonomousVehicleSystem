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


from src.main.util.Util import Util
from src.main.util.Logger import Logger
from src.main.VisionSystem import VisionSystem
from src.main.poseEstimator.CameraProperties import CameraProperties
from src.main.Config import Config

# TODO: Update README.md
# TODO: Is async necessary?
# TODO: Train better model & check if input frame size is correct
# TODO: Add text recognition for speed signs
# TODO: Fix relative imports
# TODO: Dog


async def main():
    logger = Logger("root")
    if (len(sys.argv) != 2):
        logger.error(f"Invalid number of arguments, expected 1 but got {len(sys.argv) - 1}.")

        exit(1)

    # Load config file
    with open(sys.argv[1]) as f:
        config = Config.fromJson(json.loads(f.read()))

    # Initialize vision system
    vision = VisionSystem(config, logger.getChild("VisionSystem"))

    # Start vision system
    shouldQuit = False
    while(not shouldQuit):
        shouldQuit = await vision.update()


if (__name__ == "__main__"):
    asyncio.run(main())
