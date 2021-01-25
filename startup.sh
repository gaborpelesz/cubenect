#!/bin/sh
chromium-browser --start-fullscreen --kiosk ~/WebGL-Fluid-Simulation/index.html & # force chromium to run in background
sudo python3 /home/$USER/cubenect/cubenect/test_multitouch.py
