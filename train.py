from ultralytics import YOLO
import os
import time


def main():
    startTime = time.time()
    print(f"CWD: {os.getcwd()}")
    model = YOLO("yolov8n.yaml")
    results = model.train(data="dataset/data.yaml", epochs=100, device='mps', batch=32)
    model.export(format="tflite")
    endTime = time.time()
    print(f"Training time: {endTime - startTime}")


if (__name__ == "__main__"):
    main()
