import unittest

import numpy as np

from signals.imu import (Orientation, Still, euler_xyz, mounting, qconj, qexp, qmul, relative,
                         rotate, swing_twist, to_byte)

DT = 1 / 120
UP = np.array([0.0, 0.0, 1.0])


def readings(q_true: np.ndarray, w_body_dps: np.ndarray, bias_dps=0.0):
    """What an IMU at q_true turning at w_body measures: its rate plus an offset, the force of
    standing still, 1 g up, in its own frame."""
    force = rotate(qconj(q_true), UP)
    return w_body_dps + bias_dps, force


def angle_between(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.degrees(np.linalg.norm(np.atleast_2d(np.asarray(
        __import__("signals.imu", fromlist=["qlog"]).qlog(qmul(qconj(a), b)))), axis=-1))


class TestOrientation(unittest.TestCase):
    def test_tilt_found_and_offset_learnt(self):
        q_true = qexp(np.radians([[30.0, 0, 0], [0, -45.0, 0]]))
        f = Orientation(2)
        bias = np.array([[1.0, -0.5, 0.0], [0.5, 1.0, 0.0]])            # °/s
        for _ in range(120 * 120):                                      # two minutes still
            w, a = readings(q_true, np.zeros((2, 3)), bias)
            f.step(w, a)
        tilt = np.degrees(np.arccos(np.clip(rotate(f.q, rotate(qconj(q_true), UP)) @ UP, -1, 1)))
        self.assertTrue(np.all(tilt < 0.5))
        up = rotate(qconj(q_true), UP)                      # only the offset across gravity shows
        perp = lambda v: v - np.sum(v * up, axis=1, keepdims=True) * up       # noqa: E731
        self.assertTrue(np.allclose(perp(np.degrees(f.bias)), perp(bias), atol=0.1))

    def test_turn_followed(self):
        f = Orientation(1)
        q = np.array([[1.0, 0, 0, 0]])
        w = np.array([[0.0, 0.0, 90.0]])                                # about the vertical
        for _ in range(240):
            q = qmul(q, qexp(np.radians(w) * DT))
            f.step(*readings(q, w))
        self.assertLess(angle_between(q, f.q)[0], 0.5)                  # 180° turned

    def test_tilting_while_turning(self):
        f = Orientation(1)
        q = np.array([[1.0, 0, 0, 0]])
        for k in range(600):
            w = np.array([[40 * np.sin(k / 60), 25 * np.cos(k / 45), 10.0]])
            q = qmul(q, qexp(np.radians(w) * DT))
            f.step(*readings(q, w))
        tilt = np.degrees(np.arccos(np.clip(rotate(f.q, rotate(qconj(q), UP)) @ UP, -1, 1)))
        self.assertLess(tilt[0], 1.0)

    def test_no_force_waits(self):
        f = Orientation(2)
        f.step(np.zeros((2, 3)), np.array([[0.0, 0, 0], [0, 0, 1.0]]))     # the first held, empty
        self.assertTrue(np.all(np.isfinite(f.q)))
        self.assertEqual(f.started.tolist(), [False, True])
        f.step(np.zeros((2, 3)), np.array([[1.0, 0, 0], [0, 0, 1.0]]))
        self.assertTrue(f.started.all())


class TestJoints(unittest.TestCase):
    def test_hinge_flexion(self):
        parent = qexp(np.radians([[0.0, 0, 20]]))                       # turned about the vertical
        mount_p, mount_c = qexp(np.radians([[10.0, -5, 3]])), qexp(np.radians([[-7.0, 4, 30]]))
        calib_p, calib_c = qmul(parent, qconj(mount_p)), qmul(parent, qconj(mount_c))
        m_p, m_c = mounting(calib_p, parent), mounting(calib_c, parent)
        for flex in (0.0, 30.0, 90.0, 130.0):
            child = qmul(parent, qexp(np.radians([[flex, 0, 0]])))
            sens_p, sens_c = qmul(parent, qconj(mount_p)), qmul(child, qconj(mount_c))
            rel = relative(qmul(sens_p, m_p), qmul(sens_c, m_c))
            self.assertTrue(np.allclose(euler_xyz(rel)[0], [flex, 0, 0], atol=1e-6))

    def test_swing_and_twist(self):
        axis = np.array([0.0, 1.0, 0.0])                                # the bone along y
        swing = qexp(np.radians([[40.0, 0, 0]]) + np.radians([[0, 0, 20.0]]))
        twist = qexp(np.radians([[0, 30.0, 0]]))
        s = swing_twist(qmul(swing, twist), axis)[0]
        u = np.cross(axis, [1.0, 0, 0])
        u /= np.linalg.norm(u)
        v = np.cross(axis, u)
        sv = np.degrees(np.array([40.0, 0, 20.0]) * np.pi / 180)
        self.assertAlmostEqual(s[2], 30.0, places=6)
        self.assertAlmostEqual(s[0], sv @ u, places=6)
        self.assertAlmostEqual(s[1], sv @ v, places=6)
        rest = qexp(np.radians([[0, 0, 45.0]]))
        s0 = swing_twist(rest, axis, rest)[0]
        self.assertTrue(np.allclose(s0, 0, atol=1e-6))

    def test_bytes(self):
        self.assertEqual(to_byte([0.0, 70.0, 140.0, -5.0, 150.0], 0, 140).tolist(),
                         [0, 128, 255, 0, 255])


class TestStill(unittest.TestCase):
    def test_offset_when_still(self):
        s = Still(2)
        rng = np.random.default_rng(1)
        off = np.array([[0.7, -0.3, 0.2], [-0.4, 0.5, 1.1]])
        for _ in range(130):
            s.feed(off + rng.normal(0, 0.1, (2, 3)))
        self.assertTrue(np.allclose(s.offset, off, atol=0.05))
        moving = Still(1)
        for k in range(130):
            moving.feed(np.array([[30 * np.sin(k / 10), 0, 0]]))
        self.assertTrue(np.allclose(moving.offset, 0))


if __name__ == "__main__":
    unittest.main()
