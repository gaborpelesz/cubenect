import subprocess
import threading
import json
import os

import cv2

import cubenect
import calib_gui as gui
import utils

class CalibrationController:
    def __init__(self, rotate90=None):
        try:
            # get display size run: xrandr | grep '*'
            proc_1 = subprocess.Popen(['xrandr'], stdout=subprocess.PIPE)
            proc_2 = subprocess.Popen(['grep', '*'], stdin=proc_1.stdout, stdout=subprocess.PIPE)
            proc_1.stdout.close()
            # monitor params
            width, height = proc_2.communicate()[0].split()[0].decode("utf-8").split('x')
            width, height = int(width), int(height)
            proc_2.stdout.close()
        except FileNotFoundError:
            print("Can't get display size.")
            width, height = 2560, 1600
            print(f"Probably using Mac... Setting display to: {width}, {height}")

        self.current_cubenect = None
        self.gui = gui.CalibrationGUI((width, height))
        self.keep_running = True

        self.stage = 1

        self.centers = [None, (0, 0), (width, height)]
        self.selected = 0 # tracking
        self.last_valid = None

        self.kinect_size = (640, 480)
        self.rotate90 = rotate90

        self.top_left_calibrated = None
        self.bottom_right_calibrated = None

    def _save_calibration_data(self):
        if self.top_left_calibrated is None or self.bottom_right_calibrated is None:
            raise Exception("Calibration did not complete... Unknown error, possible bug.")

        print("calibrated top:", self.top_left_calibrated)
        print("calibrated bottom:", self.bottom_right_calibrated)

        config = {}
        config_file_path = './cubenect/config.json'
        print(f"Saving calibration data into file: {config_file_path}")
        if os.path.exists(config_file_path):
            with open(config_file_path, "r") as json_file:
                try:
                    config = json.load(json_file)
                except Exception:
                    print("Can't open previous configuration, creating a new one...")
                    config = {}

        config['SYNCH_CALIBRATION'] = {}
        config['SYNCH_CALIBRATION']['TOP_LEFT'] = self.top_left_calibrated
        config['SYNCH_CALIBRATION']['BOTTOM_RIGHT'] = self.bottom_right_calibrated
        config['SYNCH_CALIBRATION']['WINDOW_WIDTH'] = self.gui.window_width
        config['SYNCH_CALIBRATION']['WINDOW_HEIGHT'] = self.gui.window_height

        with open(config_file_path, "w") as json_file:
            json.dump(config, json_file)

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
                 # ... save bottom right circle center
                 # ... save calibration data
                 # ... stop loop

    def handle_keyboard_events(self, key_code):
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
            if self.rotate90 == "right":
                center[1] = self.kinect_size[1] - center[1] # rotate 1.
                center = [center[1], center[0]]             # rotate 2.
                center[0] = int(self.gui.window_width/self.kinect_size[1] * center[0])  # scale 1.
                center[1] = int(self.gui.window_height/self.kinect_size[0] * center[1]) # scale 2.
            elif self.rotate90 == "left":
                raise NotImplementedError

        return tuple(center)

    def run(self):
        self.init_tracking()

        # gui loop and keyboard action handling
        while self.keep_running:
            self.gui.draw(self.centers[self.selected])
            k = cv2.waitKey(10)
            self.handle_keyboard_events(k)

    def init_tracking(self):
        flip = utils.CV2_VERTICAL_FLIP if self.rotate90 in ("left", "right") else utils.CV2_HORIZONTAL_FLIP
        self.current_cubenect = cubenect.Cubenect(debug=False, flip=flip)
        thread_stage = threading.Thread(target=self.current_cubenect.run, args=(self.handle_new_contact, ))
        thread_stage.start()

    def stop_tracking(self):
        if self.current_cubenect:
            self.current_cubenect.keep_running = False


if __name__ == "__main__":
    controller = CalibrationController(rotate90="right")
    controller.run()
    cv2.destroyAllWindows()
