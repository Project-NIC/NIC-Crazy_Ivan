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

    def ring(self, module, t, n, below_cm, above_cm=4, turn=0.0, span=360.0):
        """n P evenly round at t over span degrees from the gap, turned by `turn` of a place; N
        1, 3, 5... along, below (above when below_cm is negative); N 2, 4... half a place round
        and above (below when above_cm is negative)."""
        step = span / n
        for k in range(n):
            ang = step * (k + 0.5 + turn) + (360 - span) / 2
            P = self.at(t, ang)
            N = self.at(t, ang, below_cm) if k % 2 == 0 else self.at(t, ang + step / 2, -above_cm)
            channel(module, P, N)


def ring_best(limb, module, t, n, gap=20.0, tries=None, along=(4, -4, 3, -3), across=(4, -4, 3, -3)):
    """A further ring of n P at t, clear of the gap (gap degrees each side of it): of the t, the
    turns and the N's offsets tried, along the bone (cm, + towards B) for N 1, 3, 5... and half a
    place round for N 2, 4..., the one whose electrodes keep farthest from every electrode placed.
    The offsets allowed keep a ring's N off the joint beside it; the choice is printed, for the
    page."""
    span = 360 - 2 * gap
    have = np.array([e['p'] for e in E])
    best = None
    for t_ in (tries or (t,)):
        for turn in (0.0, 0.25, 0.5, 0.75):
            for al in along:
                for ac in across:
                    step = span / n; pts = []
                    for k in range(n):
                        ang = gap + step * (k + 0.5 * (1 + turn) - 0.25)
                        pts.append(limb.at(t_, ang)[0])
                        pts.append((limb.at(t_, ang, al) if k % 2 == 0
                                    else limb.at(t_, ang + step / 2, ac))[0])
                    pts = np.array(pts)
                    d = np.linalg.norm(have[None, :, :] - pts[:, None, :], axis=2).min()
                    own = np.linalg.norm(pts[None] - pts[:, None], axis=2) + np.eye(len(pts)) * 9
                    score = min(d, own.min())
                    if best is None or score > best[0]:
                        best = (score, turn, al, ac, t_)
    _, turn, al, ac, t = best
    step = span / n
    for k in range(n):
        ang = gap + step * (k + 0.5 * (1 + turn) - 0.25)
        channel(module, limb.at(t, ang), limb.at(t, ang, al) if k % 2 == 0
                else limb.at(t, ang + step / 2, ac))
    print(f"  {module}: a ring of {n} at {t:.2f}, turned {turn}, along N {al:+} cm, "
          f"across N {ac:+} cm (+ towards the hand or the foot), {best[0] / CM:.1f} cm clear")


def pick(module, options, label=''):
    """Of the (P, N) options, the pair farthest from every electrode placed; printed."""
    have = np.array([e['p'] for e in E])
    def clear(o):
        pts = np.array([o[0][0], o[1][0]])
        return np.linalg.norm(have[None] - pts[:, None], axis=2).min()
    k = max(range(len(options)), key=lambda i: clear(options[i]))
    channel(module, *options[k])
    print(f"  {module}: {label} option {k}, {clear(options[k]) / CM:.1f} cm clear")


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
# Every unit's channels, by the main muscles (bogatyr/CONSTRUCTION.md): the first eight of a
# module on its muscles one site each, the second eight on the same muscles' other parts, a second
# ring on a limb, or crossed to a neighbour; references on the head and the neck alone, the body
# measuring differentially; the hand's and the foot's eight on the glove's and the sock's chip.

def head_module():
    m = 'head'
    brow = J('l-eye')[1] + 0.3
    for sx in (1, -1):
        channel(m, head(brow, sx, 14), head(brow + 0.3, sx, 14))          # frontalis, mid brow
        channel(m, head(brow, sx, 30), head(brow + 0.3, sx, 30))          # its outer third
        channel(m, head(brow - 0.15, sx, 62), head(brow + 0.15, sx, 62))  # temporalis, front
        channel(m, head(brow + 0.15, sx, 92), head(brow + 0.15, sx, 115))  # above the ear
    for sx in (1, -1):
        channel(m, head(brow + 0.45, sx, 80), head(brow + 0.75, sx, 80))  # temporalis, middle
        channel(m, head(brow + 0.45, sx, 105), head(brow + 0.55, sx, 125))  # temporalis, back
        channel(m, head(brow - 0.1, sx, 158), head(brow + 0.2, sx, 158))  # occipitalis, the side
        channel(m, head(brow + 0.1, sx, 46), head(brow + 0.45, sx, 44))   # frontalis, outer edge
    put(*head(J('l-eye')[1] - 0.45, 1, 118), 'ref', m)                      # the mastoids
    put(*head(J('l-eye')[1] - 0.45, -1, 118), 'bias', m)
    for sx in (1, -1):
        imu(m, head(J('l-eye')[1] + 0.75, sx, 22))             # the forehead, beside Míša
        imu(m, head(J('l-eye')[1] + 0.55, sx, 140))            # the back half, above the ear


