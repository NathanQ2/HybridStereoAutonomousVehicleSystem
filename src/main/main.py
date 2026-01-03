import asyncio
import json
import sys

from src.main.Config import Config
from src.main.VisionSystem import VisionSystem
from src.main.util.Logger import Logger


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
