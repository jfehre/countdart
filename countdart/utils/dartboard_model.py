"""Utility functions for dartboard model"""
import re
from typing import Tuple

import numpy as np


class DartboardModel:
    """This Model describes the dartboard.
    It defines all lines and segments of a typical dartboard
    in a new coordinate system, where bull eye is (0, 0).
    It is used to get specific points for calibration,
    or to return the score of a given point in the dartboard
    coordinate system
    """

    outer_double_ring = 170
    inner_double_ring = 162
    outer_triple_ring = 107
    inner_triple_ring = 99
    bull = 31.8 / 2
    double_bull = 12.7 / 2

    # definition of segments inside the circle
    degree_of_segment = 18
    start_degree = degree_of_segment / 2
    point_mapping = [
        20,
        1,
        18,
        4,
        13,
        6,
        10,
        15,
        2,
        17,
        3,
        19,
        7,
        16,
        8,
        11,
        14,
        9,
        12,
        5,
    ]

    def get_translation_vector(self) -> np.ndarray:
        """Returns translation vector to translate 0, 0 to the top left
        corner.

        Returns:
            np.ndarray: Translation vector
        """
        return np.array([[1, 0, 350], [0, 1, 350], [0, 0, 1]])

    def get_outer_point(self, label: str) -> Tuple[int, int, int]:
        """Returns coordinates of the outer crosspoint in the dartboard
        coordinate system, between two given segments.
        The segments are given as a string in the format "s1 | s2",
        where s1 and s2 needs to be in range [1, 20].

        Args:
            label (str): the two segments

        Raises:
            ValueError: if the label contains not exactly two int
            ValueError: if one int is not in range [1, 20]
            ValueError: if the crosspoint is not valid in the
                dartboard model

        Returns:
            Tuple[int, int, int]: Returns point in dartboard coordinate
                system
        """
        # Extract point from label in format "int | int"
        match = re.match(r"^(\d+) \| (\d+)$", label)
        if match is None:
            raise ValueError(
                "Wrong format: The label has to be of the format 'int | int'"
            )
        a = int(match.group(1))
        b = int(match.group(2))
        # Check if both integers are valid (between 1 and 20)
        if not 1 <= a <= 20 or not 1 <= b <= 20:
            raise ValueError(
                "Out of range: All given numbers need to be in range [1, 20]"
            )
        a_idx = self.point_mapping.index(a)
        b_idx = self.point_mapping.index(b)
        if (a_idx + 1) % len(self.point_mapping) == b_idx:
            degree = self.start_degree + self.degree_of_segment * a_idx
        elif (a_idx - 1) % len(self.point_mapping) == b_idx:
            degree = self.start_degree + self.degree_of_segment * b_idx
        else:
            raise ValueError(f"Invalid label: {label} is not a valid cross point.")
        x = self.outer_double_ring * np.sin(np.radians(degree))
        y = self.outer_double_ring * np.cos(np.radians(degree))
        return (x, y)

    def get_score(self, point_2d: np.array) -> Tuple[str, int]:
        """Returns the score in a descriptional string and as integer,
        given a 2d point (x, y) in dartboard coordinate system.
        The descriptional string can contain:
         - M {segment} for a miss
         - S {segment} for single
         - D {segment} for double
         - T {segment} for triple
         - BULL for bull
         - D BULL for double bull


        Args:
            point_2d (np.ndarray[float, float]): 2d point in dartboard coordinate system

        Returns:
            Tuple[str, int]: descriptional string and score
        """
        distance = np.linalg.norm(point_2d)
        # get degree in range [0, 360]
        degree = np.rad2deg(np.arctan2(point_2d[0], point_2d[1])) % 360
        # calculate in which segment the point is, with help of start degree
        segment = (degree + self.start_degree) / self.degree_of_segment
        # get base_score from point mapping
        base_score = self.point_mapping[int(segment) % len(self.point_mapping)]
        # check if double, triple, bull or miss
        if distance > self.outer_double_ring:
            return f"M {base_score}", 0
        elif distance > self.inner_double_ring:
            return f"D {base_score}", 2 * base_score
        elif distance > self.inner_triple_ring and distance < self.outer_triple_ring:
            return f"T {base_score}", 3 * base_score
        elif distance > self.double_bull and distance < self.bull:
            return "BULL", 25
        elif distance < self.double_bull:
            return "D BULL", 50
        else:
            return f"S {base_score}", base_score
