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


def parse_marker(marker):
    marker_data = np.zeros(shape=(3, 3), dtype=np.int)

    for row, j in zip(range(90, 240, 60), range(3)):
        for col, k in zip(range(90, 240, 60), range(3)):
            if marker[row, col] == 0:
                marker_data[j, k] = 0
            elif marker[row, col] == 255:
                marker_data[j, k] = 1

    return marker_data


def validate_marker(marker):
    markers = []
    markers.append([[1, 0, 1], [0, 0, 0], [0, 0, 1]])
    markers.append([[1, 0, 1], [0, 0, 1], [0, 0, 1]])
    markers.append([[1, 0, 1], [0, 0, 0], [0, 1, 1]])
    markers.append([[1, 1, 1], [0, 0, 0], [0, 0, 1]])
    markers.append([[1, 1, 1], [0, 0, 1], [0, 0, 1]])
    markers.append([[1, 1, 1], [0, 0, 0], [0, 1, 1]])

    for i, mat in enumerate(markers):
        for rotations in range(4):
            if (marker == np.rot90(mat, rotations)).all():
                return True, i

    return False, None


def main_loop(img, gray, contours):
    for i, cont in enumerate(contours):

        if small_area(cont):
            continue

        eps = 0.05 * cv2.arcLength(cont, closed=True)
        poly = cv2.approxPolyDP(cont, eps, closed=True)

        if not_quadrilateral(poly):
            continue

        if oriented_clockwise(poly):
            trans_mat = np.float32([[0, 0], [WIDTH, 0], [WIDTH, HEIGHT], [0, HEIGHT]])
        else:
            trans_mat = np.float32([[0, 0], [0, HEIGHT], [WIDTH, HEIGHT], [HEIGHT, 0]])

        poly_fl = np.float32(poly)
        pers_tr = cv2.getPerspectiveTransform(poly_fl, trans_mat)
        sq_marker = cv2.warpPerspective(gray, pers_tr, (WIDTH, HEIGHT))
        __, sq_marker_bin = cv2.threshold(sq_marker, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        if no_black_border(sq_marker_bin):
            continue

        marker_candidate = parse_marker(sq_marker_bin)
        valid_marker, marker_id = validate_marker(marker_candidate)

        if not valid_marker:
            continue

        # cv2.imshow('data {num}'.format(num=i), square_bin)

        id_pos = tuple(map(int, poly.min(axis=0)[0]))
        id_str = "id={id}".format(id=marker_id)

        cv2.drawContours(img, [poly], -1, GREEN, 2)
        cv2.putText(img, id_str, id_pos, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=0.6, color=RED)