#!/usr/bin/env python

import time
import cv2
from lib import tracker

BLUE = (255, 50, 50)
GREEN = (50, 255, 50)
RED = (50, 50, 255)

STATIC = True

if STATIC:
    img = cv2.imread('images/test.jpg')
    img = cv2.resize(img, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_LINEAR)

    markers = tracker.find_markers(img)

    for marker in markers:
        marker_id = "id={id}".format(id=marker.id)
        cv2.drawContours(img, [marker.contour], -1, GREEN, 2)
        cv2.line(img, marker.position, marker.major_axis, BLUE, 2)
        cv2.putText(img, marker_id, (marker.cx - 25, marker.cy),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                    fontScale=0.6, color=RED)

    cv2.imshow('Main window', img)
    cv2.waitKey(0)

else:
    cap = cv2.VideoCapture(0)

    while True:
        start = time.time()

        __, img = cap.read()

        markers = tracker.find_markers(img)

        for marker in markers:
            marker_id = "id={id}".format(id=marker.id)
            cv2.drawContours(img, [marker.polygon], -1, GREEN, 2)
            cv2.line(img, marker.position, marker.major_axis, BLUE, 2)
            cv2.putText(img, marker_id, (marker.cx - 25, marker.cy),
                        fontFace=cv2.FONT_HERSHEY_DUPLEX,
                        fontScale=0.6, color=RED)

        elapsed = time.time() - start
        fps = 'FPS: {T}'.format(T=int(1 / elapsed))
        cv2.putText(img, fps, (10, 20),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                    fontScale=0.6, color=RED)

        cv2.imshow('Main window', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()

cv2.destroyAllWindows()
