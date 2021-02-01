#!/usr/bin/python3
import cubenect
import multitouch_driver as mtd
import utils

print("initialize driver")
driver = mtd.MultitouchDriver()
print("driver initialized")

print("starting cubenect in production, with 90 degree rotated kinect")
cube = cubenect.Cubenect(debug=False, flip=utils.CV2_VERTICAL_FLIP)
print("running cubenect...")
cube.run(contact_update_callback=driver.multitouch_contact_callback)
print("exiting program")
