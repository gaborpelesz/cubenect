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

    #frame = np.full((*frame.shape[:2], 3), 0, dtype=np.uint8)
    if detected_blob is None or len(detected_blob) == 0:
        return frame

    (x,y), radius = cv2.minEnclosingCircle(detected_blob)
    cv2.circle(frame, (int(x),int(y)), 12, (0,255,0), -1)

    print("BLOB:")
    print("contour:", contour_area)
    print("circle:", min_circle_area)
    print("ratio:", contour_area/min_circle_area)
    print()

    cv2.drawContours(frame, [detected_blob], -1, (0, 0, 255), 3)

    return frame

def main():
    frame = cv2.imread('test/images/frame_105.png', 0)
    frame = process_frame(frame)

    cv2.namedWindow("depth video", cv2.WINDOW_FREERATIO)
    cv2.imshow("depth video", frame)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()