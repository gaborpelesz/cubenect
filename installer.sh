#!/bin/bash

# update and upgrade everything
# important fixes for touchscreen are also present in those upgrades
sudo apt-get update
sudo apt-get upgrade

# freenect and stuff
cd ~/ 
sudo apt-get install -y python3-pip 
sudo -H pip3 install -r cubenect/requirements.txt 
sudo apt-get install -y libusb-1.0.0-dev cmake pkg-config 
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
# load in as a kernel module -> loads in every boot
sudo cp virtual_touchscreen.ko /lib/modules/`uname -r`
sudo depmod -a
sudo modprobe virtual_touchscreen
echo "virtual_touchscreen" | sudo tee /etc/modules-load.d/virtual_touchscreen.conf

# download fluid simulation
cd ~/
git clone https://github.com/gaborpelesz/WebGL-Fluid-Simulation

# download chrome-browser
sudo apt-get install -y chromium-browser
# set chromium the default browser: fixes unwanted header about it
xdg-settings set default-web-browser chromium-browser.desktop

# install and disable gestures
chmod +x ~/cubenect/disable_gestures_extension/install.sh
~/cubenect/disable_gestures_extension/install.sh

# creating chromium autostart
cd /home/$USER
chmod +x cubenect/starters/startup_chrome.sh
mkdir .config .config/autostart
echo "[Desktop Entry]
Type=Application
Exec=/home/$(echo $USER)/cubenect/starters/startup_chrome.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[en_US]=FluidSim
Name=FluidSim
Comment[en_US]=
Comment=" >> .config/autostart/fluid.desktop

# creating cubenect autostart
cd /home/$USER
chmod +x cubenect/starters/startup_cubenect.sh
mkdir .config .config/autostart
echo "[Desktop Entry]
Type=Application
Exec=/home/$(echo $USER)/cubenect/starters/startup_cubenect.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[en_US]=Cubenect
Name=Cubenect
Comment[en_US]=
Comment=" >> .config/autostart/cubenect.desktop

# set autologin for current user
sudo python3 ~/cubenect/autologin.py

# make python runnable by user without sudo
echo "$USER $HOSTNAME = (root) NOPASSWD: /usr/bin/python3" | sudo tee /etc/sudoers.d/cubenect

echo "Installation done. Restart and see if everything is working."

