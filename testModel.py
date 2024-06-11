import cv2
from ultralytics import YOLO


def main():
    cam = cv2.VideoCapture(0)

    # Load the trained model
    model = YOLO("runs/detect/train3/weights/best.pt")

    while (True):
        ret, frame = cam.read()
        # cv2.imshow("raw frame", frame)

        results = model(frame)

        processedFrame = results[0].plot()

        cv2.imshow("Processed Frame", processedFrame)

        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break

    cam.release()

    cv2.destroyAllWindows()


if (__name__ == "__main__"):
    main()
