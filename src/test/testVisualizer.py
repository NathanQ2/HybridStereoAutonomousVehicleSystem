import socket
import asyncio

from src.main.VisualizerManager import VisualizerManager
from src.main.poseEstimator.StopSign import StopSign
from src.main.poseEstimator.SpeedLimitSign import SpeedLimitSign
from src.main.poseEstimator.WarningSign import WarningSign
from src.main.util.Logger import Logger


async def main():
    logger = Logger("TestVisualizer")
    visualizerManager = VisualizerManager(None, logger.getChild("Visualizer"))

    objs = [
        StopSign(0.0, 0.1, 0.1),
        SpeedLimitSign(0.1, 0.0, 0.25, 55)
    ]

    while (True):
        await visualizerManager.update(objs)


if (__name__ == "__main__"):
    asyncio.run(main())
