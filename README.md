# Generic Autonomous Vehicle System
Pose estimation for autonomous vehicles using road signs. Not very user-friendly at the moment.

# How It Works
## Hardware
I chose to use two generic usb webcams in a stereo configuration with a baseline of ~190.5 millimeters. 
This allows us to do basic depth estimation using the difference between the two images.
At the moment, camera calibration constants can be found hard-coded in the [main.py](src/main/main.py) file.
## Software
### Sign Detection
Sign detection is done using a pre-trained YOLOv8 model for each camera.