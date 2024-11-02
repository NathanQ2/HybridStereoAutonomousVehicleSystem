import socket
import asyncio

from VisualizerManager import VisualizerManager
from poseEstimator.StopSign import StopSign


async def main():
    visualizerManager = VisualizerManager(None)
    objs = [StopSign(5, 10, 15), StopSign(25, 20, 15)]
    # while (True):
    #     await visualizerManager.update(objs)
    await visualizerManager.update(objs)


if (__name__ == "__main__"):
    asyncio.run(main())
