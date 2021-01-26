#!/bin/sh
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>/home/digital/log_cubenect.out 2>&1
sleep 10

echo "Starting..."
sudo python3 /home/digital/cubenect/cubenect/test_multitouch.py