def neck_module():
    m = 'neck and upper back'
    for sx in (1, -1):
        L = side(sx)
        channel(m, neck(LEVEL['C6'], sx, 40), neck(LEVEL['C7'] - 0.05, sx, 25))   # SCM, low
        pick(m, [(neck(LEVEL['C2'] - 0.05, sx, 128), neck(LEVEL['C2'] + h, sx, a))
                 for h in (0.18, 0.22, 0.26) for a in (100, 106, 112)], 'splenius')
        c7 = spine('C7')[0]
        p = (L['acromion'][0] + c7) / 2
        P = cast(np.array([p[0] * 0.6, p[1] - 0.5, p[2]]), unit(p - np.array([p[0] * 0.6, p[1] - 0.5, p[2]])))
        q = P[0] + 0.4 * unit(c7 - P[0])
        N = cast(np.array([q[0] * 0.6, q[1] - 0.5, q[2]]), unit(q - np.array([q[0] * 0.6, q[1] - 0.5, q[2]])))
        channel(m, P, N)                                                    # upper trapezius
        channel(m, spine('C4', 0.15 * sx), spine('C6', -0.15 * sx))        # extensors, across
    put(*spine('C7'), 'ref', m)
    put(*spine('T4'), 'bias', m)
    for lv in ('C2', 'C5', 'T2', 'T6'):
        imu(m, spine(lv))


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
    # the second eight: the deltoid's lower parts crossed to its middle, the trapezius' upper
    # fibres, the serratus' lower slip to the latissimus, the latissimus' lower fibres
    for sg in (1, -1):                                  # the deltoid's front and back, lower, to its middle
        pick(m, [(ua.at(t, sg * a), ua.at(t2, sg * b)) for t in (0.25, 0.3) for a in (65, 75, 85)
                 for t2 in (0.22, 0.27) for b in (25, 32)], 'deltoid crossed')
    channel(m, back(0.25 * sx, LEVEL['T1']), back(0.62 * sx, LEVEL['T1']))
    channel(m, round_(3.45, sx, 90), round_(3.45, sx, 106 if sx > 0 else 104))
    pick(m, [(round_(LEVEL[lv], sx, a), round_(LEVEL[lv] + 0.4, sx, a - 10)) for lv in ('T10', 'T11')
             for a in (138, 146, 154)], 'latissimus, lower')
    channel(m, round_(LEVEL['T9'], sx, 126), round_(LEVEL['T9'] - 0.05, sx, 110))   # lat -> serratus
    channel(m, ua.at(0.15, 82), front(1.45 * sx, 5.12))             # anterior deltoid -> pec, over the groove
    channel(m, ua.at(0.15, -82), ua.at(0.03, -108))                  # posterior deltoid, low -> by the spine
    put(*scapula_spine(L, 1), 'bias', m)
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
    for sx in (1, -1):
        channel(m, front(0.35 * sx, 3.0), front(0.35 * sx, 3.4))           # rectus, upper part
        channel(m, front(0.25 * sx, 1.5), front(0.2 * sx, 1.12))           # rectus, below the navel
        channel(m, round_(2.2, sx, 52), round_(1.95, sx, 40))              # external oblique, front
        channel(m, round_(3.45, sx, 72), round_(3.25, sx, 56))             # external oblique, ribs
    put(*front(0.003, 5.1), 'bias', m)                                     # the manubrium
    imu(m, front(0.003, 4.5))


