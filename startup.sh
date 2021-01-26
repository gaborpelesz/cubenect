#!/bin/sh
chromium-browser --start-fullscreen --kiosk ~/WebGL-Fluid-Simulation/index.html & # force chromium to run in background
sleep 10
sudo python3 /home/$USER/cubenect/cubenect/test_multitouch.py
