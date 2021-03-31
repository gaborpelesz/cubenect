import numpy as np
import cubenect
import multitouch_driver_mock as mock_mtd

mock_driver = mock_mtd.MultitouchDriverMock()


with open("action_processing/test/videos/record_close_1610737635.npy", "rb") as f:
#with open("action_processing/test/videos/record_close_1612111434.npy", "rb") as f:
    depth_video = np.load(f)

cube = cubenect.Cubenect(dummy_loop_frames=depth_video, debug=True, dummy_loop_frames_n=2000)
cube.run(contact_update_callback=mock_driver.print_action_callback)
