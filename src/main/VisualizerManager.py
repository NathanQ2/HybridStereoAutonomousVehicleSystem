import socket
import subprocess
import asyncio

from poseEstimator.PoseObject import PoseObject
from Serializer import Serializer


class VisualizerManager:
    def __init__(self, visualizerPath: str | None):
        print("-- INFO -- Starting Visualizer...")
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
        print("-- INFO -- Waiting for connection...")
        self.conn, self.addr = self.sock.accept()

        pass

    def __del__(self):
        if (self.p is not None):
            self.p.terminate()
        self.conn.close()
        self.sock.close()

    async def update(self, poseObjects: list[PoseObject]):
        # TODO: update this
        # Serialization spec:
        # 4 bytes - size of rest of message in bytes
        # pose objects

        # Create new byte array
        buff = bytearray()

        # Write length to byte array
        size = Serializer.getSizePoseObjects(poseObjects)
        print(f"SizeBytes: {size}")
        sizeBytes = int.to_bytes(size, 4, "little", signed=False)
        buff += sizeBytes

        # if (len(poseObjects) != 0):
        #     buff += Serializer.serialize(poseObjects[0])

        for obj in poseObjects:
            buff += Serializer.serialize(obj)

        # Send bytes to client
        self.conn.send(buff)
        print(f"Sent: {buff.hex()}")
