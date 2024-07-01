import time
import numpy as np
import cv2 as cv
from ultralytics import YOLO

from poseEstimator.PoseEstimator import PoseEstimator
from poseEstimator.CameraProperties import CameraProperties
from src.main.util.Util import Util


def main():
    cam1 = cv.VideoCapture(0)
    cam2 = cv.VideoCapture(1)

    cam1Properties = CameraProperties(
        "cam1",
        1920,
        1080,
        90,
        Util.inchesToMeters(4),
        0,
        cv.Mat(np.array([
            [1369.4881912538015, 0, 832.9337668370491],
            [0, 1378.0704791616597, 462.8089497112824],
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
    cam2Properties = CameraProperties(
        "cam1",
        1280,
        720,
        48.80887495,
        Util.inchesToMeters(-4),
        0,
        cv.Mat(np.array([
            [1354.2724948624088, 0, 701.0525651374418],
            [0, 1367.9151263124934, 460.5499004758408],
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

    poseEstimator = PoseEstimator((cam1Properties, cam2Properties))

    # Load the trained model
    model = YOLO("../../runs/detect/train/weights/best.pt")
    # model = YOLO(r"C:\Users\natet\OneDrive\Dev\Python\GenericAutonomousVehicleSystem\runs\detect\train\weights\best_saved_model\best_float32.tflite")
    frames = 0
    startTimeSecs = time.perf_counter()

    while (True):
        frameStartTimeSecs = time.perf_counter()
        ret1, frame1 = cam1.read()
        ret2, frame2 = cam2.read()

        frame1 = cv.undistort(frame1, cam1Properties.cameraMatrix, cam1Properties.distortionCoefficients)
        frame2 = cv.undistort(frame2, cam2Properties.cameraMatrix, cam2Properties.distortionCoefficients)

        results1 = model.predict(frame1, conf=0.70, verbose=False)
        results2 = model.predict(frame2, conf=0.70, verbose=False)

        processedFrame1 = results1[0].plot()
        processedFrame2 = results2[0].plot()

        if (len(results1[0].boxes) != 0 and len(results2[0].boxes) != 0):
            poseEstimator.update((frame1, frame2), (results1, results2))

        cv.imshow("Processed Frame1", processedFrame1)
        cv.imshow("Processed Frame2", processedFrame2)

        if (cv.waitKey(1) & 0xFF == ord('q')):
            break

        frameEndTimeSecs = time.perf_counter()
        frames += 1

        # print(f"Frame time: {(frameEndTimeSecs - frameStartTimeSecs) * 1000}ms")
        # print(f"FPS: {frames / (frameEndTimeSecs - startTimeSecs)}")

    cam1.release()
    cam2.release()

    cv.destroyAllWindows()


if (__name__ == "__main__"):
    main()
