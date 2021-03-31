import cv2

def cv2_window_freeratio(img, title="<no title>"):
    cv2.namedWindow(title, cv2.WINDOW_FREERATIO)
    cv2.imshow(title, img)