def lower_back_module():
    m = 'lower back'
    for sx in (1, -1):
        channel(m, spine('T9', 0.35 * sx), spine('T11', -0.35 * sx))      # thoracic erectors
        channel(m, spine('L1', 0.35 * sx), spine('L2', -0.35 * sx))       # longissimus
        channel(m, spine('L2', 0.65 * sx), back(0.7 * sx, LEVEL['L2'] + 0.4))   # iliocostalis
        channel(m, spine('L5', 0.25 * sx), spine('L4', -0.25 * sx))       # multifidus
    for sx in (1, -1):
        channel(m, spine('T8', 0.4 * sx), spine('T7', -0.4 * sx))         # thoracic erectors, higher
        channel(m, spine('L3', 0.4 * sx), back(0.55 * sx, LEVEL['L4']))   # longissimus, L3
        pick(m, [(back(x * sx, LEVEL[lv]), back(x * sx, LEVEL[lv] + 0.4)) for lv in ('T10', 'T11', 'T12')
                 for x in (0.55, 0.65, 0.75)], 'iliocostalis, thoracic')
        channel(m, round_(CREST_Y + 0.35, sx, 118), round_(CREST_Y + 0.7, sx, 106))  # ext. oblique, back
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
    channel(m, round_(0.47, sx, 148), round_(1.0, sx, 135))               # maximus, low -> medius
    # the second eight: the sartorius, the medius' front above the TFL, the maximus' upper part
    # beside the sacrum and between its two sites, crossings between them
    channel(m, front(0.88 * sx, 0.72), front(0.78 * sx, 0.34))            # sartorius
    channel(m, round_(1.5, sx, 82), round_(1.5, sx, 64))                  # medius front, high -> TFL
    channel(m, back(0.25 * sx, 1.25), back(0.25 * sx, 0.88))              # maximus, beside the sacrum
    pick(m, [(back(x * sx, y), back((x + 0.3) * sx, y - 0.15)) for x in (0.5, 0.6) for y in (1.1, 1.25, 1.4)],
         'maximus, upper middle')
    channel(m, round_(1.42, sx, 128), round_(1.38, sx, 98))               # medius back -> middle, high
    channel(m, round_(0.3, sx, 118), round_(0.72, sx, 126))               # maximus' outer edge -> up
    channel(m, round_(0.62, sx, 70), round_(0.25, sx, 84))                # TFL low -> its back edge
    channel(m, round_(1.25, sx, 145), round_(1.55, sx, 135))              # maximus, top -> medius back
    imu(m, round_(CREST_Y - 0.1, sx, 72))                                 # the iliac tubercle
    put(*round_(TROCH_Y, sx, 92), 'bias', m)


def upper_arm_module(sx):
    L = side(sx); m = 'upper arm ' + L['s']; ua = L['upperarm']
    ua.ring(m, 0.5, 8, 4)
    ring_best(ua, m, 0.74, 8, gap=25, tries=(0.71, 0.74, 0.77), along=(-4, -3), across=(4, 3, -4, -3))   # the second ring, its along N up
    imu(m, ua.at(0.9, 0))                                                  # above the epicondyle
    put(*ua.at(0.9, 0, -6), 'bias', m)
    imu(m, ua.at(0.4, 0))                                                  # the deltoid's insertion
    imu(m, ua.at(0.88, 200))                                               # above the medial ep.
    imu(m, ua.at(0.86, 270))                                               # above the olecranon


def forearm_module(sx):
    L = side(sx); m = 'forearm ' + L['s']; fa = L['forearm']
    fa.ring(m, 0.4, 5, 4)
    ring_best(fa, m, 0.17, 6, tries=(0.15, 0.17, 0.19), along=(4, 3), across=(4, 3))   # by the elbow, its N down
    ring_best(fa, m, 0.63, 5, tries=(0.6, 0.63, 0.66), along=(-4, -3), across=(-4, -3))   # mid-forearm, its N up
    put(*fa.at(0.97, 0), 'bias', m)
    imu(m, fa.at(0.16, 10))                                                # the ulna, by the elbow
    imu(m, fa.at(0.91, 150))                                               # the radius' back


