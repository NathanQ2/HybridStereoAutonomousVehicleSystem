import socket
import subprocess
import asyncio

from src.main.poseEstimator.PoseObject import PoseObject
from src.main.Serializer import Serializer
from src.main.util.Logger import Logger


class VisualizerManager:
    """Manages the visualizer gui"""

    def __init__(self, visualizerPath: str | None):
        self.logger = Logger("VisualizerManager")

        self.logger.info("Starting Visualizer")
        self.IP = "127.0.0.1"
        self.PORT = 5006
        self.p = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.IP, self.PORT))

        if (visualizerPath is not None):
            self.p = subprocess.Popen(
                [visualizerPath],
                stdout=subprocess.PIPE,
                text=True
            )

        self.sock.listen(1)
        self.logger.info("Waiting for connection")
        self.conn, self.addr = self.sock.accept()
        self.logger.info(f"Connected at {self.addr}")

        pass

    def __del__(self):
        if (self.p is not None):
            self.p.terminate()
        self.conn.close()
        self.sock.close()

    async def update(self, poseObjects: list[PoseObject]):
        """Publish new data to the visualizer"""

        # TODO: update this
        # Serialization spec:
        # 4 bytes - size of rest of message in bytes
        # Pose objects

        # Create new byte array
        buff = bytearray()

        # Write length to byte array
        size = Serializer.getSizePoseObjects(poseObjects)
        sizeBytes = int.to_bytes(size, 4, "little", signed=False)
        buff += sizeBytes

        for obj in poseObjects:
            buff += Serializer.serialize(obj)

        # Send bytes to client
        try:
            self.conn.send(buff)
        except BrokenPipeError:
            self.logger.warn("The visualizer has disconnected, stopping.")

            exit(0)
