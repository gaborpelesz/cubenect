import freenect
import cv2
import signal
import numpy as np
import utils
import depth_transforms

KEEP_RUNNING = True # maybe reconsider as a singleton to follow OOP
IS_DEPTH_FORMAT_SET = False

def depth(dev, depth, timestamp):
    global IS_DEPTH_FORMAT_SET, KEEP_RUNNING

    if not IS_DEPTH_FORMAT_SET:
        freenect.set_depth_mode(dev, freenect.RESOLUTION_HIGH, freenect.DEPTH_REGISTERED)
        IS_DEPTH_FORMAT_SET = True
        print("Depth:")
        print(np.unique(depth))
        print(np.unique(depth).shape)
        return # continue to the next frame

    depth_close = depth_transforms.accurate_depth_image(depth, 545)
    depth_far = depth_transforms.accurate_depth_image(depth, 800)
    
    utils.cv2_window_freeratio(depth_close, "54.5-80cm")
    utils.cv2_window_freeratio(depth_far, "80-105.5cm")

    if cv2.waitKey(10) == 27: # esc
        KEEP_RUNNING = False

    return

def video(dev, video, timestamp):
    return

def body(dev, ctx):
    global KEEP_RUNNING

    if not KEEP_RUNNING:
        freenect.set_tilt_degs(dev, 0)
        raise freenect.Kill

    # freenect.set_tilt_degs(dev, tilt)
    

def handler(signum, frame):
    """Sets up the kill handler, catches SIGINT"""
    global KEEP_RUNNING

    KEEP_RUNNING = False

if __name__ == "__main__":
    print('Press Ctrl-C in terminal to stop')
    signal.signal(signal.SIGINT, handler) # ctrl-c to stop

    freenect.runloop(body=body, video=video, depth=depth)
    cv2.destroyAllWindows()