import signal
import time
import threading

import cv2
import freenect
import numpy as np

import tracker
import processing
import utils

class Cubenect:
    def __init__(self, flip=None,
                       depth_calibration_start_mm=400,
                       calibration_objective=170,
                       calibration_error_epsilon=2,
                       calibration_mode="median",
                       debug=False,
                       dummy_loop_frames=None,
                       dummy_loop_frames_n=100):
        self.keep_running = False

        # test the behavior of settings the depth
        # format in the body callback...
        self.is_depth_format_set = False

        # start depth calibration at 400mm default
        self.depth_calibrated_mm = depth_calibration_start_mm
        self.depth_calibrated_max_mm = 2000 # 2000mm is the max a kinect would be able to see
        self.is_depth_calibrated = False
        self.calibration_error_epsilon = calibration_error_epsilon
        self.calibration_objective = calibration_objective
        if calibration_mode not in ("mean", "median"):
            calibration_mode = "median"
        self.calibration_mode = calibration_mode

        # dummy loop and debug settings
        self.is_debug = debug
        self.dummy_loop_frames = dummy_loop_frames
        self.dummy_loop_frames_n = dummy_loop_frames_n

        self.contact_tracker = tracker.ContactTracker(max_slot=10, acceptance_radius=30)
        self.contact_update_callback = None
        self.contact_detection_pipeline = processing.AdaptiveThresholdDetection(flip=flip, debug=self.is_debug)

    def run(self, contact_update_callback):
        self.keep_running = True
        print("setting up handlers")
        #self._setup_handlers()
        print("save the contact update callback")
        self.contact_update_callback = contact_update_callback
        print("decide if dummy")
        if not self.dummy_loop_frames is None:
            self._run_dummy_loop()
        else:
            print("starting a prod loop")
            freenect.runloop(depth=self._depth_callback,
                             body=self._body)

        cv2.destroyAllWindows() # if any

    def _depth_callback(self, dev, depth, timestamp):
        depth_frame = utils.create_accurate_depth_image(depth, from_mm=self.depth_calibrated_mm)

        if not self.is_depth_calibrated:
            print("calibrating...", end="\r")
            if self.is_debug:
                utils.cv2_window(depth_frame, "calibration progress")
            
                pressed_key = cv2.waitKey(1)
                if pressed_key == ord('q'):
                    print("Quiting...")
                    self.keep_running = False

            self._depth_calibration(depth_frame)
            return

        contact_centers = self.contact_detection_pipeline.detect(depth_frame)
        self.contact_tracker.update(contact_centers)

        self.contact_update_callback(self.contact_tracker)

        if self.is_debug:
            if not self.contact_detection_pipeline.contact_detected_frame is None:
                utils.cv2_window(depth_frame, "debug frame")
                utils.cv2_window(self.contact_detection_pipeline.contact_detected_frame, "debug detected contact")

                pressed_key = cv2.waitKey(1)
                if pressed_key == ord('q'):
                    print("Quiting...")
                    self.keep_running = False

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
            print("Calibration finished! Feel free to make contacts on the canvas interface.")
            if self.is_debug:
                cv2.destroyAllWindows()
        elif self.depth_calibrated_mm < self.depth_calibrated_max_mm:
            self.depth_calibrated_mm += 1
        else:
            print("ERROR: Calibration failed, it exceeded the max mm limit. Aborting program.")
            self.keep_running = False

    def calibration_error(self, frame):
        if self.calibration_mode == "median":
            return abs(np.median(frame) - self.calibration_objective)
        if self.calibration_mode == "mean":
            return abs(np.mean(frame) - self.calibration_objective)

    def _run_dummy_loop(self):
        frame_id = 0
        fps_in_sec = 0.02
        last_frame_time = time.time()

        loop_i = 0
        while self.keep_running and loop_i < self.dummy_loop_frames_n:
            if time.time() - last_frame_time > fps_in_sec: # fps limit
                frame = self.dummy_loop_frames[frame_id]
                contact_centers = self.contact_detection_pipeline.detect(frame)
                self.contact_tracker.update(contact_centers)

                self.contact_update_callback(self.contact_tracker)

                frame_id += 1
                if frame_id >= self.dummy_loop_frames.shape[0] - 1:
                    frame_id = 0
                last_frame_time = time.time()

                if self.is_debug:
                    if not self.contact_detection_pipeline.contact_detected_frame is None:
                        utils.cv2_window_freeratio(frame, "debug frame")
                        utils.cv2_window_freeratio(self.contact_detection_pipeline.contact_detected_frame, "debug detected contact")

                    pressed_key = cv2.waitKey(1)
                    if pressed_key == ord('q'):
                        print("Quiting...")
                        self.keep_running = False

                loop_i += 1
