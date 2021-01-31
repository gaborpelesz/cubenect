import cv2
import numpy as np
import subprocess
import calib_gui as gui
import threading
import cubenect


class CalibrationController:
    def __init__(self, rotate90=None):
        # get display size run: xrandr | grep '*'
        proc_1 = subprocess.Popen(['xrandr'], stdout=subprocess.PIPE)
        proc_2 = subprocess.Popen(['grep', '*'], stdin=proc_1.stdout, stdout=subprocess.PIPE)
        proc_1.stdout.close()
        # monitor params
        width, height = proc_2.communicate()[0].split()[0].decode("utf-8").split('x')
        width, height = int(width), int(height)

        proc_2.stdout.close()

        self.current_cubenect = None
        self.gui = gui.CalibrationGUI((width, height))
        self.keep_running = True

        self.stage = 1

        self.centers = [None, (0, 0), (width, height)]
        self.selected = 0 # tracking
        self.last_valid = None

        self.kinect_size = (640, 480)
        if rotate90 in ("left", "right"):
            self.scale_to_display = [height/self.kinect_size[1], width/self.kinect_size[0]]
        else:
            self.scale_to_display = [width/self.kinect_size[0], height/self.kinect_size[1]]
        self.rotate90 = rotate90

        self.top_left_calibrated = None
        self.bottom_right_calibrated = None

    def _save_calibration_data(self):
        print("Saving calibration data into file")

    def switch_calibration_stage(self):
                 # stage 1: start tracking top left
        self.stage += 1
        if self.stage == 2: # moving tl
            self.stop_tracking()
            self.centers[1] = self.last_valid if self.last_valid else (0, 0)
            self.selected = 1
                 # ... save center of top left tracking
                 # ... start moving circle top left
        elif self.stage == 3: # tracking br
            self.top_left_calibrated = self.centers[1]
            self.selected = 0
            self.init_tracking()
                 # ... save top left circle center
                 # ... start tracking bottom right
        elif self.stage == 4: # moving br
            self.stop_tracking()
            self.centers[2] = self.last_valid if self.last_valid else (self.gui.window_width, self.gui.window_height)
            self.selected = 2
                 # ... save center of bottom right
                 # ... start moving circle bottom right
        elif self.stage == 5: # saving exiting
            self.bottom_right_calibrated = self.centers[2]
            self._save_calibration_data()
            self.keep_running = False

            print("calibrated top:", self.top_left_calibrated)
            print("calibrated bottom:", self.bottom_right_calibrated)
                 # ... save bottom right circle center
                 # ... save calibration data
                 # ... stop loop

    def handle_keyboard_action(self, key_code):
        """ q -> abort
            SHIFT -> change circle moving speed (slow, medium, fast)
            ENTER -> next stage of the calibration
            Arrows -> move the calibration circles
        """

        if key_code == ord('q'):
            print("Aborting calibration")
            self.keep_running = False
            self.stop_tracking()
        elif key_code == 13: # ENTER
            self.switch_calibration_stage()

        elif self.stage in (2, 4):
            if key_code in (225, 226): # SHIFT: change step size
                self.gui.change_step()
            elif key_code in (81,82,83,84): # ARROWS: move accordingly
                self.centers[self.selected] = self.gui.move(self.centers[self.selected], key_code)
        elif key_code == -1:
            return
        else:
            print(f"Unknown keyboard command for stage {self.stage}: '{key_code}'")

    def handle_new_contact(self, contact_tracker):
        if len(contact_tracker.currently_active_slots) > 0:
            current_center = contact_tracker.slots[list(contact_tracker.currently_active_slots)[0]].center
            self.centers[0] = self.translate_contact(current_center)
            self.last_valid = self.centers[0]
        else:
            self.centers[0] = None

    def translate_contact(self, center):
        center = list(center)
        if self.rotate90 in ("left", "right"):
            if self.rotate90 == "left":
                center[0] = self.kinect_size[0] - center[0]
            elif self.rotate90 == "right":
                center[1] = self.kinect_size[1] - center[1]

            center = [center[1], center[0]]

        center = int(center[0]*self.scale_to_display[0]), int(center[1]*self.scale_to_display[1])
        #print(center)
        return center

    def run(self):
        self.init_tracking()

        while self.keep_running:
            self.gui.draw(self.centers[self.selected])
            k = cv2.waitKey(10)
            self.handle_keyboard_action(k)

    def init_tracking(self):
        self.current_cubenect = cubenect.Cubenect(debug=False)
        thread_stage = threading.Thread(target=self.current_cubenect.run, args=(self.handle_new_contact, ))
        thread_stage.start()

    def stop_tracking(self):
        if self.current_cubenect:
            self.current_cubenect.keep_running = False


if __name__ == "__main__":
    controller = CalibrationController(rotate90="left")
    controller.run()
    cv2.destroyAllWindows()
