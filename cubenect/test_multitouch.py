#!/usr/bin/python3
import os
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

print("initialize driver")
driver = MultitouchDriver()
print("driver initialized")

print("starting cubenect in debug mode")
cube = cubenect.Cubenect(debug=False)
print("running cubenect...")
cube.run(contact_update_callback=driver.multitouch_contact_callback)
print("exiting program")
