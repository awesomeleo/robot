#!/usr/bin/env python

import cv2

import vision

BLUE = (255, 50, 50)
GREEN = (50, 255, 50)
RED = (50, 50, 255)

STATIC = True

if STATIC:
    img = cv2.imread('grids.jpg')
    img = cv2.resize(img, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_LINEAR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    __, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    contours, __ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    markers = vision.main_loop(img, gray, contours)

    for marker in markers:
        id_pos = tuple(map(int, marker.polygon.min(axis=0)[0]))
        id_str = "id={id}".format(id=marker.id)
        cv2.drawContours(img, [marker.polygon], -1, GREEN, 2)
        cv2.putText(img, id_str, id_pos, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=0.6, color=RED)

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

        for marker in markers:
            id_pos = tuple(map(int, marker.polygon.min(axis=0)[0]))
            id_str = "id={id}".format(id=marker.id)
            cv2.drawContours(img, [marker.polygon], -1, GREEN, 2)
            cv2.putText(img, id_str, id_pos, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=0.6, color=RED)

        cv2.imshow('Main window', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()

cv2.destroyAllWindows()
