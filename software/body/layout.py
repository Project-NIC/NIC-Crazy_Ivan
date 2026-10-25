"""Bogatyr's layout on MakeHuman's base mesh (CC0): every module's eight P and eight N, its
reference and its bias, and the 48 IMUs, each put where bogatyr/CONSTRUCTION.md says, by the
bones' landmarks of an average body. The landmarks are estimates on this mesh, not measured.
Usage: layout.py base.obj layout.json"""
import json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from skin import V, tris, cast, J, unit

CM = 0.1                                   # the mesh is in decimetres
up, fwd = np.array([0, 1, 0.]), np.array([0, 0, 1.])
E, C = [], []                              # the places; the channels as pairs of places


def put(p, n, layer, module, pole=''):
    E.append(dict(p=[float(x) for x in p], n=[float(x) for x in n], layer=layer, pole=pole,
                  module=module))
    return len(E) - 1


def channel(module, P, N):
    """A channel, P and N given as (point, normal)."""
    C.append((put(*P, 'emg', module, 'P'), put(*N, 'emg', module, 'N')))


# --- the trunk and the head: rays from an axis inside -----------------------------------------

def zc(y):
    """The trunk's middle front to back at the height y."""
    f = cast(np.array([0.01, y, 10.]), -fwd)[0][2]
    b = cast(np.array([0.01, y, -10.]), fwd)[0][2]
    return (f + b) / 2


def round_(y, sx, ang, centre=None):
    """The skin at the height y, ang degrees from the front towards the side sx (90 the side,
    180 the back), seen from the trunk's middle or from a centre given."""
    o = np.array([0., y, zc(y)]) if centre is None else np.asarray(centre, float)
    r = np.radians(ang)
    return cast(o, np.array([sx * np.sin(r), 0, np.cos(r)]))


def back(x, y):
    return cast(np.array([x, y, zc(y)]), -fwd)


def front(x, y):
    return cast(np.array([x, y, zc(y)]), fwd)


# the spinous processes, an estimate: C7 by the mesh's neck joint, the sacrum by its hips, the
# thoracic ones evenly between, the lumbar a third of a vertebra apart more
yC7 = J('neck')[1] - 0.05
LEVEL = {'C%d' % k: yC7 + (7 - k) * 0.17 for k in range(2, 8)}
LEVEL.update({'T%d' % k: yC7 - k * 0.224 for k in range(1, 13)})
LEVEL.update({'L%d' % k: LEVEL['T12'] - k * 0.34 for k in range(1, 6)})
LEVEL.update({'S1': LEVEL['L5'] - 0.30, 'S2': LEVEL['L5'] - 0.52, 'S3': LEVEL['L5'] - 0.72})


HEAD = np.array([0., J('l-eye')[1] + 0.3, 0.15])         # inside the skull
NECK0, NECK1 = J('neck'), J('head')                       # the neck's axis


def spine(level, x=0.0):
    """A spinous process, or a place x beside it; the neck's from its own axis, not past the
    chin."""
    y = LEVEL[level]
    if level[0] == 'C':
        z = NECK0[2] + (y - NECK0[1]) / (NECK1[1] - NECK0[1]) * (NECK1[2] - NECK0[2])
        return cast(np.array([x + 0.003, y, z]), -fwd)
    return back(x + 0.003, y)


def neck(y, sx, ang):
    t = (y - NECK0[1]) / (NECK1[1] - NECK0[1])
    return round_(y, sx, ang, NECK0 + t * (NECK1 - NECK0))


def head(y, sx, ang):
    return round_(y, sx, ang, np.array([0., y, HEAD[2]]))


# --- the limbs: a point on the bone's axis, a ray across it -----------------------------------

