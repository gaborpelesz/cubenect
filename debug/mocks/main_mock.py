import numpy as np
import cubenect
import multitouch_driver as mtd

# action_processing/test/videos/record_close_1610737635.npy
file_path = f"{'/'.join(__file__.split('/')[:4])}/debug/action_processing/test/videos/record_close_1610737635.npy"

with open(file_path, "rb") as f:
    depth_video = np.load(f)

driver = mtd.MultitouchDriver()

cube = cubenect.Cubenect(dummy_loop_frames=depth_video, debug=False, dummy_loop_frames_n=1000)
cube.run(contact_update_callback=driver.multitouch_contact_callback)
print("exiting program")
