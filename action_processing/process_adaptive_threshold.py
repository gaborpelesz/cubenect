import os
import time
import numpy as np
import cv2

def cv2_window(image, title="debug"):
    cv2.namedWindow(title, cv2.WINDOW_FREERATIO)
    cv2.imshow(title, image)

def process_frame(frame):
    # desaturate if necessary
    if len(frame.shape) > 2 and frame.shape[2] == 3:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    _, otsu_mask = cv2.threshold(frame, 0, 255, cv2.THRESH_OTSU)
    # TODO if otsu value is different than average pixel value...
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

    cv2_window(connected_close_components, "debug")

    contours, _ = cv2.findContours(connected_close_components.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = list(filter(lambda contour: cv2.contourArea(contour) < frame.shape[0]*frame.shape[1]*0.01, contours))
    
    # detected_blob = contour_filtering(contours)

    action_detected_frame = np.full((*frame.shape[:2], 3), 0, dtype=np.uint8)
    # if detected_blob is None or len(detected_blob) == 0:
    #     return frame

    for contour in contours:
        (x,y), radius = cv2.minEnclosingCircle(contour)
        cv2.circle(action_detected_frame, (int(x),int(y)), 7, (0,255,0), -1)

    return action_detected_frame

if __name__ == "__main__":
    with open("test/videos/record_close_1610737635.npy", "rb") as f:
        depth_video = np.load(f)

    frameSize = depth_video.shape[1:]

    frame_id = 0
    fps_time = time.time()
    fps_in_sec = 0.05 # display new depth video in every 100 ms
    DO_THRESHOLD = False

    # background calibration
    BACKGROUND = depth_video[0]

    # ACTIONS DURING VIDEO
    #   press:
    #     - 'q' to quit
    #     - 'a' to print the current frame id
    #     - 's' to save the current frame
    #     - 't' to switch to global thresholding
    while True:
        if time.time() - fps_time > fps_in_sec:
            frame = depth_video[frame_id]

            # cv2.namedWindow("depth video", cv2.WINDOW_FREERATIO)
            # cv2.imshow("depth video", frame)

            if DO_THRESHOLD:
                frame = process_frame(frame)

            cv2_window(frame, "processed action")

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
                cv2.imwrite(frame_path, depth_video[frame_id-1])

    cv2.destroyAllWindows()