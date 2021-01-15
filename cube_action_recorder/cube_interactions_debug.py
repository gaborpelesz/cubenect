import freenect
import cv2
import signal
import numpy as np
import os
import time

import utils
import depth_transforms

KEEP_RUNNING = True # maybe reconsider as a singleton to follow OOP
IS_DEPTH_FORMAT_SET = False
NP_VIDEO_PACKETS = []
SAVE_VIDEO_CLOSE = False
SAVE_VIDEO_FAR = False

def depth(dev, depth, timestamp):
    global IS_DEPTH_FORMAT_SET, KEEP_RUNNING, SAVE_VIDEO_CLOSE, SAVE_VIDEO_FAR, NP_VIDEO_PACKETS

    if not IS_DEPTH_FORMAT_SET:
        freenect.set_depth_mode(dev, freenect.RESOLUTION_HIGH, freenect.DEPTH_REGISTERED)
        IS_DEPTH_FORMAT_SET = True
        print("Depth:")
        print(np.unique(depth))
        print(np.unique(depth).shape)
        return # this probably was the first frame -> continue to the next frame

    depth_close = depth_transforms.accurate_depth_image(depth, 545)
    depth_far = depth_transforms.accurate_depth_image(depth, 800)

    if SAVE_VIDEO_CLOSE:
        NP_VIDEO_PACKETS.append(depth_close)
    elif SAVE_VIDEO_FAR:
        NP_VIDEO_PACKETS.append(depth_far)

    utils.cv2_window_freeratio(depth_close, "54.5-80cm")
    utils.cv2_window_freeratio(depth_far, "80-105.5cm")

    # HANDLING KEYBOARD EVENTS
    #     - "q", "esc" -> quit program
    #     - "c"        -> start video close
    #     - "f"        -> start video far
    pressed_k = cv2.waitKey(10)
    if pressed_k in (27, ord("q")): # esc or "q" for quit
        KEEP_RUNNING = False
    elif pressed_k == ord("c"): # "c" start video close
        if SAVE_VIDEO_CLOSE and not SAVE_VIDEO_FAR:
            SAVE_VIDEO_CLOSE = False
            stop_recording(NP_VIDEO_PACKETS, "close")
            NP_VIDEO_PACKETS = []
        else:
            SAVE_VIDEO_CLOSE = True
            if SAVE_VIDEO_FAR:
                print("You are currently recording a long-range video. Stop it before trying...")
            else:
                print("Close-range recording has started...")
    elif pressed_k == ord("f"): # "f" start video far
        if SAVE_VIDEO_FAR and not SAVE_VIDEO_CLOSE:
            SAVE_VIDEO_FAR = False
            stop_recording(NP_VIDEO_PACKETS, "far")
            NP_VIDEO_PACKETS = []
        else:
            SAVE_VIDEO_FAR = True
            if SAVE_VIDEO_CLOSE:
                print("You are currently recording a close-range video. Stop it before trying...")
            else:
                print("Long-range recording has started...")

def video(dev, video, timestamp):
    return

def body(dev, ctx):
    global KEEP_RUNNING

    if not KEEP_RUNNING:
        freenect.set_tilt_degs(dev, 0)
        raise freenect.Kill

    # freenect.set_tilt_degs(dev, tilt)

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

def setup_handler():
    print('Press Ctrl-C in terminal to stop')
    signal.signal(signal.SIGINT, kill_handler) # ctrl-c to stop

def main():
    target_dir = "saved"
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

    setup_handler()

    freenect.runloop(body=body, video=video, depth=depth)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()