class Limb:
    """A bone from A to B; angles from the gap's side g round the axis, positive towards f."""

    def __init__(self, A, B, g, f):
        self.A, self.B = np.asarray(A, float), np.asarray(B, float)
        self.a = unit(self.B - self.A)
        self.L = np.linalg.norm(self.B - self.A)
        self.g = unit(g - (g @ self.a) * self.a)
        self.f = unit(f - (f @ self.a) * self.a - (f @ self.g) * self.g)

    def at(self, t, ang, dt_cm=0.0):
        """t of the way from A to B, moved dt_cm centimetres along the bone."""
        t = t + dt_cm * CM / self.L
        r = np.radians(ang)
        return cast(self.A + t * (self.B - self.A), np.cos(r) * self.g + np.sin(r) * self.f)

    def ring(self, module, t, n, below_cm, above_cm=4):
        """n P evenly round at t, the gap between the last and the first; N 1, 3, 5... along,
        below; N 2, 4... half a place round and above."""
        step = 360 / n
        for k in range(n):
            ang = step * (k + 0.5)
            P = self.at(t, ang)
            N = self.at(t, ang, below_cm) if k % 2 == 0 else self.at(t, ang + step / 2, -above_cm)
            channel(module, P, N)


def segment_frame(sx):
    lat = np.array([sx, 0, 0.])
    return lat


# --- the landmarks of each side ---------------------------------------------------------------

def side(sx):
    s = 'l' if sx > 0 else 'r'
    lat = np.array([sx, 0, 0.])
    L = dict(sh=J(f'{s}-shoulder'), el=J(f'{s}-elbow'), wr=J(f'{s}-hand'),
             hip=J(f'{s}-upper-leg'), kn=J(f'{s}-knee'), an=J(f'{s}-ankle'),
             f1=J(f'{s}-finger-1-1'), f12=J(f'{s}-finger-1-2'), f2=J(f'{s}-finger-2-1'),
             f3=J(f'{s}-finger-3-1'), f5=J(f'{s}-finger-5-1'), ft1=J(f'{s}-foot-1'),
             ft2=J(f'{s}-foot-2'), lat=lat, s=s, sx=sx)
    L['acromion'] = cast(L['sh'], unit(up + 0.35 * lat))
    ulnar = L['f5'] - L['f2']
    hand_axis = (L['f2'] + L['f5']) / 2 - L['wr']
    dorsal = unit(np.cross(hand_axis, ulnar)) * sx
    if dorsal @ fwd > 0.5 or dorsal @ up < -0.5:
        dorsal = -dorsal
    L['ulnar'], L['dorsal'] = unit(ulnar), dorsal
    L['upperarm'] = Limb(L['sh'], L['el'], lat, fwd)          # gap outside, + towards the front
    L['forearm'] = Limb(L['el'], L['wr'], ulnar, dorsal)      # gap over the ulna, + to the back
    L['thigh'] = Limb(L['hip'], L['kn'], lat, fwd)            # gap over the iliotibial tract
    L['calf'] = Limb(L['kn'], L['an'], unit(fwd - 0.7 * lat), -lat)   # gap over the tibia
    return L


IMU = []


def imu(module, p_n):
    IMU.append(len(E))
    put(*p_n, 'imu', module)


def mid(a, b):
    return (np.asarray(a[0]) + np.asarray(b[0])) / 2


# --- the modules ------------------------------------------------------------------------------

def head_module():
    m = 'head'
    for sx in (1, -1):
        brow = J('l-eye')[1] + 0.3
        channel(m, head(brow, sx, 14), head(brow + 0.3, sx, 14))          # frontalis, mid brow
        channel(m, head(brow, sx, 30), head(brow + 0.3, sx, 30))          # its outer third
        channel(m, head(brow - 0.15, sx, 62), head(brow + 0.15, sx, 62))  # temporalis, front
        channel(m, head(brow + 0.15, sx, 92), head(brow + 0.15, sx, 115))  # above the ear
    put(*head(J('l-eye')[1] - 0.45, 1, 118), 'ref', m)                      # the mastoids
    put(*head(J('l-eye')[1] - 0.45, -1, 118), 'bias', m)
    imu(m, head(J('l-eye')[1] + 0.75, 1, 22))                  # the forehead, beside Míša
    imu(m, head(J('l-eye')[1] + 0.55, -1, 92))                             # above the ear


