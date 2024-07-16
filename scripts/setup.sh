#! /bin/bash

echo " -- Auto Setup Running --"
echo "Python version being used:"
python3 --version
echo "Please install PyTorch and press enter when completed: https://pytorch.org/get-started/locally/"
read -n 1 -s -r
echo "Please install the drivers and press enter when completed: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads"
read -n 1 -s -r
cd ../vendor/RP_LiDAR_Interface_Cpp || exit
mkdir build
cd build || exit
cmake ..
cmake --build .
cd ../../../
python3 -m pip install -r requirements.txt
read -s -r input
if [ "$input" == "y" ]; then
  python3 src/test/train.py
  echo "Setup completed. Press enter to continue."
else
  echo "Setup completed. Press enter to continue."
  read -n 1 -s -r
fi