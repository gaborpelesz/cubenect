#!/bin/bash

# freenect and stuff
cd ~/ ""
sudo apt-get install python3-pip 
sudo -H pip3 install -r ~/cubenect/requirements.txt 
sudo apt-get install libusb-1.0.0-dev cmake pkg-config 
git clone https://github.com/gaborpelesz/libfreenect 
cd libfreenect 
mkdir build 
cd build 
cmake .. -DBUILD-PYTHON3=ON -DBUILD_EXAMPLES=OFF -DBUILD_FAKENECT=OFF 
sudo make install 
cd ../wrappers/python/ 
sudo python3 setup.py install 

# virtual touchscreen driver build and install
cd ~/ 
git clone https://github.com/gaborpelesz/virtual_touchscreen 
cd virtual_touchscreen 
sudo make 
sudo insmod virtual_touchscreen.ko