def neck_module():
    m = 'neck and upper back'
    for sx in (1, -1):
        L = side(sx)
        channel(m, neck(LEVEL['C6'], sx, 40), neck(LEVEL['C7'] - 0.05, sx, 25))   # SCM, low
        channel(m, neck(LEVEL['C2'] - 0.05, sx, 128), neck(LEVEL['C2'] + 0.22, sx, 112))  # splenius
        c7 = spine('C7')[0]
        p = (L['acromion'][0] + c7) / 2
        P = cast(np.array([p[0] * 0.6, p[1] - 0.5, p[2]]), unit(p - np.array([p[0] * 0.6, p[1] - 0.5, p[2]])))
        q = P[0] + 0.4 * unit(c7 - P[0])
        N = cast(np.array([q[0] * 0.6, q[1] - 0.5, q[2]]), unit(q - np.array([q[0] * 0.6, q[1] - 0.5, q[2]])))
        channel(m, P, N)                                                    # upper trapezius
        channel(m, spine('C4', 0.15 * sx), spine('C6', -0.15 * sx))        # extensors, across
    put(*spine('C7'), 'ref', m)
    put(*spine('T4'), 'bias', m)
    imu(m, spine('C2'))
    imu(m, spine('T2'))


def scapula_spine(L, k):
    """The k-th place out along the scapula's spine from its root, ~3.5 cm apart."""
    root = np.array([0.7 * L['sx'], LEVEL['T3']])
    tip = np.array([L['acromion'][0][0] * 0.92, L['acromion'][0][1] - 0.12])
    d = unit(tip - root)
    x, y = root + d * 0.35 * k
    return back(x, y)


def shoulder_module(sx):
    L = side(sx); m = 'shoulder ' + L['s']; ua = L['upperarm']
    # deltoid: anterior, middle (across to the posterior part), posterior; angles from outside
    channel(m, ua.at(0.08, 50), ua.at(0.08, 50, 4))
    channel(m, ua.at(0.2, 0), ua.at(0.2, -45, 3))
    channel(m, ua.at(0.08, -50), ua.at(0.08, -50, 4))
    # pectoralis major, clavicular part, across to the anterior deltoid
    channel(m, front(0.8 * sx, 5.05), front(1.25 * sx, 4.98))
    # trapezius middle and lower, latissimus, serratus
    channel(m, back(0.35 * sx, LEVEL['T3']), scapula_spine(L, 0))
    root = np.array([0.7 * sx, LEVEL['T3']]); t8 = np.array([0.0, LEVEL['T8']])
    p = root + (t8 - root) * 2 / 3; q = p + 0.4 * unit(root - p)
    channel(m, back(*p), back(*q))
    channel(m, round_(LEVEL['T7'] - 0.15, sx, 140), round_(LEVEL['T7'] + 0.25, sx, 128))
    channel(m, round_(4.0, sx, 92), round_(4.0, sx, 92 + (13 if sx > 0 else 17)))
    put(*scapula_spine(L, 1), 'bias', m)
    put(*scapula_spine(L, 2), 'ref', m)
    imu(m, scapula_spine(L, 3))
    imu(m, L['acromion'])
    imu(m, front(0.75 * sx, 5.28))                                         # the clavicle


def chest_module():
    m = 'chest and abdomen'
    for sx in (1, -1):
        out = 0.3 if sx > 0 else 0.4                                       # 3 cm on the left
        channel(m, front(0.6 * sx, 4.75), front((0.6 + out) * sx, 4.82))   # pectoralis, sternal
        channel(m, front(0.3 * sx, 1.8), front(0.3 * sx, 2.2))             # rectus abdominis
        channel(m, round_(2.9, sx, 62), round_(2.55, sx, 50))              # external oblique
        channel(m, front(0.85 * sx, 1.05), front(0.42 * sx, 0.98))         # internal oblique
    put(*front(0.003, 5.1), 'bias', m)                                     # the manubrium
    imu(m, front(0.003, 4.5))
    put(*front(0.003, 3.95), 'ref', m)                                     # above the xiphoid


def lower_back_module():
    m = 'lower back'
    for sx in (1, -1):
        channel(m, spine('T9', 0.35 * sx), spine('T11', -0.35 * sx))      # thoracic erectors
        channel(m, spine('L1', 0.35 * sx), spine('L2', -0.35 * sx))       # longissimus
        channel(m, spine('L2', 0.65 * sx), back(0.7 * sx, LEVEL['L2'] + 0.4))   # iliocostalis
        channel(m, spine('L5', 0.25 * sx), spine('L4', -0.25 * sx))       # multifidus
    put(*spine('L4'), 'ref', m)
    put(*spine('S3'), 'bias', m)
    imu(m, back(0.003, (LEVEL['T12'] + LEVEL['L1']) / 2))
    imu(m, spine('L3'))
    imu(m, spine('S1'))


