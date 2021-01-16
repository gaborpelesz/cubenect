import numpy as np
import cubenect
import pyautogui

pyautogui.FAILSAFE = True

class PyAtuoGUILogic:
    def __init__(self, starter_window_image_path):
        self.window_coordinates = pyautogui.locateOnScreen(starter_window_image_path)
        if not self.window_coordinates is None:
            print("Window found!")

        self.hold = False
        self.kinect_depth_height = 480
        self.kinect_depth_width = 640

        self.height_multiplier = self.window_coordinates.height/self.kinect_depth_height
        self.width_multiplier = self.window_coordinates.width/self.kinect_depth_width
        print(self.height_multiplier)
        print(self.width_multiplier)
        # self.previous_center = None

    def print_action_callback(self, tracked_action_center):
        if not tracked_action_center is None:
            tracked_action_center = self._translate_action_center(tracked_action_center)

            if not self.hold:
                self.hold = True
                print("clicking center:", tracked_action_center)
                pyautogui.mouseDown(x=tracked_action_center[0], y=tracked_action_center[1], button='left')
            else:
                pyautogui.moveTo(x=tracked_action_center[0], y=tracked_action_center[1], duration=0.001)
                print("holding center:", tracked_action_center)
        elif self.hold:
            self.hold = False
            pyautogui.mouseUp(x=5800, y=3500, button='left')
            print("Released...")

    def _translate_action_center(self, action_center):
        x = action_center[0]*self.width_multiplier + self.window_coordinates.left
        y = action_center[1]*self.height_multiplier + self.window_coordinates.top
        return (x, y)

logic = PyAtuoGUILogic('resources/fluid_window.png')

with open("action_processing/test/videos/record_close_1610737635.npy", "rb") as f:
    depth_video = np.load(f)

cube = cubenect.Cubenect(dummy_loop_frames=depth_video, debug=True)
cube.run(action_callback=logic.print_action_callback)