def hand_unit(sx):
    L = side(sx); s = L['s']; m = 'hand ' + s
    wr, d, u = L['wr'], L['dorsal'], L['ulnar']
    ax = unit((L['f2'] + L['f5']) / 2 - wr)
    c = wr + 0.62 * ((L['f1'] + L['f2']) / 2 - wr)                         # first dorsal interosseous
    channel(m, cast(c - ax * 0.1, d), cast(c + ax * 0.1, d))
    c = wr + 0.45 * (L['f12'] - wr); dd = unit(-u * 0.8 - d * 0.6)        # abductor pollicis brevis
    channel(m, cast(c - ax * 0.1, dd), cast(c + ax * 0.1, dd))
    c = wr + 0.5 * (L['f5'] - wr); dd = unit(u * 0.9 - d * 0.3)           # abductor digiti minimi
    channel(m, cast(c - ax * 0.1, dd), cast(c + ax * 0.1, dd))
    # the second five: the dorsal interossei of the second to fourth spaces, a trial; the first
    # web across; the hypothenar's edge across to the fifth metacarpal's back
    for f, g in ((2, 3), (3, 4), (4, 5)):
        ja, jb = J(f'{s}-finger-{f}-1'), J(f'{s}-finger-{g}-1')
        pick(m, [(cast(wr + t0 * ((ja + jb) / 2 - wr), d), cast(wr + (t0 + 0.2) * ((ja + jb) / 2 - wr), d))
                 for t0 in (0.45, 0.5, 0.55)], f'dorsal interosseous {f}-{g}')
    c = (L['f1'] + L['f2']) / 2 + 0.15 * (L['f2'] - L['f1'])
    channel(m, cast(c, unit(d - 0.7 * u)), cast(c, unit(-d - 0.7 * u)))                # the first web
    pick(m, [(cast(wr + t0 * (L['f5'] - wr), unit(u - k * d)), cast(wr + (t0 + 0.1) * (L['f5'] - wr), d))
             for t0 in (0.2, 0.25, 0.3) for k in (0.0, 0.3)], 'hypothenar across')
    put(*cast(wr + 0.12 * (L['f3'] - wr), d), 'bias', m)                  # the carpus, the board's
    # the glove's 20 IMU places: the board, the thumb's metacarpal and two phalanges, each
    # finger's three, the four spares (the fourth and fifth metacarpals' heads, the thumb's
    # metacarpal again, by its base, and the second metacarpal's head)
    imu(m, cast(wr + 0.3 * (L['f3'] - wr), d))
    th = [J(f'{s}-finger-1-{k}') for k in (1, 2, 3, 4)]
    for a_, b_ in zip(th[:-1], th[1:]):
        imu(m, cast((a_ + b_) / 2, unit(d - 0.5 * u)))
    for f in (2, 3, 4, 5):
        js = [J(f'{s}-finger-{f}-{k}') for k in (1, 2, 3, 4)]
        for a_, b_ in zip(js[:-1], js[1:]):
            imu(m, cast((a_ + b_) / 2, d))
    for f in (4, 5):
        imu(m, cast(wr + 0.85 * (J(f'{s}-finger-{f}-1') - wr), d))
    imu(m, cast(th[0] + 0.12 * (th[1] - th[0]), unit(d - 0.5 * u)))
    imu(m, cast(wr + 0.85 * (L['f2'] - wr), d))


def thigh_module(sx):
    L = side(sx); m = 'thigh ' + L['s']; th = L['thigh']
    th.ring(m, 0.4, 8, 5)
    ring_best(th, m, 0.7, 8, along=(4, 3, -4), across=(-4, -3, 4))            # the second ring
    put(*th.at(0.97, 180), 'bias', m)                                      # medial epicondyle
    imu(m, th.at(0.97, 0, -4.5))
    imu(m, th.at(0.97, 180, -4.5))
    imu(m, th.at(0.12, 0))                                                 # below the trochanter
    imu(m, th.at(0.9, 90))                                                 # above the patella


def calf_module(sx):
    L = side(sx); m = 'calf ' + L['s']; ca = L['calf']
    ca.ring(m, 0.33, 5, 4)
    ring_best(ca, m, 0.2, 6, gap=30, along=(4, 3), across=(4, 3))          # below the knee, its N down
    ring_best(ca, m, 0.53, 5, along=(-4, -3, 4), across=(-4, -3))            # mid-calf
    put(*ca.at(0.5, 0), 'bias', m)
    imu(m, ca.at(0.1, 0))                                                  # below the knee
    imu(m, ca.at(0.82, 0))                                                 # above the ankle


