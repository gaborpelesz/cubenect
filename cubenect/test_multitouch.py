import numpy as np
import cubenect
import multitouch_driver as mtd

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

logic = InterfaceLogic()

with open("action_processing/test/videos/record_close_1610737635.npy", "rb") as f:
    depth_video = np.load(f)

cube = cubenect.Cubenect(dummy_loop_frames=depth_video, debug=False, dummy_loop_frames_n=3000)
cube.run(action_callback=logic.mt_action_callback)
