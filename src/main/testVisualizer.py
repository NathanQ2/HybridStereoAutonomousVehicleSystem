# Purely for debug purposes, not in test directory because of relative imports used in all the main/ files
# I shouldn't have done that :(

import socket
import asyncio

from VisualizerManager import VisualizerManager
from poseEstimator.StopSign import StopSign
from poseEstimator.SpeedLimitSign import SpeedLimitSign
from poseEstimator.WarningSign import WarningSign


async def main():
    visualizerManager = VisualizerManager(None)
    # objs = [StopSign(5, 10, 15), StopSign(25, 20, 15), SpeedLimitSign(60, 50, 20, 55)]
    objs = [StopSign(0, 0.01, 0.1), WarningSign(0.1, 0.01, 0.1), SpeedLimitSign(-0.1, 0.01, 0.1, 55)]
    while (True):
        await visualizerManager.update(objs)
    # await visualizerManager.update(objs)


if (__name__ == "__main__"):
    asyncio.run(main())
