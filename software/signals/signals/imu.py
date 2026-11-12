"""The IMUs and the joints (bata/SIGNALS.md, *The IMUs and the joints*), every IMU at once, a
step at a time.

- **Orientation** a quaternion an IMU, w x y z, the body's frame turned into the world's (z up):
  each step's turn integrated, the tilt pulled towards gravity by a complementary filter of
  Mahony's kind (Mahony et al., IEEE Trans. Autom. Control 2008), the error the cross product of
  the measured force and the gravity the quaternion expects, proportional and integral, the
  integral the gyro's offset. No magnetometer: the turn about the vertical is free. The force is
  trusted only near 1 g, not while the limb accelerates.
- **Still:** while every IMU of a unit turns less than 2 °/s for a second, its gyro's offset is
  taken as the mean of that second, on top of the filter's integral; silent EMG may confirm it.
- **A joint** is the relative turn of two bones, each IMU turned into its bone by the
  calibration pose; out as angles about the bone's axes (flexion, abduction, rotation) or, for
  the shoulder and the hip, as a swing forward and out and a twist from a rest direction
  (porjadok/SOFTWARE.md, *Output*), each into a byte by its range from the joint table.
- **Not yet:** the joint's own constraints pinning the free turn about the vertical (Seel,
  Schauer and Raisch, IEEE CCA 2012); for the recordings.
"""
from __future__ import annotations

import numpy as np

STEP_S = 1 / 120
GYRO_DPS = 0.070          # 70 mdps/LSB at ±2000 dps (DS13510 Rev 4, table 3)
ACC_G = 0.000488          # 0.488 mg/LSB at ±16 g


# --- quaternions, w x y z, every function over arrays of them ---------------------------------

def qmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    aw, ax, ay, az = np.moveaxis(a, -1, 0)
    bw, bx, by, bz = np.moveaxis(b, -1, 0)
    return np.stack((aw * bw - ax * bx - ay * by - az * bz,
                     aw * bx + ax * bw + ay * bz - az * by,
                     aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw), axis=-1)


def qconj(q: np.ndarray) -> np.ndarray:
    return q * np.array([1.0, -1.0, -1.0, -1.0])


def qexp(rotvec: np.ndarray) -> np.ndarray:
    """The quaternion of a rotation vector, rad."""
    angle = np.linalg.norm(rotvec, axis=-1, keepdims=True)
    half = angle / 2
    with np.errstate(invalid="ignore", divide="ignore"):
        axis = np.where(angle > 1e-12, rotvec / angle, 0.0)
    return np.concatenate((np.cos(half), np.sin(half) * axis), axis=-1)


def qlog(q: np.ndarray) -> np.ndarray:
    """The rotation vector of a unit quaternion, rad, the short way round."""
    q = np.where(q[..., :1] < 0, -q, q)
    v = q[..., 1:]
    s = np.linalg.norm(v, axis=-1, keepdims=True)
    angle = 2 * np.arctan2(s, q[..., :1])
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(s > 1e-12, v / s * angle, 2 * v)


def rotate(q: np.ndarray, v: np.ndarray) -> np.ndarray:
    """v turned by q: the body's vector in the world's frame."""
    p = np.concatenate((np.zeros(v.shape[:-1] + (1,)), v), axis=-1)
    return qmul(qmul(q, p), qconj(q))[..., 1:]


# --- orientation ---------------------------------------------------------------------------

class Orientation:
    """N IMUs, `step` fed each step's mean turn rate in °/s and mean force in g, (N, 3) each."""

    def __init__(self, n: int, kp: float = 1.0, ki: float = 0.02, dt: float = STEP_S,
                 force_gate: float = 0.1) -> None:
        self.q = np.tile([1.0, 0.0, 0.0, 0.0], (n, 1))
        self.bias = np.zeros((n, 3))                     # rad/s, the filter's integral
        self.kp, self.ki, self.dt, self.gate = kp, ki, dt, force_gate
        self.started = np.zeros(n, bool)

    def start(self, force: np.ndarray) -> None:
        """Level from the first force near 1 g: the tilt at once, the turn about the vertical
        zero; an IMU with no force yet (its steps held from nothing) waits."""
        g = np.linalg.norm(force, axis=1)
        new = ~self.started & (np.abs(g - 1) < 0.5)
        if not new.any():
            return
        up = force[new] / g[new, None]
        z = np.array([0.0, 0.0, 1.0])
        axis = np.cross(up, z)                           # the body's up turned onto the world's
        s = np.linalg.norm(axis, axis=1, keepdims=True)
        angle = np.arctan2(s, up @ z[:, None])
        with np.errstate(invalid="ignore", divide="ignore"):
            rv = np.where(s > 1e-9, axis / s * angle, 0.0)
        self.q[new] = qexp(rv)
        self.started |= new

    def step(self, rate_dps: np.ndarray, force_g: np.ndarray) -> np.ndarray:
        if not self.started.all():
            self.start(force_g)
        w = np.radians(rate_dps)
        g = np.linalg.norm(force_g, axis=1, keepdims=True)
        a = force_g / np.maximum(g, 1e-9)
        expected = rotate(qconj(self.q), np.array([0.0, 0.0, 1.0]))   # up in the body's frame
        e = np.cross(a, expected) * (np.abs(g - 1) < self.gate)
        self.bias -= self.ki * e * self.dt
        w = w - self.bias + self.kp * e
        self.q = qmul(self.q, qexp(w * self.dt))
        self.q /= np.linalg.norm(self.q, axis=1, keepdims=True)
        return self.q


