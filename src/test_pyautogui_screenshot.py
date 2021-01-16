import numpy as np
import cubenect
import cv2
import pyautogui

pyautogui.FAILSAFE = True

img = pyautogui.screenshot()
img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

cv2.namedWindow("test", cv2.WINDOW_FREERATIO)
cv2.imshow("test", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
