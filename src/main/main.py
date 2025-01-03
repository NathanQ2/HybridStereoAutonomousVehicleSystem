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
# TODO: Add text recognition for speed signs
# TODO: Fix relative imports
# TODO: Dog


async def main():
    logger = Logger("Main")
    if (len(sys.argv) != 2):
        logger.error(f"ERR: Invalid number of arguments, expected 1 but got {len(sys.argv)}.")

        return 1

    # Load config file
    with open(sys.argv[1]) as f:
        config = Config.fromJson(json.loads(f.read()))

    # Initialize vision system
    vision = VisionSystem(config)

    # Start vision system
    await vision.start()


if (__name__ == "__main__"):
    asyncio.run(main())
