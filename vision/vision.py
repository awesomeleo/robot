#!/usr/bin/env python

import cv2
import numpy as np

BLUE = (255, 50, 50)
GREEN = (50, 255, 50)
RED = (50, 50, 255)

SQUARE_PX = 60
WIDTH = SQUARE_PX * 5
HEIGHT = SQUARE_PX * 5


def small_area(region):
    return cv2.contourArea(region) < 1e2


def not_quadrilateral(points):
    return len(points) != 4


def no_black_border(region):
    left = cv2.mean(region[0:60])
    right = cv2.mean(region[240:300])
    top = cv2.mean(region[:, 0:60])
    bottom = cv2.mean(region[:, 240:300])
    mean = np.mean(left + right + top + bottom)
    return mean > 10


def oriented_clockwise(polygon):
    x0 = polygon[0][0][0]
    y0 = polygon[0][0][1]
    x1 = polygon[1][0][0]
    y1 = polygon[1][0][1]
    x2 = polygon[2][0][0]
    y2 = polygon[2][0][1]
    cross = (x1-x0)*(y2-y0) - (x2-x0)*(y1-y0)
    if cross > 0:
        return True
    else:
        return False


def main_loop(img, gray, contours):
    for i, contour in enumerate(contours):

        if small_area(contour):
            continue

        epsilon = 0.05 * cv2.arcLength(contour, closed=True)
        polygon = cv2.approxPolyDP(contour, epsilon, closed=True)

        if not_quadrilateral(polygon):
            continue

        if oriented_clockwise(polygon):
            transform_mat = np.float32([[0, 0], [WIDTH, 0], [WIDTH, HEIGHT], [0, HEIGHT]])
        else:
            transform_mat = np.float32([[0, 0], [0, HEIGHT], [WIDTH, HEIGHT], [HEIGHT, 0]])

        polygon_f = np.float32(polygon)
        M = cv2.getPerspectiveTransform(polygon_f, transform_mat)
        square = cv2.warpPerspective(gray, M, (WIDTH, HEIGHT))
        __, square_bin = cv2.threshold(square, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        if no_black_border(square_bin):
            continue

        bitmap_candidate = np.zeros(shape=(3, 3), dtype=np.int)

        for row, j in zip(range(90, 240, 60), range(3)):
            for col, k in zip(range(90, 240, 60), range(3)):
                if square_bin[row, col] == 0:
                    bitmap_candidate[j, k] = 0
                elif square_bin[row, col] == 255:
                    bitmap_candidate[j, k] = 1

        cv2.imshow('data {num}'.format(num=i), square_bin)

        print bitmap_candidate

        if (bitmap_candidate == [[1, 1, 1], [0, 0, 1], [0, 0, 1]]).all():
            marker_id = "id=L-block"
        else:
            marker_id = "id={num}".format(num=i)

        id_pos = tuple(map(int, polygon.min(axis=0)[0]))

        cv2.drawContours(img, [polygon], -1, GREEN, 2)
        cv2.putText(img, marker_id, id_pos, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=0.6, color=RED)
