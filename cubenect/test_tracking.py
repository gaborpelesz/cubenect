import numpy as np
import cubenect
import pyautogui

class InterfaceLogic:
    def __init__(self):
        self.hold = False
        # self.previous_center = None

    def print_action_callback(self, tracked_action_center):
        if not tracked_action_center is None:
            if not self.hold:
                self.hold = True
                print("clicking center:", tracked_action_center)
            else:
                print("holding center:", tracked_action_center)
        elif self.hold:
            self.hold = False
            print("Release...")

logic = InterfaceLogic()

with open("action_processing/test/videos/record_close_1610737635.npy", "rb") as f:
    depth_video = np.load(f)

cube = cubenect.Cubenect(dummy_loop_frames=depth_video, debug=True)
cube.run(action_callback=logic.print_action_callback)
