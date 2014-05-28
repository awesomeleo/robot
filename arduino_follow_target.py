#!/usr/bin/env python

import time
import serial
import cv2
import numpy as np
from lib import tracker

BLUE = (255, 50, 50)
GREEN = (50, 255, 50)
RED = (50, 50, 255)
WHITE = (255, 255, 255)


def main():
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
                ser.write('x')  # stop if inside target radius
                contour_color = GREEN
                deg_color = GREEN
            else:
                contour_color = RED

                if abs(phi) < 15:
                    ser.write('w')  # forward
                    deg_color = GREEN
                elif phi > 0 or abs(phi) > 131:
                    ser.write('a')  # left
                    deg_color = RED
                elif -130 < phi < 0:
                    ser.write('d')  # right
                    deg_color = RED

            cv2.drawContours(img, [robot.contour], -1, contour_color, 2)
            cv2.line(img, robot.position, target.position, deg_color, 2)
            cv2.line(img, robot.position, robot.major_axis, WHITE, 2)
            cv2.circle(img, target.position, radius, contour_color, 2)
            cv2.putText(img, "Angle: {ang}".format(ang=phi), (10, 40),
                        fontFace=cv2.FONT_HERSHEY_DUPLEX,
                        fontScale=0.6, color=deg_color)

        else:
            ser.write('x')  # stop

        elapsed = time.time() - start
        fps = 'FPS: {T}'.format(T=int(1 / elapsed))
        cv2.putText(img, fps, (10, 20),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                    fontScale=0.6, color=RED)

        cv2.imshow('Main window', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    serial_port = '/dev/tty.usbmodemfd131'
    ser = serial.Serial(serial_port, 9600)
    time.sleep(2)

    main()

    cap.release()
    cv2.destroyAllWindows()