def foot_unit(sx):
    L = side(sx); m = 'foot ' + L['s']; lat = L['lat']
    def foot(out, ahead, d):                       # from inside the foot, `ahead` from the ankle
        return cast(np.array([L['an'][0] + out * L['sx'], -7.95, L['an'][2] + ahead]), unit(d))
    channel(m, foot(0.12, 0.65, up + 0.5 * lat), foot(0.12, 0.85, up + 0.5 * lat))   # ext. dig. brevis
    channel(m, foot(-0.2, 1.0, up), foot(-0.2, 1.2, up))                  # the first space
    channel(m, foot(0.2, 0.75, lat), foot(0.2, 0.95, lat))                # abductor digiti minimi
    # the second five: the second to fourth spaces, the extensor hallucis brevis, the abductor
    # digiti minimi across to the fifth metatarsal's base
    channel(m, foot(-0.08, 1.15, up), foot(-0.08, 1.35, up))              # the second space
    channel(m, foot(0.05, 1.2, up), foot(0.05, 1.4, up))                  # the third space
    channel(m, foot(0.28, 1.2, up + 0.2 * lat), foot(0.28, 1.4, up + 0.2 * lat))     # the fourth
    channel(m, foot(-0.03, 0.62, up), foot(-0.12, 0.82, up))              # extensor hallucis brevis
    channel(m, foot(0.22, 0.45, lat), foot(0.12, 0.42, up + lat))         # abd. digiti minimi -> EDB
    put(*cast(np.array([L['an'][0], -7.95, L['an'][2] - 0.25]), unit(-0.3 * fwd - lat)), 'bias', m)   # the heel's inner side
    # the sock's four IMUs to start: the heel, the midfoot inside, the fourth metatarsal, the hallux
    imu(m, cast(np.array([L['an'][0], -7.85, L['an'][2] - 0.2]), unit(-fwd)))
    imu(m, foot(-0.1, 0.55, up - 0.6 * lat))
    imu(m, foot(0.25, 1.1, up))
    imu(m, foot(-0.25, 1.55, up))


def main():
    head_module(); neck_module(); chest_module(); lower_back_module()
    for sx in (1, -1):
        shoulder_module(sx); hip_module(sx); upper_arm_module(sx); forearm_module(sx)
        hand_unit(sx); thigh_module(sx); calf_module(sx); foot_unit(sx)
    mods = sorted(set(e['module'] for e in E))
    count = lambda m, layer: sum(e['module'] == m and e['layer'] == layer for e in E)
    print(f"{'unit':22} P+N ref bias IMUs")
    for m in mods:
        print(f"{m:22} {count(m, 'emg'):3} {count(m, 'ref'):3} {count(m, 'bias'):4} {count(m, 'imu'):4}")
    total = {l: sum(e['layer'] == l for e in E) for l in ('emg', 'ref', 'bias', 'imu')}
    print(len(mods), 'units', total, len(C), 'channels')
    want = {'head': 32, 'neck and upper back': 16, 'hand l': 16, 'hand r': 16, 'foot l': 16, 'foot r': 16}
    assert len(mods) == 20 and total == {'emg': 560, 'ref': 2, 'bias': 20, 'imu': 44 + 40 + 8}, total
    assert all(count(m, 'emg') == want.get(m, 32) and count(m, 'bias') == 1 for m in mods)
    check()
    return E, C


def check():
    """No two electrodes closer than 1.5 cm, 1 cm on the hand and the foot, where the discs are
    small; an IMU 1 cm from anything; every pair 1.5-10 cm apart in a straight line."""
    P = np.array([e['p'] for e in E]); bad = 0
    seen, name = {}, {}
    for i, e in enumerate(E):                   # a name for each: the unit, its channel's number
        if e['layer'] == 'emg':
            seen[e['module']] = seen.get(e['module'], 0) + 1
            name[i] = f"{e['module']} {(seen[e['module']] + 1) // 2}{e['pole']}"
        else:
            name[i] = f"{e['module']} {e['layer']}"
    for i in range(len(E)):
        d = np.linalg.norm(P - P[i], axis=1) / CM; d[i] = 99
        for j in np.nonzero(d < 1.5)[0]:
            if j < i:
                continue
            small = E[i]['module'][:4] in ('hand', 'foot') or 'imu' in (E[i]['layer'], E[j]['layer'])
            if d[j] < (1.0 if small else 1.5):
                bad += 1
                print(f"  close: {name[i]} and {name[j]}, {d[j]:.1f} cm")
    for a, b in C:
        d = np.linalg.norm(P[a] - P[b]) / CM
        if not 1.5 <= d <= 10:
            bad += 1; print(f"  pair: {name[a]} {d:.1f} cm")
    print(bad, 'to look at')


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