ASIS_Y, CREST_Y, TROCH_Y = 1.2, 1.75, 0.5          # estimates on this mesh


def hip_module(sx):
    L = side(sx); m = 'hip ' + L['s']
    asis = front(0.95 * sx, ASIS_Y)[0]
    lat_ep = L['thigh'].at(0.97, 0)[0]
    p = asis + (lat_ep - asis) / 6; q = p + 0.4 * unit(lat_ep - asis)
    th = L['thigh']
    channel(m, cast(th.A + ((p - th.A) @ th.a) * th.a, unit(p - th.A - ((p - th.A) @ th.a) * th.a)),
            cast(th.A + ((q - th.A) @ th.a) * th.a, unit(q - th.A - ((q - th.A) @ th.a) * th.a)))
    channel(m, round_(0.95, sx, 75), round_(0.95, sx, 58))                # medius front -> TFL
    channel(m, round_((CREST_Y + TROCH_Y) / 2, sx, 98), round_((CREST_Y + TROCH_Y) / 2 - 0.4, sx, 98))
    channel(m, round_(CREST_Y - 0.15, sx, 112), round_(CREST_Y - 0.55, sx, 112))
    channel(m, round_(1.15, sx, 122), round_(1.15, sx, 142))              # medius back -> max.
    channel(m, round_(0.95, sx, 150), round_(0.62, sx, 140))              # maximus, outer
    channel(m, back(0.4 * sx, 0.85), back(0.62 * sx, 0.55))               # maximus, inner
    channel(m, round_(0.55, sx, 158), round_(1.0, sx, 135))               # maximus, low -> medius
    imu(m, round_(CREST_Y - 0.1, sx, 72))                                 # the iliac tubercle
    put(*round_(CREST_Y - 0.05, sx, 92), 'ref', m)
    put(*round_(TROCH_Y, sx, 92), 'bias', m)


def upper_arm_module(sx):
    L = side(sx); m = 'upper arm ' + L['s']; ua = L['upperarm']
    ua.ring(m, 0.5, 8, 4)
    imu(m, ua.at(0.9, 0))                                                  # above the epicondyle
    put(*ua.at(0.9, 0, -3), 'ref', m)
    put(*ua.at(0.9, 0, -6), 'bias', m)
    imu(m, ua.at(0.4, 0))                                                  # the deltoid's insertion
    imu(m, ua.at(0.88, 200))                                               # above the medial ep.
    imu(m, ua.at(0.86, 270))                                               # above the olecranon


def forearm_module(sx, glove):
    L = side(sx); m = 'forearm ' + L['s']; fa = L['forearm']
    fa.ring(m, 0.4, 5, 4)
    wr, d, u = L['wr'], L['dorsal'], L['ulnar']
    ax = unit((L['f2'] + L['f5']) / 2 - wr)
    c = wr + 0.62 * ((L['f1'] + L['f2']) / 2 - wr)                         # first dorsal interosseous
    channel(m, cast(c - ax * 0.1, d), cast(c + ax * 0.1, d))
    c = wr + 0.45 * (L['f12'] - wr); dd = unit(-u * 0.8 - d * 0.6)        # abductor pollicis brevis
    channel(m, cast(c - ax * 0.1, dd), cast(c + ax * 0.1, dd))
    c = wr + 0.5 * (L['f5'] - wr); dd = unit(u * 0.9 - d * 0.3)           # abductor digiti minimi
    channel(m, cast(c - ax * 0.1, dd), cast(c + ax * 0.1, dd))
    put(*fa.at(0.4, 0), 'ref', m)
    put(*fa.at(0.97, 0), 'bias', m)
    imu(m, fa.at(0.16, 10))                                                # the ulna, by the elbow
    imu(m, fa.at(0.91, 150))                                               # the radius' back
    if not glove:
        c = wr + 0.5 * (L['f3'] - wr)
        imu(m, cast(c, d))                                                 # the third metacarpal
        c = (L['f1'] + L['f12']) / 2; dd = unit(d - 0.6 * u)
        imu(m, cast(c, dd))                                                # the thumb's metacarpal


