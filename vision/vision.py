#!/usr/bin/env python

import cv2
import numpy as np


SQUARE_PX = 60
WIDTH = SQUARE_PX * 5
HEIGHT = SQUARE_PX * 5

VALID_MARKERS = [
    [[1, 0, 1], [0, 0, 0], [0, 0, 1]],
    [[1, 0, 1], [0, 0, 1], [0, 0, 1]],
    [[1, 0, 1], [0, 0, 0], [0, 1, 1]],
    [[1, 1, 1], [0, 0, 0], [0, 0, 1]],
    [[1, 1, 1], [0, 0, 1], [0, 0, 1]],
    [[1, 1, 1], [0, 0, 0], [0, 1, 1]]
]


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
    return cross > 0


def parse_marker(marker):
    marker_data = np.zeros(shape=(3, 3), dtype=np.int)

    for row, j in zip(range(90, 240, SQUARE_PX), range(3)):
        for col, k in zip(range(90, 240, SQUARE_PX), range(3)):
            if marker[row, col] == 0:
                marker_data[j, k] = 0
            elif marker[row, col] == 255:
                marker_data[j, k] = 1

    return marker_data


def validate_marker(marker):
    for i, mat in enumerate(VALID_MARKERS):
        for rotations in range(4):
            if (marker == np.rot90(mat, rotations)).all():
                return True, i

    return False, None


class Marker:
    def __init__(self, marker_id, contour, polygon):
        self.id = marker_id
        self.contour = contour
        self.polygon = polygon
        self.position = self.__pos()
        self.x, self.y = self.position
        self.direction = None  # TODO

    def __pos(self):
        moments = cv2.moments(self.contour)
        cx = int(moments['m10']/moments['m00'])
        cy = int(moments['m01']/moments['m00'])
        return cx, cy


def main_loop(gray, contours):
    markers = list()

    for contour in contours:

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

        polygon_fl = np.float32(polygon)
        transform = cv2.getPerspectiveTransform(polygon_fl, trans_mat)
        sq_marker = cv2.warpPerspective(gray, transform, (WIDTH, HEIGHT))
        __, sq_marker_bin = cv2.threshold(sq_marker, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        if no_black_border(sq_marker_bin):
            continue

        marker = parse_marker(sq_marker_bin)
        valid_marker, marker_id = validate_marker(marker)

        if not valid_marker:
            continue

        markers.append(Marker(marker_id, contour, polygon))

    return markers