import abc

import cv2
import numpy as np

class ContactDetectionPipeline(abc.ABC):
    def __init__(self, debug=False):
        self.contact_detected_frame = None
        self.is_debug = debug

    @abc.abstractmethod
    def detect(self, frame):
        """
        gets a depth map video frame and detects contact on the canvas interface
        """
        raise NotImplementedError

class AdaptiveThresholdDetection(ContactDetectionPipeline):
    def __init__(self, debug=False):
        self.is_debug = debug
        self.kernel_3 = np.ones((3,3), np.uint8)
        self.kernel_5 = np.ones((5,5), np.uint8)
        self.contact_detected_frame = None

    def detect(self, frame):
        # desaturate if necessary
        if len(frame.shape) > 2 and frame.shape[2] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # create a more separate view of the not canvas objects and the canvas
        _, otsu_mask = cv2.threshold(frame, 0, 255, cv2.THRESH_OTSU)
        frame_inv = cv2.bitwise_not(frame)
        frame_objectnoise_zeroed = cv2.bitwise_and(frame_inv, otsu_mask) # object (mostly) noise zeroed, canvas is white

        # first adaptive threshold shows the object noise and the contacts
        # second adaptive threshold shows only the object noise
        # subtracting the two from eachother gives the contacts
        contact_highlighted_with_noise = cv2.adaptiveThreshold(frame_objectnoise_zeroed, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 53, -3)
        possible_noise = cv2.adaptiveThreshold(frame_objectnoise_zeroed, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 53, -20)
        possible_noise_extrapolated = cv2.dilate(possible_noise, self.kernel_3, iterations=20)
        contact_highlighthed_noise_eliminated = cv2.subtract(contact_highlighted_with_noise, possible_noise_extrapolated)

        # eliminate small noise in the contacts binary image
        # and close the contact components with kernel 5 dilation 3 times
        small_noise_eliminated = cv2.erode(contact_highlighthed_noise_eliminated, self.kernel_3, iterations=1)
        connected_close_components = cv2.dilate(small_noise_eliminated, self.kernel_5, iterations=3)

        # find contours and filter those that has smaller area than 1% of the total frame area
        contours, _ = cv2.findContours(connected_close_components.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contact_contours = list(filter(lambda contour: cv2.contourArea(contour) < frame.shape[0]*frame.shape[1]*0.01, contours))

        if self.is_debug:
            contact_detected_frame = np.full((*frame.shape[:2], 3), 0, dtype=np.uint8)

            for contour in contact_contours:
                (x,y), radius = cv2.minEnclosingCircle(contour)
                cv2.circle(contact_detected_frame, (int(x),int(y)), 7, (0,255,0), -1)

            self.contact_detected_frame = contact_detected_frame

        # calculate contact centers and propagate
        contact_centers = []
        for contact_contour in contact_contours:
            M = cv2.moments(contact_contour)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            contact_centers.append((cX,cY))

        return contact_centers
