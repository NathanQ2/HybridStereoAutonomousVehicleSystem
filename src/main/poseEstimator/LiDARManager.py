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

from util.Util import Util


class Node:
    def __init__(self, angle_z_q14, dist_mm_q2, quality, flag):
        self.angle_z_q14 = angle_z_q14
        self.dist_mm_q2 = dist_mm_q2
        self.quality = quality
        self.flag = flag


class LiDARMeasurement:
    def __init__(self, timestamp, nodes):
        self.timestamp = timestamp
        self.nodes = nodes

    def getDistAtAngle(self, angleDeg) -> float:
        native = LiDARMeasurement.degToNative(angleDeg)
        closestNode = self.nodes[0]
        for node in self.nodes:
            if (abs(node.angle_z_q14 - native) < abs(closestNode.angle_z_q14 - native)):
                closestNode = node

        return Util.millimetersToMeters(closestNode.dist_mm_q2) / 4

    # Returns the native rotation units of the lidar
    @staticmethod
    def degToNative(degrees: float) -> int:
        # deg = node.angle_z_q14 * 90 / (1 << 14)
        # deg = node.angle_z_q14 * 90 / 2^14
        # deg = node.angle_z_q14 * (90 / 2^14)
        # deg / (90 / 2^14) = node.angle_z_q14
        return int(degrees / (90 / math.pow(2, 14)))


class LiDARManager:
    def __init__(self, lidarDevice: str):
        print(f"-- INFO -- Starting LiDAR Interface...")
        print(f"-- INFO -- LiDAR Device: {lidarDevice}")

        interfacePath = f"{os.path.dirname(os.path.realpath(__file__))}/../../../vendor/RP_LiDAR_Interface_Cpp/build/RP_LiDAR_Interface_Cpp"

        # Setup socket
        self.IP = "127.0.0.1"
        self.PORT = 5005
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.IP, self.PORT))

        # Make interface path sys.argv
        self.p = subprocess.Popen(
            [interfacePath, lidarDevice, self.IP, str(self.PORT)],
            stdout=subprocess.PIPE,
            text=True
        )

        self.sock.listen(1)
        print("-- INFO -- Waiting for connection...")
        # TODO: add cleanup for self.conn and self.sock
        self.conn, self.addr = self.sock.accept()

        # time.sleep(3)

        output = self.p.stdout.read(1)
        print(f"-- INFO -- Begin RP_LiDAR_Interface STDOUT:")
        while (output.find("Scanning") == -1):
            if (self.p.poll() is None):  # Program still running
                output += self.p.stdout.read(1)

                print(output, end='\r')
            else:
                print(f"-- ERROR -- RP_LiDAR_Interface has crashed with exit code {self.p.returncode} during startup!")
                exit(1)

        print(f"-- INFO -- End RP_LiDAR_Interface STDOUT")
        self.latestMeasurement = None

    def __del__(self):
        self.p.terminate()
        self.conn.close()
        self.sock.close()

    def getLatest(self) -> LiDARMeasurement | None:
        return self.latestMeasurement

    async def start(self):
        print("hello!")
        while(True):
            timestampBytes = await self.conn.recv(8)
            timestampInt = int.from_bytes(timestampBytes, 'little', signed=False)
            print(f"TimestampBytes: {timestampBytes.hex()} TimestampInt: {timestampInt}")

            nodes = []
            nodeSizeBytes = 2 + 4 + 1 + 1
            for i in range(291):
                angleBytes = await self.conn.recv(2)
                distBytes = await self.conn.recv(4)
                qualityBytes = await self.conn.recv(1)
                flagBytes = await self.conn.recv(1)

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

            self.latestMeasurement = LiDARMeasurement(timestampInt, nodes)

            await asyncio.sleep(0.01)
