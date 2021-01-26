#!/bin/sh
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>/home/digital/log_chromium.out 2>&1

chromium-browser --start-fullscreen --kiosk ~/WebGL-Fluid-Simulation/index.html & # force chromium to run in background
