import cv2
import time
from ultralytics import YOLO


def main():
    cam1 = cv2.VideoCapture(0)
    cam2 = cv2.VideoCapture(1)

    # Load the trained model
    model = YOLO("../../runs/detect/train/weights/best.pt")
    # model = YOLO(r"C:\Users\natet\OneDrive\Dev\Python\GenericAutonomousVehicleSystem\runs\detect\train\weights\best_saved_model\best_float32.tflite")
    frames = 0
    startTimeSecs = time.perf_counter()

    while (True):
        frameStartTimeSecs = time.perf_counter()
        ret1, frame1 = cam1.read()
        ret2, frame2 = cam2.read()
        # cv2.imshow("raw frame1", frame1)

        results1 = model.predict(frame1, conf=0.80)
        results2 = model.predict(frame2, conf=0.80)

        processedFrame1 = results1[0].plot()
        processedFrame2 = results2[0].plot()

        cv2.imshow("Processed Frame 1", processedFrame1)
        cv2.imshow("Processed Frame 2", processedFrame2)

        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break

        frameEndTimeSecs = time.perf_counter()
        frames += 1

        print(f"Frame time: {(frameEndTimeSecs - frameStartTimeSecs) * 1000}ms")
        print(f"FPS: {frames / (frameEndTimeSecs - startTimeSecs)}")

    cam1.release()

    cv2.destroyAllWindows()


if (__name__ == "__main__"):
    main()
