import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw

def putText_utf8(img, text, center):
    img_pil = Image.fromarray(img)
    ###

    # get a font
    fnt = ImageFont.load_default()
    # get a drawing context
    d = ImageDraw.Draw(img_pil)

    # draw text, half opacity
    d.text(center, text, font=fnt, fill=(0,0,0))
    ###
    img = np.array(img_pil)
    return img

class CalibrationGUI:
    def __init__(self, window_size):
        self.window_width = window_size[0]
        self.window_height = window_size[1]
        self.start_screen = True

        self.center_continue_circle = self.window_width//2, self.window_height//2

        self.circle_center_from_corner = 0.015 # ~50/3840

        center_from_corner = int(self.circle_center_from_corner*self.window_width)

        self.center_tl = center_from_corner, \
                         center_from_corner
        self.center_tr = self.window_width - center_from_corner, \
                         center_from_corner
        self.center_bl = center_from_corner, \
                         self.window_height - center_from_corner
        self.center_br = self.window_width - center_from_corner, \
                         self.window_height - center_from_corner

        self.is_calibrated = [False]*4
        self.is_pressed = [False]*4

        self.selected_corner = 0 # top_left

        self.corner_centers = [self.center_tl,
                               self.center_bl,
                               self.center_br,
                               self.center_tr]

    def _draw_calibration_circles(self, frame):
        for i in range(4):
            color = (0, 0, 255)
            if self.is_calibrated[i]:
                color = (44, 175, 98)
            elif self.is_pressed[i]:
                color = (245, 135, 66)

            frame = cv2.circle(frame, self.corner_centers[i], 5, color, -1)
            frame = cv2.circle(frame, self.corner_centers[i], 30, color, 10)

        return frame

    def _draw_continue_calibration(self, frame):
        frame = cv2.circle(frame, (self.window_width//2, self.window_height//2), 20, (3, 186, 252), -1)
        frame = cv2.circle(frame, (self.window_width//2, self.window_height//2), 80, (3, 186, 252), 50)
        return frame

    def _draw_cornertext(self, frame, center):
        print("NOT IMPLEMENTED WARNING: Calibration text drawing is not implemented.")
        return frame

    def next(self):
        if self.selected_corner > 3:
            return

        self.selected_corner += 1
        self.start_screen = False

    def press_tl(self):
        self.is_pressed[0] = True

    def press_bl(self):
        self.is_pressed[1] = True

    def press_br(self):
        self.is_pressed[2] = True

    def press_tr(self):
        self.is_pressed[3] = True

    def release_tl(self):
        self.is_pressed[0] = False

    def release_bl(self):
        self.is_pressed[1] = False

    def release_br(self):
        self.is_pressed[2] = False

    def release_tr(self):
        self.is_pressed[3] = False

    def calibrate_tl(self):
        self.is_calibrated[0] = True

    def calibrate_bl(self):
        self.is_calibrated[1] = True

    def calibrate_br(self):
        self.is_calibrated[2] = True

    def calibrate_tr(self):
        self.is_calibrated[3] = True

    def draw(self):
        frame = np.full((self.window_height, self.window_width, 3), 255, dtype=np.uint8)

        frame = self._draw_calibration_circles(frame)
        if self.start_screen:
            frame = self._draw_continue_calibration(frame)

        cv2.namedWindow("test", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("test", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("test", frame)