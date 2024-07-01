import cv2
from ultralytics import YOLO
from ultralytics.engine.results import Results

from poseEstimator.CameraProperties import CameraProperties

from src.main.util.Util import Util



class PoseEstimator:
    def __init__(self, cameraProps: tuple[CameraProperties, CameraProperties]):
        if (len(cameraProps) != 2):
            print(f"[ERR, PoseEstimator] Invalid number of camera properties! Got {len(cameraProps)} but expected 2.")
            exit(1)

        self.cameraProps = cameraProps
        self.baseline = cameraProps[0].x - cameraProps[1].x

    def update(self, frames: tuple[cv2.Mat, cv2.Mat], results: tuple[list[Results], list[Results]]):
        frame1 = frames[0]
        frame2 = frames[1]

        results1 = results[0]
        results2 = results[1]

        boxes1 = results1[0].boxes.xywh
        boxes2 = results2[0].boxes.xywh

        box1 = boxes1[0]
        box2 = boxes2[0]

        # (0, 640) -> (-1, 1) and (0, 480) -> (-1, 1)
        # ur = ((box1[0] / 640) - 0.5) * 2
        # vr = -((box1[1] / 480) - 0.5) * 2
        # ul = ((box2[0] / 640) - 0.5) * 2
        # vl = -((box2[1] / 480) - 0.5) * 2
        ur = box1[0] - (640 / 2)
        vr = box1[1] - (480 / 2)
        ul = box2[0] - (640 / 2)
        vl = box2[1] - (480 / 2)
        disparity = ul - ur

        # print(f"Right box: ({ur}, {vr})")
        # print(f"Left box: ({ul}, {vl})")
        # print(f"Baseline: {self.baseline}\nDisparity: {disparity}")
        # print(f"ur: {ur}, vr: {vr}, ul: {ul}, vl: {vl}")
        ray1 = self.findOutgoingRay(self.cameraProps[0], ur, vr)
        ray2 = self.findOutgoingRay(self.cameraProps[1], ul, vl)

        # x = (b(ul - ox)) / disparity
        # y = (b*fx(vl - oy)) / (fy*disparity)
        # z = b*fx / disparity

        x = (self.baseline * (ul - ray1[0])) / disparity
        y = -(self.baseline * self.cameraProps[0].cameraMatrix[0][0] * (vl - ray1[1])) / (self.cameraProps[0].cameraMatrix[1][1] * disparity)
        z = (self.baseline * self.cameraProps[0].cameraMatrix[0][0]) / disparity

        # print(f"POSE: ({x}, {y}, {z})")
        print(f"POSE: ({Util.metersToInches(x)}, {Util.metersToInches(y)}, {Util.metersToInches(z)})")

    def findOutgoingRay(self, cameraProps: CameraProperties, u: float, v: float):
        # cx = cameraProps.cameraMatrix[0][2]
        # cy = cameraProps.cameraMatrix[1][2]
        # print(f"cs: {cx}, cy: {cy}")

        # ray = ((u - cx) / cameraProps.cameraMatrix[0][0], (v - cy) / cameraProps.cameraMatrix[1][1], 1)
        ray = (-(u / (640 / 2)), -(v / (480 / 2)), 1)
        # print(f"Ray: ({ray[0]}, {ray[1]}, {ray[2]})")

        return ray
