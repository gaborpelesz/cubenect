import json
import os

class MultitouchDriver:
    def __init__(self, rotate_direction="clockwise"):
        self.current_commands = None

        config_file_path = './cubenect/config.json'
        if not os.path.exists(config_file_path):
            raise FileNotFoundError("Screen calibration config file was not found. Calibrate cubenect before using it.")

        with open(config_file_path, "r") as config_file:
            try:
                config = json.load(config_file)
            except Exception:
                print("ERROR: Can't understand json file, it is well formed?")
                raise Exception("ERROR: Can't understand json file, it is well formed?")

        self.calibrated_screen_parameters = config['SYNCH_CALIBRATION']

        # these can be hardcoded as kinect will
        # always send data in this format
        self.kinect_depth_height = 480
        self.kinect_depth_width  = 640

        virtual_driver_width_scale = 1024
        virtual_driver_height_scale = 1024

        self.rotate_direction = rotate_direction

        tl = self.calibrated_screen_parameters['TOP_LEFT']
        br = self.calibrated_screen_parameters['BOTTOM_RIGHT']
        window_width = self.calibrated_screen_parameters['WINDOW_WIDTH']
        window_height = self.calibrated_screen_parameters['WINDOW_HEIGHT']

        if self.rotate_direction == "clockwise":
            self.width_multiplier  = (br[0] - tl[0])/self.kinect_depth_height # scale on calibrated display
            self.width_multiplier *= virtual_driver_width_scale/window_width # scale to virtual driver

            self.height_multiplier  = (br[1] - tl[1])/self.kinect_depth_width # scale on calibrated display
            self.height_multiplier *= virtual_driver_height_scale/window_height # scale to virtual driver

        self.translate_x = tl[0] * virtual_driver_width_scale/window_width
        self.translate_y = tl[1] * virtual_driver_height_scale/window_height

    def transform_center(self, center):
        if self.rotate_direction == "clockwise":
            # rotate clockwise
            x = self.kinect_depth_height - center[1]
            y = center[0]

            # scale, with rotated kinect image
            x = int(self.width_multiplier * x)
            y = int(self.height_multiplier * y)

            # translate, with calibrated screen parameters
            x += self.translate_x
            y += self.translate_y

            return x, y

        raise NotImplementedError('Anti-clockwise 90 degree rotation is not implemented for the kinect')

    def freeup_slot(self, slot_id):
        freeup_commands = '\n'.join([f"s {slot_id}", "T -1", "0 0", ": 0", "e 0", "u 0", "S 0\n"])
        self.current_commands.append(freeup_commands)

    def activate_slot(self, slot_id):
        self.current_commands.append('\n'.join([f"s {slot_id}", "T {slot_id}", "0 10", ": 100", "e 0", "d 0", "S 0\n"]))

    def move(self, slot_id, center):
        x, y = self.transform_center(center)
        self.current_commands.append('\n'.join([f"s {slot_id}", f"X {x}", f"Y {y}", f"x {x}", f"y {y}", "a 1", "S 0\n"]))

    def multitouch_contact_callback(self, contact_tracker):
        self.current_commands = []
        for slot_id in range(len(contact_tracker.slots)):
            if contact_tracker.slots[slot_id].was_freed:
                self.freeup_slot(slot_id)
                contact_tracker.slots[slot_id].was_freed = False
            if contact_tracker.slots[slot_id].activate:
                self.activate_slot(slot_id)
                contact_tracker.slots[slot_id].activate = False
            if not contact_tracker.slots[slot_id].center is None:
                self.move(slot_id, contact_tracker.slots[slot_id].center)
        self.send_commands()

    def send_commands(self):
        commands = '\n'.join(self.current_commands)
        with open("/dev/virtual_touchscreen", "w") as f:
            f.write(commands)