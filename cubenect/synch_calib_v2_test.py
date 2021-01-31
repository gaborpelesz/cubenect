import cv2
import numpy as np
import subprocess
import gui
import threading
import cubenect


class CalibrationController:
    def __init__(self):
        # get display size run: xrandr | grep '*'
        proc_1 = subprocess.Popen(['xrandr'], stdout=subprocess.PIPE)
        proc_2 = subprocess.Popen(['grep', '*'], stdin=proc_1.stdout, stdout=subprocess.PIPE)
        proc_1.stdout.close()
        # monitor params
        width, height = proc_2.communicate()[0].split()[0].decode("utf-8").split('x')
        width, height = int(width), int(height)

        proc_2.stdout.close()

        self.gui = gui.CalibrationGUI((width, height))
        self.keep_running = True

        self.stage = 1

        self.centers = [None, (0, 0), (width, height)]
        self.selected = 0 # dont draw
        self.current_cubenect = None

    def _save_calibration_data(self):
        print("Saving calibration data into file")

    def switch_calibration_stage(self):
                 # stage 1: start tracking top left
        self.stage += 1
        if self.stage == 2: # moving tl
            self.stop_tracking()
            self.selected = 1
                 # ... save center of top left tracking
                 # ... start moving circle top left
        elif self.stage == 3: # tracking br
            self.init_tracking()
            self.selected = 0
                 # ... save top left circle center
                 # ... start tracking bottom right
        elif self.stage == 4: # moving br
            self.stop_tracking()
            self.centers[2] = (self.gui.window_width, self.gui.window_height) # mocking
            self.selected = 2
                 # ... save center of bottom right
                 # ... start moving circle bottom right
        elif self.stage == 5: # saving exiting
            self.keep_running = False
            self._save_calibration_data()
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
        elif key_code == 13: # ENTER
            self.switch_calibration_stage()

        elif self.stage in (2, 4):
            if key_code in (225, 226): # SHIFT: change step size
                self.gui.change_step()
            elif key_code in (81,82,83,84): # ARROWS: move accordingly
                self.centers[self.selected] = self.gui.move(self.centers[self.selected], key_code)
        else:
            print(f"Unknown keyboard command for stage {self.stage}: '{key_code}'")

    def handle_new_contact(self, contact_tracker):
        if len(contact_tracker.currently_active_slots) > 0:
            current_center = contact_tracker.slots(list(contact_tracker.currently_active_slots)[0]).center
            self.centers[0] = current_center

    def run(self):
        self.init_tracking()

        while self.keep_running:
            self.gui.draw(self.centers[self.selected])
            k = cv2.waitKey(0)
            self.handle_keyboard_action(k)

    def init_tracking(self):
        self.current_cubenect = cubenect.Cubenect(debug=False)
        thread_stage1 = threading.Thread(target=self.current_cubenect.run, args=self.handle_new_contact)
        thread_stage1.start()

    def stop_tracking(self):
        self.current_cubenect.keep_running = False


if __name__ == "__main__":
    controller = CalibrationController()
    controller.run()
    cv2.destroyAllWindows()
