#!/usr/bin/env python


import cv2
import tracker
import math

BLUE = (255, 50, 50)
GREEN = (50, 255, 50)
RED = (50, 50, 255)
WHITE = (255, 255, 255)

cap = cv2.VideoCapture(0)

target = (200, 200)

while True:
    __, img = cap.read()

    marker = tracker.find_marker_with_id(img, 1)

    if marker:
        a = (marker.cx - marker.major_axis[0], marker.cy - marker.major_axis[1])
        b = (marker.cx - target[0], marker.cy - target[1])
        ab = a[0]*b[0] + a[1]*b[1]
        na = math.sqrt(a[0]**2 + a[1]**2)
        nb = math.sqrt(b[0]**2 + b[1]**2)
        phi = math.floor(math.degrees(math.acos(ab/(na*nb))))

        cv2.line(img, marker.position, marker.major_axis, WHITE, 2)

        if math.sqrt((marker.cx - target[0])**2 + (marker.cy - target[1])**2) < 70:
            contour_color = GREEN
        else:
            contour_color = RED

        if phi < 10:
            deg_color = GREEN
        else:
            deg_color = RED

        cv2.drawContours(img, [marker.contour], -1, contour_color, 2)
        cv2.line(img, marker.position, target, deg_color, 2)
        cv2.circle(img, target, 80, contour_color, 2)
    else:
        cv2.circle(img, target, 80, RED, 2)


    cv2.imshow('Main window', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
