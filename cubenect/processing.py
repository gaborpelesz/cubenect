import abc

import cv2
import numpy as np

class ActionDetectionPipeline(abc.ABC):
    def __init__(self, debug=False):
        self.action_detected_frame = None
        self.is_debug = debug

    @abc.abstractmethod
    def detect(self, frame):
        """
        gets a depth map video frame and detects action on the canvas interface
        """
        raise NotImplementedError

class AdaptiveThresholdDetection(ActionDetectionPipeline):
    def detect(self, frame):
        # desaturate if necessary
        if len(frame.shape) > 2 and frame.shape[2] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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


        contours, _ = cv2.findContours(connected_close_components.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        action_contours = list(filter(lambda contour: cv2.contourArea(contour) < frame.shape[0]*frame.shape[1]*0.01, contours))

        if self.is_debug:
            action_detected_frame = np.full((*frame.shape[:2], 3), 0, dtype=np.uint8)

            for contour in action_contours:
                (x,y), radius = cv2.minEnclosingCircle(contour)
                cv2.circle(action_detected_frame, (int(x),int(y)), 7, (0,255,0), -1)

            self.action_detected_frame = action_detected_frame

        action_centers = []
        for action_contour in action_contours:
            M = cv2.moments(action_contour)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            action_centers.append((cX,cY))

        return action_centers