import socket
import asyncio

from src.main.VisualizerManager import VisualizerManager
from src.main.poseEstimator.StopSign import StopSign
from src.main.poseEstimator.SpeedLimitSign import SpeedLimitSign
from src.main.poseEstimator.WarningSign import WarningSign


async def main():
    visualizerManager = VisualizerManager(None)

    objs = [StopSign(0.0, 0.1, 0.1)]

    while (True):
        await visualizerManager.update(objs)


if (__name__ == "__main__"):
    asyncio.run(main())
