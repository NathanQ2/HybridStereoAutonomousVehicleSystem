from ultralytics import YOLO
import os
import time


def main():
    startTime = time.time()

    print(f"CWD: {os.getcwd()}")

    model = YOLO("yolov8n.yaml")
    results = model.train(data=f"{os.getcwd()}/dataset/data.yaml", epochs=1000, device=[0], batch=-0.90)
    model.export(format="tflite")

    endTime = time.time()
    print(f"Training time: {(endTime - startTime) / 60}mins")


if (__name__ == "__main__"):
    main()
