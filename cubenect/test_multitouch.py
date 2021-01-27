#!/usr/bin/python3
import cubenect
import multitouch_driver as mtd

print("initialize driver")
driver = mtd.MultitouchDriver()
print("driver initialized")

print("starting cubenect in debug mode")
cube = cubenect.Cubenect(debug=False)
print("running cubenect...")
cube.run(contact_update_callback=driver.multitouch_contact_callback)
print("exiting program")
