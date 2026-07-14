# -*- coding: utf-8 -*-
import math
import unittest

from utils.move_bounds import (
    angle_to_sdk_degrees,
    clamp_video_duration_s,
    distance_meters_to_sdk_cm,
)


class TestDistance(unittest.TestCase):
    def test_ok_edges(self):
        self.assertEqual(distance_meters_to_sdk_cm(0.2), 20)
        self.assertEqual(distance_meters_to_sdk_cm(5.0), 500)

    def test_reject_range(self):
        with self.assertRaises(ValueError):
            distance_meters_to_sdk_cm(0.1)
        with self.assertRaises(ValueError):
            distance_meters_to_sdk_cm(6.0)

    def test_reject_non_finite(self):
        with self.assertRaises(ValueError):
            distance_meters_to_sdk_cm(float("nan"))
        with self.assertRaises(ValueError):
            distance_meters_to_sdk_cm(float("inf"))


class TestAngle(unittest.TestCase):
    def test_degrees_mode(self):
        self.assertEqual(angle_to_sdk_degrees(90), 90)
        self.assertEqual(angle_to_sdk_degrees(360), 360)

    def test_radians_mode(self):
        # pi/2 rad ~ 90 deg → int path
        self.assertEqual(angle_to_sdk_degrees(math.pi / 2), 90)

    def test_reject_non_finite(self):
        with self.assertRaises(ValueError):
            angle_to_sdk_degrees(float("nan"))


class TestDuration(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(clamp_video_duration_s(5), 5.0)

    def test_reject(self):
        with self.assertRaises(ValueError):
            clamp_video_duration_s(0)
        with self.assertRaises(ValueError):
            clamp_video_duration_s(200)
        with self.assertRaises(ValueError):
            clamp_video_duration_s(float("nan"))


if __name__ == "__main__":
    unittest.main()
