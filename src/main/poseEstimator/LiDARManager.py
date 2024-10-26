import math
from multiprocessing import shared_memory
import mmap
import struct
import os
import platform
import subprocess
import time

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

        currentPlatform = platform.system()
        sharedMemoryPath = None
        if (currentPlatform == "Windows"):
            interfacePath = f"{os.path.dirname(os.path.realpath(__file__))}/../../../vendor/RP_LiDAR_Interface_Cpp/build/Debug/RP_LiDAR_Interface_Cpp.exe"
            sharedMemoryPath = r"C:\ProgramData\boost_interprocess\\"
            for root, dirs, files in os.walk(sharedMemoryPath):
                for file in files:
                    if (file == "RP_LiDAR_Shared_Memory"):
                        sharedMemoryPath = os.path.join(root, file)

                        break
        else:  # Mac and linux should be the same
            interfacePath = f"{os.path.dirname(os.path.realpath(__file__))}/../../../vendor/RP_LiDAR_Interface_Cpp/build/Debug/RP_LiDAR_Interface_Cpp"
            sharedMemoryPath = r"/tmp/boost_interprocess/RP_LiDAR_Shared_Memory"

        print(f"-- INFO -- LiDAR Device: {lidarDevice}")

        self.p = subprocess.Popen(
            [interfacePath, lidarDevice],
            stdout=subprocess.PIPE,
            text=True
        )

        time.sleep(3)

        print("-- INFO -- Starting RP_LiDAR_Interface, if the application hangs for an unreasonable amount of time")
        output = self.p.stdout.read(1)
        while (output.find("Scanning") == -1):
            print(f"-- INFO -- Begin RP_LiDAR_Interface STDOUT: {output}", end='\r')
            if (self.p.poll() is None):  # Program still running
                output += self.p.stdout.read(1)
            else:
                print(f"-- ERROR -- RP_LiDAR_Interface has crashed with exit code {self.p.returncode} during startup!")
                exit(1)

        print(f"-- INFO -- End RP_LiDAR_Interface STDOUT")

        self.f = open(sharedMemoryPath, 'rb')

    def __del__(self):
        self.f.close()
        self.p.terminate()

    def getLatest(self) -> LiDARMeasurement:
        self.f.seek(0)
        timestampBytes = self.f.read(8)
        timestampInt = int.from_bytes(timestampBytes, 'little', signed=False)
        # print(f"TimestampBytes: {timestampBytes.hex()} TimestampInt: {timestampInt}")

        nodes = []
        nodeSizeBytes = 2 + 4 + 1 + 1
        for i in range(291):
            angleBytes = self.f.read(2)
            angleInt = int.from_bytes(angleBytes, 'little', signed=False)
            # print(f"AngleBytes: {angleBytes.hex()}")
            # print(f"AngleInt: {angleInt}\n")

            distBytes = self.f.read(4)
            distInt = int.from_bytes(distBytes, 'little', signed=False)
            # print(f"DistBytes: {distBytes.hex()}")
            # print(f"DistInt: {distInt}\n")

            qualityBytes = self.f.read(1)
            qualityInt = int.from_bytes(qualityBytes, 'little', signed=False)
            # print(f"QualityBytes: {qualityBytes.hex()}")
            # print(f"QualityInt: {qualityInt}\n")

            flagBytes = self.f.read(1)
            flagInt = int.from_bytes(flagBytes, 'little', signed=False)
            # print(f"FlagBytes: {flagBytes.hex()}")
            # print(f"FlagInt: {flagInt}\n\n")

            nodes.append(Node(angleInt, distInt, qualityInt, flagInt))

        return LiDARMeasurement(timestampInt, nodes)
