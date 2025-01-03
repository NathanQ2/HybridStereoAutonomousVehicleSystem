import math
from multiprocessing import shared_memory
import mmap
import struct
import os
import platform
import subprocess
import time
import socket
import asyncio
import threading

from src.main.util.Util import Util
from src.main.util.Logger import Logger


class Node:
    """A Node is one 'pixel' from the LiDAR's measurement. It has an angle and a distance, among other things."""

    def __init__(self, angle_z_q14, dist_mm_q2, quality, flag):
        self.angle_z_q14 = angle_z_q14
        self.dist_mm_q2 = dist_mm_q2
        self.quality = quality
        self.flag = flag


class LiDARMeasurement:
    """A collection of Nodes to form a 360 degree measurement"""

    def __init__(self, timestamp, nodes):
        self.timestamp = timestamp
        self.nodes = nodes

    def getDistAtAngle(self, angleDeg) -> float:
        """Returns the distance at a specified angle"""

        native = LiDARMeasurement.degToNative(angleDeg)
        closestNode = self.nodes[0]
        for node in self.nodes:
            if (abs(node.angle_z_q14 - native) < abs(closestNode.angle_z_q14 - native)):
                closestNode = node

        return Util.millimetersToMeters(closestNode.dist_mm_q2) / 4

    @staticmethod
    def degToNative(degrees: float) -> int:
        """Returns the natiev rotation units of the lidar"""

        # deg = node.angle_z_q14 * 90 / (1 << 14)
        # deg = node.angle_z_q14 * 90 / 2^14
        # deg = node.angle_z_q14 * (90 / 2^14)
        # deg / (90 / 2^14) = node.angle_z_q14
        return int(degrees / (90 / math.pow(2, 14)))


class LiDARThread(threading.Thread):
    """Thread that reads data from RP_LiDAR_Interface. Should only be instantiated by LiDARManager"""

    def __init__(self, ip: str, port: int):
        super().__init__(daemon=True)
        self.logger = Logger("LidarThread")

        # Setup socket
        self.IP = ip
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.IP, self.PORT))

        self.sock.listen(1)
        self.logger.info("Waiting for connection")
        self.conn, self.addr = self.sock.accept()

        self.latestMeasurement = None
        self.lock = threading.Lock()
        self.running = False

    def isConnected(self) -> bool:
        return self.conn is not None

    def run(self):
        self.running = True
        while (self.running):
            # Receive data from lidar over socket
            timestampBytes = self.conn.recv(8)
            timestampInt = int.from_bytes(timestampBytes, 'little', signed=False)
            # print(f"TimestampBytes: {timestampBytes.hex()} TimestampInt: {timestampInt}")

            nodes = []
            nodeSizeBytes = 2 + 4 + 1 + 1
            # For every node in measurement
            for i in range(291):
                angleBytes = self.conn.recv(2)
                distBytes = self.conn.recv(4)
                qualityBytes = self.conn.recv(1)
                flagBytes = self.conn.recv(1)

                angleInt = int.from_bytes(angleBytes, 'little', signed=False)
                # print(f"AngleBytes: {angleBytes.hex()}")
                # print(f"AngleInt: {angleInt}\n")

                distInt = int.from_bytes(distBytes, 'little', signed=False)
                # print(f"DistBytes: {distBytes.hex()}")
                # print(f"DistInt: {distInt}\n")

                qualityInt = int.from_bytes(qualityBytes, 'little', signed=False)
                # print(f"QualityBytes: {qualityBytes.hex()}")
                # print(f"QualityInt: {qualityInt}\n")

                flagInt = int.from_bytes(flagBytes, 'little', signed=False)
                # print(f"FlagBytes: {flagBytes.hex()}")
                # print(f"FlagInt: {flagInt}\n\n")

                nodes.append(Node(angleInt, distInt, qualityInt, flagInt))

            # Update latest measurement
            with self.lock:
                self.latestMeasurement = LiDARMeasurement(timestampInt, nodes)

    def stop(self):
        # Cleanup
        self.running = False
        self.conn.close()
        self.sock.close()


class LiDARManager:
    """Manages an external lidar and its thread."""

    def __init__(self, lidarDevice: str):
        self.logger = Logger("LiDARManager")
        self.logger.info("Starting LiDAR Interface")
        self.logger.trace(f"LiDAR Device: {lidarDevice}")

        # TODO: Make this work better ( -> config file?)
        # Path to lidar interface
        interfacePath = f"{os.path.dirname(os.path.realpath(__file__))}/../../../vendor/RP_LiDAR_Interface_Cpp/build/RP_LiDAR_Interface_Cpp"

        self.IP = "127.0.0.1"
        self.PORT = 5005

        # Start process
        self.p = None
        self.p = subprocess.Popen(
            [interfacePath, lidarDevice, self.IP, str(self.PORT)],
            stdout=subprocess.PIPE,
            text=True
        )

        # Create lidar thread
        self.lidarThread = LiDARThread(self.IP, self.PORT)

        while (self.lidarThread.isConnected() == False):
            pass
        self.start()

    def __del__(self):
        self.logger.trace("Stopping")
        self.lidarThread.stop()
        self.p.terminate()

    def getLatest(self) -> LiDARMeasurement | None:
        """Returns the latest measurement from the lidar device."""
        self.logger.trace("GetLatest")
        if (not self.lidarThread.isConnected() or not self.lidarThread.running):
            return None

        with self.lidarThread.lock:
            return self.lidarThread.latestMeasurement

    def start(self):
        self.lidarThread.start()
