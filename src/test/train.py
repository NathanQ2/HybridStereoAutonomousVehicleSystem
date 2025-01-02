from ultralytics import YOLO
import os
import time


def main():
    startTime = time.time()

    print(f"CWD: {os.getcwd()}")

    model = YOLO("yolov8s.yaml")
    results = model.train(data=f"{os.getcwd()}/dataset/data.yaml", epochs=100, device='mps', batch=-0.90)
    results.export(format="-")

    endTime = time.time()
    print(f"Training time: {(endTime - startTime) / 60}mins")


if (__name__ == "__main__"):
    main()
