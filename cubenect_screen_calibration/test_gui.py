import gui

import cv2
import subprocess

# run: xrandr | grep '*'
p = subprocess.Popen(['xrandr'], stdout=subprocess.PIPE)
p2 = subprocess.Popen(['grep', '*'], stdin=p.stdout, stdout=subprocess.PIPE)
p.stdout.close()

# monitor params
width, height = p2.communicate()[0].split()[0].decode("utf-8").split('x')
width, height = int(width), int(height)

gui_handler = gui.CalibrationGUI((width, height))

while True:
    gui_handler.draw()

    k = cv2.waitKey(0)
    if k == ord('q'):
        break
    elif k == ord('n'):
        gui_handler.next()
    elif k == ord('1'):
        gui_handler.press_tl()
    elif k == ord('2'):
        gui_handler.press_bl()
    elif k == ord('3'):
        gui_handler.press_br()
    elif k == ord('4'):
        gui_handler.press_tr()
    elif k == ord('c'):
        gui_handler.calibrate_tl()

cv2.destroyAllWindows()