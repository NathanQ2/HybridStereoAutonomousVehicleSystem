from src.main.poseEstimator.CameraProperties import CameraProperties


class Config:
    """Provides a way for user to define system configuration"""
    def __init__(self, lCameraProps: CameraProperties, rCameraProps: CameraProperties, lidarDevice: str, modelPath: str, visualizerPath: str):
        self.leftCameraProperties = lCameraProps
        self.rightCameraProperties = rCameraProps
        self.lidarDevice = lidarDevice
        self.modelPath = modelPath
        self.visualizerPath = visualizerPath

    @staticmethod
    def fromJson(d):
        return Config(
            CameraProperties.fromJson(d["leftCameraProperties"]),
            CameraProperties.fromJson(d["rightCameraProperties"]),
            d["lidarDevice"],
            d["modelPath"],
            d["visualizerPath"]
        )
