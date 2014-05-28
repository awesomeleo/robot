#!/usr/bin/env python

import time
import serial
import cv2
import numpy as np
import tracker

BLUE = (255, 50, 50)
GREEN = (50, 255, 50)
RED = (50, 50, 255)
WHITE = (255, 255, 255)

cap = cv2.VideoCapture(0)

ser = serial.Serial('/dev/tty.usbmodemfd131', 9600)
time.sleep(2)


#target = (200, 200)
radius = 80

while True:
    start = time.time()

    __, img = cap.read()

    robot = tracker.find_marker_with_id(img, 1)
    target = tracker.find_marker_with_id(img, 2)

    if robot and target:
        a = np.array(robot.major_axis)
        b = np.array(robot.position)
        c = np.array(target.position)
        phi = robot.angle_to_point(target.position)

        if np.linalg.norm(c - b) < radius - np.linalg.norm(b - a):
            contour_color = GREEN
            deg_color = GREEN
            ser.write('x')
        else:
            contour_color = RED

            if abs(phi) < 15:
                deg_color = GREEN
                ser.write('w')
            elif phi > 0 or abs(phi) > 131:
                ser.write('a')
                deg_color = RED
            elif -130 < phi < 0:
                ser.write('d')
                deg_color = RED

        cv2.drawContours(img, [robot.contour], -1, contour_color, 2)
        cv2.line(img, robot.position, target.position, deg_color, 2)
        cv2.line(img, robot.position, robot.major_axis, WHITE, 2)
        cv2.circle(img, target.position, radius, contour_color, 2)
        cv2.putText(img, "Angle: {ang}".format(ang=phi), (10, 40),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                    fontScale=0.6, color=deg_color)

    else:
        #cv2.circle(img, target.position, radius, RED, 2)
        ser.write('x')

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
