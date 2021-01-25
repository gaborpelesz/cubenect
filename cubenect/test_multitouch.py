import numpy as np
import cubenect
import multitouch_driver as mtd

class MultitouchDriver:
    def __init__(self):
        self.current_commands = None

        self.window_coordinates = { "left": 0,
                                    "top":  0 }
        self.kinect_depth_height = 480
        self.kinect_depth_width  = 640
        self.height_multiplier = 1024/self.kinect_depth_height
        self.width_multiplier  = 1024/self.kinect_depth_width

    def _translate_contact_center(self, center):
        x = center[0]*self.width_multiplier + self.window_coordinates['left']
        y = center[1]*self.height_multiplier + self.window_coordinates['top']
        return x, y

    def freeup_slot(self, slot_id):
        freeup_commands = '\n'.join([f"s {slot_id}", "T -1", "0 0", ": 0", "e 0", "u 0", "S 0\n"])
        self.current_commands.append(freeup_commands)

    def activate_slot(self, slot_id):
        self.current_commands.append('\n'.join([f"s {slot_id}", "T {slot_id}", "0 10", ": 100", "e 0", "d 0", "S 0\n"]))

    def move(self, slot_id, center):
        x, y = self._translate_contact_center(center)
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

class InterfaceLogic:
    def __init__(self):
        self.hold = False
        # self.previous_center = None
        self.window_coordinates = { "left": 0,
                                    "top": 0 }

        self.kinect_depth_height = 480
        self.kinect_depth_width = 640

        self.height_multiplier = 1024/self.kinect_depth_height
        self.width_multiplier = 1024/self.kinect_depth_width

    def mt_action_callback(self, tracked_action_center):
        slot = 4
        touch_id = 50
        if not tracked_action_center is None:
            x, y = self._translate_action_center(tracked_action_center)
            if not self.hold:
                self.hold = True
                t_event = mtd.touch(touch_id)
                m_event = mtd.move(x, y)
                pt = mtd.packet(t_event, slot)
                pm = mtd.packet(m_event, slot)
                mtd.send(pt+pm)
                #print("clicking center:", tracked_action_center)
            else:
                m_event = mtd.move(x, y)
                pm = mtd.packet(m_event, slot)
                mtd.send(pm)
                print("holding center:", tracked_action_center)
        elif self.hold:
            self.hold = False
            un = mtd.untouch()
            pun = mtd.packet(un, slot)
            mtd.send(pun)
            print("Release...")

    def _translate_action_center(self, action_center):
        x = action_center[0]*self.width_multiplier + self.window_coordinates["left"]
        y = action_center[1]*self.height_multiplier + self.window_coordinates["top"]
        return (x, y)

with open("action_processing/test/videos/record_close_1610737635.npy", "rb") as f:
    depth_video = np.load(f)

driver = MultitouchDriver()

cube = cubenect.Cubenect(dummy_loop_frames=depth_video, debug=False, dummy_loop_frames_n=1000)
cube.run(contact_update_callback=driver.multitouch_contact_callback)
