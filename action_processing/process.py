import os
import time
import numpy as np
import cv2

def contour_filtering(contours):
    def contour_filter(contour):
        contour_area = cv2.contourArea(contour)
        (x,y), radius = cv2.minEnclosingCircle(contour)
        min_circle_area = radius*radius * np.pi

        if contour_area < 50:
            return False

        return contour_area/min_circle_area > 0.3

    filtered_contours = list(filter(contour_filter, contours))
    if len(filtered_contours) == 0:
        return None
    
    return filtered_contours[0]

def process_frame(frame):
    _, frame = cv2.threshold(frame, 155, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detected_blob = contour_filtering(contours)

    frame = np.full((*frame.shape[:2], 3), 0, dtype=np.uint8)
    if detected_blob is None or len(detected_blob) == 0:
        return frame

    (x,y), radius = cv2.minEnclosingCircle(detected_blob)
    cv2.circle(frame, (int(x),int(y)), 12, (0,255,0), -1)

    return frame

with open("test/videos/record_close_1610737635.npy", "rb") as f:
    depth_video = np.load(f)

frameSize = depth_video.shape[1:]

frame_id = 0
fps_time = time.time()
fps_in_sec = 0.05 # display new depth video in every 100 ms
DO_THRESHOLD = False

# ACTIONS DURING VIDEO
#   press:
#     - 'q' to quit
#     - 'a' to print the current frame id
#     - 's' to save the current frame
#     - 't' to switch to global thresholding
while True:
    if time.time() - fps_time > fps_in_sec:
        frame = depth_video[frame_id]

        cv2.namedWindow("depth video", cv2.WINDOW_FREERATIO)
        cv2.imshow("depth video", frame)

        if DO_THRESHOLD:
            frame = process_frame(frame)

        cv2.namedWindow("processed action", cv2.WINDOW_FREERATIO)
        cv2.imshow("processed action", frame)
        fps_time = time.time()
        frame_id += 1

    if frame_id >= depth_video.shape[0] - 1:
        frame_id = 0

    pressed_key = cv2.waitKey(1)
    if pressed_key == ord('q'): # press 'q' to quit
        break
    elif pressed_key == ord('a'):
        print(f"current frame:{frame_id}")
    elif pressed_key == ord('t'):
        if DO_THRESHOLD:
            DO_THRESHOLD = False
        else:
            DO_THRESHOLD = True
    elif pressed_key == ord('s'):
        frame_path = f"test/images/frame_{frame_id}.png"
        if not os.path.exists(frame_path):
            cv2.imwrite(frame_path, process_frame(depth_video[frame_id-1]))

cv2.destroyAllWindows()