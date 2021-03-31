import freenect
import cv2
import signal
import numpy as np
import os
import time

import cube_action_recorder.utils as utils
import cube_action_recorder.depth_transforms as depth_transforms

KEEP_RUNNING = True # maybe reconsider as a singleton to follow OOP
IS_DEPTH_FORMAT_SET = False
NP_VIDEO_PACKETS = []
SAVE_VIDEO_CLOSE = False
SAVE_VIDEO_FAR = False
DEPTH_CALIBRATED = False
DEPTH_CALIBRATED_MM = 400

def calibrate_depth(frame, value=170, epsilon=2, mode="median"):
    # best with median - value 170 - epsilon 2
    #           mean   - value 160 - epsilon 3
    if mode == "median":
        return abs(np.median(frame) - value) < epsilon
    if mode == "mean":
        return abs(np.mean(frame) - value) < epsilon

def process_depth_frame(frame):
    # desaturate if necessary
    if len(frame.shape) > 2 and frame.shape[2] == 3:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # TODO check what happens if otsu value is different than average pixel value...
    _, otsu_mask = cv2.threshold(frame, 0, 255, cv2.THRESH_OTSU)
    frame_inv = cv2.bitwise_not(frame)
    frame_objectnoise_zeroed = cv2.bitwise_and(frame_inv, otsu_mask)

    kernel_3 = np.ones((3,3), np.uint8)
    kernel_5 = np.ones((5,5), np.uint8)

    action_highlighted_with_noise = cv2.adaptiveThreshold(frame_objectnoise_zeroed, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 53, -3)
    possible_noise = cv2.adaptiveThreshold(frame_objectnoise_zeroed, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 53, -20)
    possible_noise_extrapolated = cv2.dilate(possible_noise, kernel_3, iterations=20)
    action_highlighthed_noise_eliminated = cv2.subtract(action_highlighted_with_noise, possible_noise_extrapolated)

    small_noise_eliminated = cv2.erode(action_highlighthed_noise_eliminated, kernel_3, iterations=1)
    connected_close_components = cv2.dilate(small_noise_eliminated, kernel_5, iterations=3)

    utils.cv2_window_freeratio(connected_close_components, "DEBUG: adaptive result")

    contours, _ = cv2.findContours(connected_close_components.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = list(filter(lambda contour: cv2.contourArea(contour) < frame.shape[0]*frame.shape[1]*0.01, contours))

    action_detected_frame = np.full((*frame.shape[:2], 3), 0, dtype=np.uint8)

    for contour in contours:
        (x,y), radius = cv2.minEnclosingCircle(contour)
        cv2.circle(action_detected_frame, (int(x),int(y)), 7, (0,255,0), -1)

    return action_detected_frame

def depth(dev, depth, timestamp):
    global IS_DEPTH_FORMAT_SET, KEEP_RUNNING, SAVE_VIDEO_CLOSE, SAVE_VIDEO_FAR, NP_VIDEO_PACKETS, DEPTH_CALIBRATED, DEPTH_CALIBRATED_MM

    if not IS_DEPTH_FORMAT_SET:
        freenect.set_depth_mode(dev, freenect.RESOLUTION_HIGH, freenect.DEPTH_REGISTERED)
        IS_DEPTH_FORMAT_SET = True
        #print("Depth:")
        #print(np.unique(depth))
        #print(np.unique(depth).shape)
        return # this probably was the first frame -> continue to the next frame

    # manual set of the calibrated_MM
    #depth_close = depth_transforms.accurate_depth_image(depth, 545)

    depth_close = depth_transforms.accurate_depth_image(depth, DEPTH_CALIBRATED_MM)

    if SAVE_VIDEO_CLOSE:
        NP_VIDEO_PACKETS.append(depth_close)

    utils.cv2_window_freeratio(depth_close, "kinect depth map")

    if not DEPTH_CALIBRATED:
        if calibrate_depth(depth_close, value=170, epsilon=2, mode="median"):
            DEPTH_CALIBRATED = True
            print("Calibration finished! Feel free to make actions on the canvas interface.")
            #cv2.destroyWindow("calibrate MM")
        else:
            DEPTH_CALIBRATED_MM += 1
        return
    else:
        depth_close_detected_actions = process_depth_frame(depth_close)

        window_name_cm = f"{DEPTH_CALIBRATED_MM/10:.1f}-{DEPTH_CALIBRATED_MM/10 + 25.5:.1f}cm"
        
        utils.cv2_window_freeratio(depth_close_detected_actions, f"{window_name_cm} detected action")

    # HANDLING KEYBOARD EVENTS
    #     - "q", "esc" -> quit program
    #     - "v"        -> start video recording
    #     - "c"        -> start calibration
    pressed_k = cv2.waitKey(10)
    if pressed_k in (27, ord("q")): # esc or "q" for quit
        KEEP_RUNNING = False
    elif pressed_k == ord("v"): # "v" start video recording
        if SAVE_VIDEO_CLOSE:
            SAVE_VIDEO_CLOSE = False
            stop_recording(NP_VIDEO_PACKETS, "close")
            NP_VIDEO_PACKETS = []
        else:
            SAVE_VIDEO_CLOSE = True
            print("Close-range recording has started...")
    elif pressed_k == ord("c"): # "c" start calibration
        cv2.destroyWindow(window_name_cm)
        cv2.destroyWindow(f"{window_name_cm} detected action")
        DEPTH_CALIBRATED = False
        print("Calibration started...")

def video(dev, video, timestamp):
    return

def body(dev, ctx):
    global KEEP_RUNNING

    if not KEEP_RUNNING:
        freenect.set_tilt_degs(dev, 0)
        raise freenect.Kill

def stop_recording(video, title=""):
    if title != "":
        title += "_" # to separate from timestamp
    if type(video) == list:
        video = np.array(video)

    recording_id = f"{title}{int(time.time())}"
    with open(f"saved/record_{recording_id}.npy", "wb") as f:
        np.save(f, video)

    print(f"Recording saved with id: {recording_id}")
    print(f"Number of frames: {video.shape[0]}")

def kill_handler(signum, frame):
    """Sets up the kill handler, catches SIGINT"""
    global KEEP_RUNNING

    KEEP_RUNNING = False

def setup_handlers():
    print('Press Ctrl-C in terminal to stop')
    signal.signal(signal.SIGINT, kill_handler) # ctrl-c to stop

def main():
    target_dir = "saved"
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

    setup_handlers()

    print("Do NOT touch the canvas until the camera is not calibrated!")
    print("Calibration started...")
    freenect.runloop(body=body, video=video, depth=depth)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()