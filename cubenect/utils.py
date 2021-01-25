import numpy as np
import cv2

def create_accurate_depth_image(depth_data: np.ndarray, from_mm: int):
    """ from a given milimeter, creates an image
        consisting of datapoints with 255 mm range
    """
    depth_data_translated = depth_data - from_mm

    # use the original depth data as a mask
    depth_data_translated[depth_data < from_mm] = 0
    depth_data_translated[depth_data > from_mm+255] = 255

    return depth_data_translated.astype(np.uint8)

def cv2_window_freeratio(img, title="<no title>"):
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, 640, 480)
    cv2.imshow(title, img)

def cv2_window(img, title="<no title>", resizeable=True, size=None):
    if resizeable:
        cv2.namedWindow(title, cv2.WINDOW_FREERATIO)
    else:
        if size is None:
            cv2.namedWindow(title, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(title, 640, 480)
        else:
            cv2.namedWindow(title, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(title, *size)
    cv2.imshow(title, img)
    