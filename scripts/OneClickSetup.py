import os
import subprocess


def main():
    os.system('cls || clear')
    print("-- Auto Setup Running -- ")
    input("Please install the drivers and press enter when completed: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads")
    os.system('pip3 install ../requirements.txt')
    os.system(f'cd {os.path.dirname(os.path.realpath(__file__))}../vendor/RP_LiDAR_Interface_Cpp && mkdir build && cd build && cmake .. && cmake --build .')


if (__name__ == '__main__'):
    main()