def thigh_module(sx):
    L = side(sx); m = 'thigh ' + L['s']; th = L['thigh']
    th.ring(m, 0.4, 8, 5)
    put(*th.at(0.97, 0), 'ref', m)                                         # lateral epicondyle
    put(*th.at(0.97, 180), 'bias', m)                                      # medial epicondyle
    imu(m, th.at(0.97, 0, -4.5))
    imu(m, th.at(0.97, 180, -4.5))
    imu(m, th.at(0.12, 0))                                                 # below the trochanter
    imu(m, th.at(0.9, 90))                                                 # above the patella


def calf_module(sx):
    L = side(sx); m = 'calf ' + L['s']; ca = L['calf']
    ca.ring(m, 0.33, 5, 4)
    lat = L['lat']
    def foot(out, ahead, d):                       # from inside the foot, `ahead` from the ankle
        return cast(np.array([L['an'][0] + out * L['sx'], -7.95, L['an'][2] + ahead]), unit(d))
    channel(m, foot(0.12, 0.65, up + 0.5 * lat), foot(0.12, 0.85, up + 0.5 * lat))   # ext. dig. brevis
    channel(m, foot(-0.2, 1.0, up), foot(-0.2, 1.2, up))                  # the first space
    channel(m, foot(0.2, 0.75, lat), foot(0.2, 0.95, lat))                # abductor digiti minimi
    put(*ca.at(0.33, 0), 'ref', m)
    put(*ca.at(0.5, 0), 'bias', m)
    imu(m, ca.at(0.1, 0))                                                  # below the knee
    imu(m, ca.at(0.82, 0))                                                 # above the ankle
    imu(m, foot(-0.1, 0.55, up - 0.6 * lat))                                # the midfoot, inside
    imu(m, foot(0.25, 1.1, up))                                            # the fourth metatarsal


def main(glove=False):
    head_module(); neck_module(); chest_module(); lower_back_module()
    for sx in (1, -1):
        shoulder_module(sx); hip_module(sx); upper_arm_module(sx)
        forearm_module(sx, glove); thigh_module(sx); calf_module(sx)
    mods = sorted(set(e['module'] for e in E))
    count = lambda m, layer: sum(e['module'] == m and e['layer'] == layer for e in E)
    print(f"{'module':22} P+N ref bias IMUs")
    for m in mods:
        print(f"{m:22} {count(m, 'emg'):3} {count(m, 'ref'):3} {count(m, 'bias'):4} {count(m, 'imu'):4}")
    total = {l: sum(e['layer'] == l for e in E) for l in ('emg', 'ref', 'bias', 'imu')}
    print(len(mods), 'modules', total, len(C), 'channels')
    assert len(mods) == 16 and total == {'emg': 256, 'ref': 16, 'bias': 16, 'imu': 48}, total
    assert all(count(m, 'emg') == 16 and count(m, 'ref') == 1 and count(m, 'bias') == 1 for m in mods)
    return E, C


def path(i, j, steps=16):
    """The channel over the skin from its P to its N."""
    p, q = np.array(E[i]['p']), np.array(E[j]['p'])
    a, b = np.array(E[i]['n']), np.array(E[j]['n'])
    pts = []
    for t in np.linspace(0, 1, steps):
        d = unit(a * (1 - t) + b * t); m = p * (1 - t) + q * t
        try:
            h, n = cast(m - d * 0.3, d)
            if np.linalg.norm(h - m) > 0.4:
                raise RuntimeError
        except RuntimeError:
            h, n = m, d
        pts.append((h + n * 0.03).tolist())
    return pts


if __name__ == '__main__':
    main()
    json.dump(dict(positions=V.astype(np.float32).round(4).ravel().tolist(),
                   index=tris.ravel().tolist(), electrodes=E,
                   chords=[path(a, b) for a, b in C],
                   chord_modules=[E[a]['module'] for a, _ in C]), open(sys.argv[2], 'w'))
