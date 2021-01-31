import cv2
import numpy as np

class CalibrationGUI:
    def __init__(self, window_size):
        self.window_width = window_size[0]
        self.window_height = window_size[1]
        self.step = 1
        self.next_step = { 1: 5,
                           5: 20,
                          20: 1 }

    def _draw_circle(self, frame, center):
        color = (0, 0, 255)
        #color = (44, 175, 98)
        #color = (245, 135, 66)

        frame = cv2.circle(frame, center, 5, color, -1)
        frame = cv2.circle(frame, center, 30, color, 10)

        return frame

    def change_step(self):
        self.step = self.next_step[self.step]

    def move(self, center, direction):
        center = list(center)
        # handle key codes
        if direction == 81: # LEFT
            center[0] -= self.step
        elif direction == 83: # RIGHT
            center[0] += self.step
        elif direction == 82: # UP
            center[1] -= self.step
        elif direction == 84: # DOWN
            center[1] += self.step
        else:
            return tuple(center)

        # deal with edge cases
        if center[0] < 0:
            center[0] = 0
        elif center[0] >= self.window_width:
            center[0] = self.window_width
        if center[1] < 0:
            center[1] = 0
        elif center[1] >= self.window_height:
            center[1] = self.window_height

        return tuple(center)

    def draw(self, center):
        frame = np.full((self.window_height, self.window_width, 3), 255, dtype=np.uint8)

        if center is not None:
            frame = self._draw_circle(frame, center)

        cv2.namedWindow("gui", cv2.WINDOW_NORMAL)
        #cv2.setWindowProperty("gui", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("gui", frame)
