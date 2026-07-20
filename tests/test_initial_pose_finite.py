# -*- coding: utf-8 -*-
import math
import unittest


def is_finite_pose_xy_yaw(x, y, yaw):
    """Mirror of scripts/tello_ros_driver.is_finite_pose_xy_yaw (keep in sync)."""
    try:
        return math.isfinite(float(x)) and math.isfinite(float(y)) and math.isfinite(float(yaw))
    except (TypeError, ValueError):
        return False


class TestInitialPoseFinite(unittest.TestCase):
    def test_finite_ok(self):
        self.assertTrue(is_finite_pose_xy_yaw(0.0, 1.5, -0.3))

    def test_nan_x(self):
        self.assertFalse(is_finite_pose_xy_yaw(float("nan"), 0.0, 0.0))

    def test_inf_y(self):
        self.assertFalse(is_finite_pose_xy_yaw(0.0, float("inf"), 0.0))

    def test_neginf_yaw(self):
        self.assertFalse(is_finite_pose_xy_yaw(0.0, 0.0, float("-inf")))

    def test_string_reject(self):
        self.assertFalse(is_finite_pose_xy_yaw("x", 0, 0))

    def test_none_reject(self):
        self.assertFalse(is_finite_pose_xy_yaw(None, 0, 0))

    def test_source_defines_helper(self):
        import os
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        src = open(os.path.join(root, "scripts", "tello_ros_driver.py"), encoding="utf-8").read()
        self.assertIn("def is_finite_pose_xy_yaw(x, y, yaw):", src)
        self.assertIn("is_finite_pose_xy_yaw(pose.position.x, pose.position.y, yaw)", src)


if __name__ == "__main__":
    unittest.main()
