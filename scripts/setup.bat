@echo off

ECHO -- Auto Setup Running --
ECHO Python version being used:
python3 --version
ECHO Please install PyTorch and press enter when completed: https://pytorch.org/get-started/locally/
PAUSE
ECHO Please install the drivers and press enter when completed: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads
PAUSE
CD ../vendor/RP_LiDAR_Interface_Cpp
MKDIR build
CD build
cmake ..
cmake --build .
CD ../../../
python3 -m pip install -r requirements.txt
SET /p input="Would you like to start training the model? (y/n)"
IF /I "%input%"=="y" (
    python3 src/test/train.py
    ECHO Setup completed. Press enter to continue.
    PAUSE
) ELSE (
    ECHO Setup completed. Press enter to continue.
    PAUSE
)