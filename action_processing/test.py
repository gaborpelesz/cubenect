import numpy as np
import cv2

def contour_filtering(contours):
    def contour_filter(contour):
        contour_area = cv2.contourArea(contour)
        (x,y), radius = cv2.minEnclosingCircle(contour)
        min_circle_area = radius*radius * np.pi

        print("contour:", contour_area)
        print("circle:", min_circle_area)
        print("ratio:", contour_area/min_circle_area)
        print()

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

    if detected_blob is None or len(detected_blob) == 0:
        return frame

    contour_area = cv2.contourArea(detected_blob)
    (x,y), radius = cv2.minEnclosingCircle(detected_blob)
    min_circle_area = radius*radius * np.pi
    print("BLOB:")
    print("contour:", contour_area)
    print("circle:", min_circle_area)
    print("ratio:", contour_area/min_circle_area)
    print()

    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    #cv2.drawContours(frame, [detected_blob], -1, (0, 0, 255), 3)

    return frame

def main():
    frame = cv2.imread('test/images/frame_334.png', 0)
    frame = cv2.bitwise_not(frame)
    frame = process_frame(frame)

    cv2.namedWindow("depth video", cv2.WINDOW_FREERATIO)
    cv2.imshow("depth video", frame)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()