def from_steps(raw: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The IMU steps as the frames carry them, (..., 6) i16: the rate in °/s, the force in g."""
    raw = np.asarray(raw, float)
    return raw[..., :3] * GYRO_DPS, raw[..., 3:] * ACC_G


# --- the bones and the joints ---------------------------------------------------------------

def mounting(q_sensor: np.ndarray, q_bone: np.ndarray | None = None) -> np.ndarray:
    """Each IMU's turn into its bone, from the calibration pose: the bones as `q_bone` (the
    world's frame if none), the IMUs as measured then."""
    if q_bone is None:
        q_bone = np.tile([1.0, 0.0, 0.0, 0.0], (len(q_sensor), 1))
    return qmul(qconj(q_sensor), q_bone)


def relative(q_parent: np.ndarray, q_child: np.ndarray) -> np.ndarray:
    """The child bone's turn in the parent bone's frame."""
    return qmul(qconj(q_parent), q_child)


def euler_xyz(q: np.ndarray) -> np.ndarray:
    """Intrinsic angles about x, then y, then z, degrees: flexion, abduction, rotation for a
    joint whose range keeps away from y's ±90°."""
    w, x, y, z = np.moveaxis(q, -1, 0)
    ax = np.arctan2(2 * (w * x - y * z), 1 - 2 * (x * x + y * y))
    ay = np.arcsin(np.clip(2 * (w * y + x * z), -1, 1))
    az = np.arctan2(2 * (w * z - x * y), 1 - 2 * (y * y + z * z))
    return np.degrees(np.stack((ax, ay, az), axis=-1))


def swing_twist(q: np.ndarray, axis: np.ndarray, rest: np.ndarray | None = None) -> np.ndarray:
    """The shoulder's and the hip's three numbers, degrees: the swing as a rotation vector across
    the bone's `axis`, its two components (the first and the second of the axes orthogonal to it,
    forward and out), then the twist about the axis; all from `rest`."""
    if rest is not None:
        q = qmul(qconj(rest), q)
    axis = np.asarray(axis, float) / np.linalg.norm(axis)
    proj = (q[..., 1:] @ axis)[..., None] * axis
    twist = np.concatenate((q[..., :1], proj), axis=-1)
    twist /= np.linalg.norm(twist, axis=-1, keepdims=True)
    swing = qmul(q, qconj(twist))
    sv = np.degrees(qlog(swing))
    tv = np.degrees(qlog(twist)) @ axis
    u = np.cross(axis, [1.0, 0, 0] if abs(axis[0]) < 0.9 else [0, 1.0, 0])
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    return np.stack((sv @ u, sv @ v, tv), axis=-1)


def to_byte(deg: np.ndarray, low: float, high: float) -> np.ndarray:
    """A joint value into its byte, 0 and 255 the ends of its range (porjadok, *Output*)."""
    return np.clip(np.rint((np.asarray(deg) - low) / (high - low) * 255), 0, 255).astype(np.uint8)


class Still:
    """A unit's IMUs still for a second: each gyro's mean over it, its offset, °/s."""

    def __init__(self, n: int, limit_dps: float = 2.0, steps: int = 120) -> None:
        self.limit, self.steps = limit_dps, steps
        self.sum = np.zeros((n, 3))
        self.count = 0
        self.offset = np.zeros((n, 3))

    def feed(self, rate_dps: np.ndarray) -> np.ndarray:
        if np.all(np.linalg.norm(rate_dps - self.offset, axis=1) < self.limit):
            self.sum += rate_dps
            self.count += 1
            if self.count == self.steps:
                self.offset = self.sum / self.count
                self.sum[:], self.count = 0, 0
        else:
            self.sum[:], self.count = 0, 0
        return self.offset
