import time
import numpy as np
import cv2 as cv
from ultralytics import YOLO

from poseEstimator.PoseEstimator import PoseEstimator
from poseEstimator.CameraProperties import CameraProperties
from src.main.util.Util import Util


def main():
    rightCam = cv.VideoCapture(1)
    leftCam = cv.VideoCapture(0)

    rightCamProps = CameraProperties(
        "rightCam",
        1280,
        720,
        48.80887495,
        0.1905 / 2,
        Util.inchesToMeters(2.5) - Util.millimetersToMeters(15.00),
        Util.inchesToMeters(1),
        cv.Mat(np.array([
            [902.8483299082725, 0, 350.5262825687209],
            [0, 911.9434175416623, 307.03326698389384],
            [0, 0, 1]
        ])),
        cv.Mat(np.array([
            [0.003172203922427552],
            [0.35311385355303954],
            [0.017672315681720594],
            [0.011996156270444938],
            [-1.114603391809918]
        ]))
    )

    leftCamProps = CameraProperties(
        "leftCam",
        640,
        480,
        90,
        -0.1905 / 2,
        Util.inchesToMeters(2.5) - Util.millimetersToMeters(15.00),
        Util.inchesToMeters(1),
        cv.Mat(np.array([
            [608.6614183350229, 0, 277.64458894568304],
            [0, 612.4757685162931, 205.69286653834774],
            [0, 0, 1]
        ])),
        cv.Mat(np.array([
            [-0.33956942504037607],
            [0.12334483908902447],
            [-0.0021704463640817846],
            [0.0007264004080491259],
            [-0.028929626021268803]
        ]))
    )

    poseEstimator = PoseEstimator(rightCamProps, leftCamProps)

    # Load the trained model
    model = YOLO("../../runs/detect/train/weights/best.pt")
    frames = 0
    startTimeSecs = time.perf_counter()

    while (True):
        frameStartTimeSecs = time.perf_counter()

        rRet, rFrame = rightCam.read()
        lRet, lFrame = leftCam.read()

        rFrame = cv.undistort(rFrame, rightCamProps.calibrationMatrix, rightCamProps.distortionCoefficients)
        lFrame = cv.undistort(lFrame, leftCamProps.calibrationMatrix, leftCamProps.distortionCoefficients)

        rResults = model.predict(rFrame, conf=0.70, verbose=False)
        lResults = model.predict(lFrame, conf=0.70, verbose=False)

        processedRFrame = rResults[0].plot()
        processedLFrame = lResults[0].plot()

        if (len(rResults[0].boxes) != 0 and len(lResults[0].boxes) != 0):
            x, y, z, = poseEstimator.update(rFrame, lFrame, rResults, lResults)

            print(f"POSE: ({Util.metersToInches(x)}, {Util.metersToInches(y)}, {Util.metersToInches(z)})")

        cv.imshow("Processed Right Frame", processedRFrame)
        cv.imshow("Processed Left Frame", processedLFrame)

        if (cv.waitKey(1) & 0xFF == ord('q')):
            break

        frameEndTimeSecs = time.perf_counter()
        frames += 1

        # print(f"Frame time: {(frameEndTimeSecs - frameStartTimeSecs) * 1000}ms")
        # print(f"FPS: {frames / (frameEndTimeSecs - startTimeSecs)}")

    rightCam.release()
    leftCam.release()

    cv.destroyAllWindows()


if (__name__ == "__main__"):
    main()
