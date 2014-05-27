#!/usr/bin/env python

import math
import time
import cv2
import numpy as np
import tracker

BLUE = (255, 50, 50)
GREEN = (50, 255, 50)
RED = (50, 50, 255)
WHITE = (255, 255, 255)

cap = cv2.VideoCapture(0)

target = (200, 200)

while True:
    start = time.time()

    __, img = cap.read()

    marker = tracker.find_marker_with_id(img, 5)

    if marker:
        a = np.array(marker.major_axis)
        b = np.array(marker.position)
        c = np.array(target)
        ba = a - b
        bc = c - b
        s = np.arctan2(*ba)
        if s < 0:
            s += 2*np.pi
        e = np.arctan2(*bc)
        if e < 0:
            e += 2*np.pi
        delta = e - s
        phi = math.floor(np.degrees(delta))

        if math.sqrt((marker.cx - target[0])**2 + (marker.cy - target[1])**2) < 70:
            contour_color = GREEN
        else:
            contour_color = RED

        if abs(phi) < 10:
            deg_color = GREEN
        else:
            deg_color = RED

        cv2.drawContours(img, [marker.contour], -1, contour_color, 2)
        cv2.line(img, marker.position, target, deg_color, 2)
        cv2.line(img, marker.position, marker.major_axis, WHITE, 2)
        cv2.circle(img, target, 80, contour_color, 2)
        cv2.putText(img, "Angle: {ang}".format(ang=phi), (10, 40), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=0.6, color=deg_color)

    else:
        cv2.circle(img, target, 80, RED, 2)

    elapsed = time.time() - start
    fps = 'FPS: {T}'.format(T=int(1 / elapsed))
    cv2.putText(img, fps, (10, 20), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=0.6, color=RED)

    cv2.imshow('Main window', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
