import signal
import time
import threading

import cv2
import freenect
import numpy as np

import processing
import utils

class Cubenect:
    def __init__(self, depth_calibration_start_mm=400,
                       calibration_objective=170,
                       calibration_error_epsilon=2,
                       calibration_mode="median",
                       debug=False,
                       dummy_loop_frames=None):
        self.keep_running = False

        # test the behavior of settings the depth
        # format in the body callback...
        self.is_depth_format_set = False

        # start depth calibration at 400mm default
        self.depth_calibrated_mm = depth_calibration_start_mm
        self.is_depth_calibrated = False
        self.calibration_error_epsilon = calibration_error_epsilon
        self.calibration_objective = calibration_objective
        if calibration_mode not in ("mean", "median"):
            calibration_mode = "median"
        self.calibration_mode = calibration_mode

        self.is_debug = debug
        self.dummy_loop_frames = dummy_loop_frames

        self.action_callback = None
        self.tracked_action = None
        self.pipeline = processing.AdaptiveThresholdDetection(debug=self.is_debug)

    def run(self, action_callback):
        self.keep_running = True

        self._setup_handlers()
        self.action_callback = action_callback

        if not self.dummy_loop_frames is None:
            self._run_dummy_loop()
        else:
            freenect.runloop(depth=self._depth_calibration,
                             body=self._body)

        cv2.destroyAllWindows() # if any

    def _tracking_action(self, new_centers, acceptance_radius=10):
        """For now only one action is being tracked in FIFO style"""

        # no new center --> stop tracking
        if len(new_centers) == 0:
            self.tracked_action = None
            return

        # no previous tracking --> start tracking with the first element in new center
        if self.tracked_action is None:
            self.tracked_action = new_centers[0] # maybe random choice?
            return

        acceptance_radius = acceptance_radius**10 # so squaring l2_norm to distance is not necessary

        closest = None
        closest_dist = float('inf')
        for new_center in new_centers:
            l2_norm = (self.tracked_action[0] - new_center[0])**2 + \
                      (self.tracked_action[1] - new_center[1])**2
            if l2_norm < closest_dist:
                closest = new_center
                closest_dist = l2_norm

        # tracking: if the closest new center is in the acceptance radius --> follow
        if closest_dist < acceptance_radius:
            self.tracked_action = closest
            return

        # else: lose tracked center
        self.tracked_action = None


    def _depth_callback(self, dev, depth, timestamp):
        frame = utils.create_accurate_depth_image(depth, from_mm=self.depth_calibrated_mm)

        if not self.is_depth_calibrated:
            self._depth_calibration(depth)
            return

        action_centers = self.pipeline.detect(frame)

        self._tracking_action(action_centers)

        action_thread = threading.Thread(target=self.action_callback, args=(self.tracked_action,))
        action_thread.start()

    def _body(self, dev, ctx):
        if not self.keep_running:
            freenect.set_tilt_degs(dev, 0)
            raise freenect.Kill

    def _setup_handlers(self):
        print('Press Ctrl-C in terminal to stop')
        signal.signal(signal.SIGINT, self.kill_handler) # ctrl-c to stop

    def kill_handler(self, signum, frame):
        self.keep_running = False

    def _depth_calibration(self, frame):
        error = self.calibration_error(frame)
        if error < self.calibration_error_epsilon:
            self.is_depth_calibrated = True
            print("Calibration finished! Feel free to make actions on the canvas interface.")
        else:
            self.depth_calibrated_mm += 1

    def calibration_error(self, frame):
        if self.calibration_mode == "median":
            return abs(np.median(frame) - self.calibration_objective)
        if self.calibration_mode == "mean":
            return abs(np.mean(frame) - self.calibration_objective)

    def _run_dummy_loop(self):
        frame_id = 0
        fps_in_sec = 0.025
        last_frame_time = time.time()

        while(self.keep_running):
            if time.time() - last_frame_time > fps_in_sec:
                frame = self.dummy_loop_frames[frame_id]
                action_centers = self.pipeline.detect(frame)
                self._tracking_action(action_centers)

                action_thread = threading.Thread(target=self.action_callback, args=(self.tracked_action,))
                action_thread.start()

                frame_id += 1
                if frame_id >= self.dummy_loop_frames.shape[0] - 1:
                    frame_id = 0
                last_frame_time = time.time()

                if self.is_debug:
                    if not self.pipeline.action_detected_frame is None:
                        utils.cv2_window_freeratio(frame, "debug frame")
                        utils.cv2_window_freeratio(self.pipeline.action_detected_frame, "debug detected action")

                pressed_key = cv2.waitKey(1)
                if pressed_key == ord('q'):
                    print("Quiting...")
                    self.keep_running = False
