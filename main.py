#!/usr/bin/env python

import cv2

import vision


STATIC = True

if STATIC:
    img = cv2.imread('grids.jpg')
    img = cv2.resize(img, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_LINEAR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    __, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    contours, __ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    markers = vision.main_loop(img, gray, contours)

    cv2.imshow('Main window', img)
    cv2.waitKey(0)

else:
    cap = cv2.VideoCapture(0)

    while 1:
        __, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        __, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
        contours, __ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        markers = vision.main_loop(img, gray, contours)

        cv2.imshow('Main window', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()

cv2.destroyAllWindows()
