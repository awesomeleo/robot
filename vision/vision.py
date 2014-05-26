#!/usr/bin/env python

import cv2
import numpy as np


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
    markers = list()
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


class Marker:
    def __init__(self, id, contour, polygon):
        self.id = id
        self.contour = contour
        self.polygon = polygon


def main_loop(img, gray, contours):
    markers = list()

    for i, contour in enumerate(contours):

        if small_area(contour):
            continue

        eps = 0.05 * cv2.arcLength(contour, closed=True)
        polygon = cv2.approxPolyDP(contour, eps, closed=True)

        if not_quadrilateral(polygon):
            continue

        if oriented_clockwise(polygon):
            trans_mat = np.float32([[0, 0], [WIDTH, 0], [WIDTH, HEIGHT], [0, HEIGHT]])
        else:
            trans_mat = np.float32([[0, 0], [0, HEIGHT], [WIDTH, HEIGHT], [HEIGHT, 0]])

        poly_fl = np.float32(polygon)
        pers_tr = cv2.getPerspectiveTransform(poly_fl, trans_mat)
        sq_marker = cv2.warpPerspective(gray, pers_tr, (WIDTH, HEIGHT))
        __, sq_marker_bin = cv2.threshold(sq_marker, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        if no_black_border(sq_marker_bin):
            continue

        marker = parse_marker(sq_marker_bin)
        valid_marker, marker_id = validate_marker(marker)

        if not valid_marker:
            continue

        markers.append(Marker(marker_id, contour, polygon))

    return markers