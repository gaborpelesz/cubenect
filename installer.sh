#!/bin/bash

# freenect and stuff
cd ~/ 
sudo apt-get install python3-pip 
sudo -H pip3 install -r cubenect/requirements.txt 
sudo apt-get install libusb-1.0.0-dev cmake pkg-config 
git clone https://github.com/gaborpelesz/libfreenect 
cd libfreenect 
mkdir build 
cd build 
cmake .. -DBUILD-PYTHON3=ON -DBUILD_EXAMPLES=OFF -DBUILD_FAKENECT=OFF 
make
sudo make install 
cd ../wrappers/python/ 
sudo python3 setup.py install 

# virtual touchscreen driver build and install
cd ~/ 
git clone https://github.com/gaborpelesz/virtual_touchscreen 
cd virtual_touchscreen 
sudo make 
sudo insmod virtual_touchscreen.ko

# download fluid simulation
cd ~/
git clone https://github.com/gaborpelesz/WebGL-Fluid-Simulation

# download chrome-browser
sudo apt-get install chromium-browser
# set chromium the default browser: fixes unwanted header about it
xdg-settings set default-web-browser chromium-browser.desktop

# creating chromium autostart
cd /home/$USER
mkdir .config .config/autostart
echo "[Desktop Entry]
Type=Application
Exec=/home/$(echo $USER)/cubenect/startup.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[en_US]=Cubenect
Name=Cubenect
Comment[en_US]=
Comment=" >> .config/autostart/cubenect.desktop

echo "Installation done. Restart and see if everything is working."

