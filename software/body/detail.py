"""The whole suit in detail on MakeHuman's base mesh (CC0): every unit's sixteen electrodes laid out
by its muscles, the chords (channels) between them, and the bias electrodes.
Usage: detail.py base.obj suit.json out.json"""
import numpy as np, json, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from place import cast, J, unit, frame, around, contour, at

up, fwd = np.array([0, 1, 0.]), np.array([0, 0, 1.])
E, C, RING = [], [], {}   # electrodes; chords as index pairs; ring chords' axis

def el(o, d, pole, unit_name, layer='emg'):
    p, n = cast(np.asarray(o, float), unit(np.asarray(d, float)))
    E.append(dict(p=p.tolist(), n=n.tolist(), layer=layer, pole=pole, module=unit_name))
    return len(E) - 1

HUB = {}
def two_halves(name, A, B, hub, axis=(0, 1, 0), via=(0, 0, 1)):
    """A and B: eight (origin, direction) a half; chord k joins A[k] with B[k ^ 1]; P is A[k] for
    an even k and B[k ^ 1] for an odd one, so that the eight P lie four on each half."""
    ia, ib = [None] * 8, [None] * 8
    for k in range(8):
        j = k ^ 1
        pa, pb = ('P', 'N') if k % 2 == 0 else ('N', 'P')
        ia[k] = el(*A[k], pa, name); ib[j] = el(*B[j], pb, name)
        C.append((ia[k], ib[j])); HUB[(ia[k], ib[j])] = (np.asarray(hub, float), unit(np.asarray(axis, float)), unit(np.asarray(via, float)))

def ring(name, A, B, frac, n, gap_dir, gap=0.14):
    c = A + frac * (B - A); a, f, s = frame(B - A, gap_dir)
    P, N, L = contour(c, a, f, s)
    g = gap * L[-1]; start, end = g * 0.75, L[-1] - g * 0.75; pitch = (end - start) / n
    idx = []
    for k in range(n):
        p, nn = at(P, N, L, start + pitch * (k + 0.5))
        E.append(dict(p=list(map(float, p)), n=list(map(float, nn)), layer='emg', pole='PN'[k % 2], module=name))
        idx.append(len(E) - 1)
    off = n // 2 - 1 if (n // 2) % 2 == 0 else n // 2     # 16: seven places on, 10: five
    for k in range(0, n, 2):
        C.append((idx[k], idx[(k + off) % n])); RING[(idx[k], idx[(k + off) % n])] = (c, a)
    p, nn = at(P, N, L, start * 0.5)
    E.append(dict(p=list(map(float, p)), n=list(map(float, nn)), layer='bias', pole='', module=name))


HELIX = {}
def two_rings(name, A, B, f1, f2, n, gap_dir, gap=0.14, mod_dir=None):
    """Two rings of n, P on the first, N on the second; each P to the N half a turn round."""
    rings = []
    for f, pole in ((f1, 'P'), (f2, 'N')):
        c = A + f * (B - A); a, fr, sd = frame(B - A, gap_dir)
        P, N, L = contour(c, a, fr, sd)
        g = gap * L[-1]; start, end = g * 0.75, L[-1] - g * 0.75; pitch = (end - start) / n
        idx = []
        for k in range(n):
            p, nn = at(P, N, L, start + pitch * (k + 0.5))
            E.append(dict(p=list(map(float, p)), n=list(map(float, nn)), layer='emg', pole=pole, module=name))
            idx.append(len(E) - 1)
        rings.append((idx, c, a))
        if pole == 'P':
            p, nn = at(P, N, L, start * 0.5)
            E.append(dict(p=list(map(float, p)), n=list(map(float, nn)), layer='bias', pole='', module=name))
    (ip, c1, a), (iN, c2, _) = rings
    cm = (c1 + c2) / 2; _, fr, sd = frame(B - A, gap_dir if mod_dir is None else mod_dir)
    el(cm, fr, '', name, 'module')
    for k in range(n):
        j = iN[(k + n // 2) % n]; C.append((ip[k], j)); HELIX[(ip[k], j)] = (c1, c2, a)

def pairs(name, items, half=0.07):
    for c, axis, d in items:
        a = unit(axis); i = el(c - a * half, d, 'P', name); j = el(c + a * half, d, 'N', name); C.append((i, j))

hd, nk = J('head'), J('neck')
yC7 = nk[1] - 0.05; yC2 = hd[1] - 0.3; yC4 = (yC2 + yC7) / 2
back = -fwd

for side, sx in (('l', 1), ('r', -1)):
    lat = np.array([sx, 0, 0.])
    sh, el_, wr = J(f'{side}-shoulder'), J(f'{side}-elbow'), J(f'{side}-hand')
    hip, kn, an = J(f'{side}-upper-leg'), J(f'{side}-knee'), J(f'{side}-ankle')
    # limbs
    two_rings(f'upper arm {side}', sh, el_, 0.35, 0.65, 8, lat, 0.08)
    f1, f2, f5 = J(f'{side}-finger-1-2'), J(f'{side}-finger-2-1'), J(f'{side}-finger-5-1')
    two_rings(f'forearm {side}', el_, wr, 0.2, 0.48, 5, f5 - f2)
    Lh = (f2 + f5) / 2 - wr; Ah = f5 - f2
    Nh = unit(np.cross(Lh, Ah)) * sx
    if Nh @ lat < 0: Nh = -Nh
    pairs(f'forearm {side}', [(wr + 0.62 * ((f1 + f2) / 2 - wr), f2 - wr, Nh),
                              (wr + 0.45 * (f1 - wr), f1 - wr, -unit(Ah) * 0.8 - Nh * 0.6),
                              (wr + 0.5 * (f5 - wr), f5 - wr, unit(Ah) * 0.9 - Nh * 0.3)])
    two_rings(f'thigh {side}', hip, kn, 0.4, 0.58, 8, lat, 0.08)
    two_rings(f'calf {side}', kn, an, 0.22, 0.42, 5, unit(fwd - 0.6 * lat), mod_dir=lat)
    ft1 = J(f'{side}-foot-1'); fa = ft1 - an
    mid = an + 0.45 * fa + np.array([0, 0.12, 0])
    pairs(f'calf {side}', [(mid + 0.12 * lat, fa, up + 0.2 * lat),        # extensor digitorum brevis
                           (mid - 0.1 * lat + np.array([0, -0.15, 0]), fa, -lat),   # abductor hallucis
                           (mid + 0.1 * lat + np.array([0, -0.2, 0]), fa + np.array([0, 0, -0.6]), lat)])  # abductor digiti quinti
    # shoulder: the front and the top, the back
    S = sh + np.array([0.05 * sx, 0.1, 0]); ax = unit(el_ - sh)
    latp = unit(lat - (lat @ ax) * ax)
    front = [(S, unit(0.3 * lat + 0.1 * up + fwd)), (S + 0.3 * ax, unit(0.2 * latp + fwd)),
             ((0.8 * sx, 4.95, 0.3), fwd), ((1.3 * sx, 4.85, 0.3), fwd),
             (S, unit(latp + 0.2 * up)), (S + 0.35 * ax, latp),
             ((1.2 * sx, 5.35, -0.2), unit(up - 0.3 * fwd)), ((0.8 * sx, 5.4, -0.25), unit(up - 0.5 * fwd))]
    backl = [(S, unit(0.3 * lat + 0.1 * up - fwd)), (S + 0.3 * ax, unit(0.2 * latp - fwd)),
             ((1.05 * sx, 4.95, -0.2), back), ((0.85 * sx, 4.8, -0.2), back),
             ((1.2 * sx, 4.7, -0.2), unit(0.6 * lat - fwd)), ((1.0 * sx, 4.45, -0.2), unit(0.5 * lat - fwd)),
             ((0.8 * sx, yC7 - 0.45, 0), back), ((0.6 * sx, yC7 - 0.35, 0), unit(0.3 * up - fwd))]
    two_halves(f'shoulder {side}', front, backl, S, lat, up)
    el((1.4 * sx, 5.25, -0.1), unit(up - fwd), '', f'shoulder {side}', 'module')
    el(sh + np.array([0.1 * sx, 0.35, 0]), up, '', f'shoulder {side}', 'bias')
    # hip: the front and the side, the back
    c = np.array([hip[0] * 0.6, hip[1] + 0.35, hip[2]])
    def hd_(ang, dy):
        r = np.radians(ang); return (c + up * dy, unit(np.cos(r) * lat + np.sin(r) * -fwd))
    fr = [hd_(-60, -0.1), hd_(-50, -0.4), hd_(-30, 0.2), hd_(-20, -0.1),
          hd_(0, 0.1), hd_(10, -0.15), hd_(-5, 0.45), hd_(20, 0.4)]
    bk = [hd_(40, 0.2), hd_(48, -0.1), hd_(58, 0.15), hd_(66, -0.15),
          hd_(76, 0.15), hd_(84, -0.15), hd_(94, 0.15), hd_(102, -0.15)]
    two_halves(f'hip {side}', fr, bk, c, up, lat)
    el(c + up * 0.05, unit(lat - 0.4 * fwd), '', f'hip {side}', 'module')
    el(np.array([hip[0] * 0.8, hip[1] - 0.1, hip[2]]), lat, '', f'hip {side}', 'bias')

# neck and upper back
def neck_half(sx):
    lat = np.array([sx, 0, 0.]); sh = J('l-shoulder')
    acr = np.array([sh[0] * sx + 0.15 * sx, sh[1] + 0.25, sh[2]])
    c7 = cast(np.array([0, yC7, 0.1]), back)[0]; m = (acr + c7) / 2
    return [((0, yC2, 0.1), unit(back + 0.75 * lat)),
            ((0, yC4 + 0.05, 0.25), unit(lat + 0.35 * fwd)),
            ((0.35 * sx, yC4, 0.15), back),
            ((0, yC4 - 0.1, 0.05), unit(lat - 0.25 * fwd)),
            ((0, yC7, 0.1), unit(back + 0.55 * lat)),
            ((m[0], m[1] - 0.6, m[2] - 0.1), unit(up - 0.35 * fwd)),
            ((0.35 * sx, yC7 - 0.6, 0.2), back),
            ((0.65 * sx, yC7 - 1.0, 0.2), back)]
two_halves('neck', neck_half(1), neck_half(-1), (0, yC4, 0.05), up, back)
el((0, yC7 - 0.3, 0.1), back, '', 'neck', 'module')
el((0, 4.3, 0.1), back, '', 'neck', 'bias')
# chest and abdomen
def front_half(sx):
    lat = np.array([sx, 0, 0.])
    return [((0.35 * sx, 4.7, 0.2), fwd), ((0.85 * sx, 4.65, 0.2), fwd),
            ((0.6 * sx, 3.6, 0.3), unit(lat + 0.3 * fwd)), ((0.3 * sx, 2.75, 0.2), fwd),
            ((0.5 * sx, 2.55, 0.2), unit(lat + 0.6 * fwd)), ((0.3 * sx, 2.05, 0.2), fwd),
            ((0.3 * sx, 1.45, 0.2), fwd), ((0.6 * sx, 1.2, 0.2), unit(0.5 * lat + fwd))]
def reorder(L, idx): return [L[i] for i in idx]
two_halves('chest and abdomen', reorder(front_half(1), [0, 3, 1, 4, 2, 5, 6, 7]),
           reorder(front_half(-1), [0, 3, 1, 4, 2, 5, 6, 7]), (0, 3.0, 0.3), up, fwd)
el((0, 3.3, 0.3), fwd, '', 'chest and abdomen', 'module')
el((0, 4.0, 0.3), fwd, '', 'chest and abdomen', 'bias')
# lower back
def back_half(sx):
    lat = np.array([sx, 0, 0.])
    return [((0.5 * sx, 4.55, 0), back), ((0.8 * sx, 4.2, 0), unit(0.5 * lat - fwd)),
            ((0.3 * sx, 3.8, 0), back), ((0.25 * sx, 2.85, 0), back),
            ((0.6 * sx, 2.6, 0), back), ((0.8 * sx, 2.35, 0), unit(0.6 * lat - fwd)),
            ((0.7 * sx, 2.1, 0), back), ((0.2 * sx, 1.3, 0), back)]
two_halves('lower back', reorder(back_half(1), [0, 5, 1, 4, 2, 7, 3, 6]),
           reorder(back_half(-1), [0, 5, 1, 4, 2, 7, 3, 6]), (0, 3.0, 0.1), up, back)
el((0, 3.3, 0.0), back, '', 'lower back', 'module')
el((0, 1.0, 0), back, '', 'lower back', 'bias')
# head: the front half of the headband
c = np.array([0, hd[1] + 0.75, hd[2] + 0.1])
def head_half(sx):
    out = []
    for ang, dy in ((10, 0.1), (30, -0.05), (50, 0.05), (58, -0.25), (66, -0.5), (78, 0.0), (88, -0.25), (98, -0.45)):
        r = np.radians(ang); out.append((c + up * dy, unit(np.cos(r) * fwd + np.sin(r) * sx * np.array([1, 0, 0.]))))
    return out
two_halves('head', head_half(1), head_half(-1), c, up, fwd)
el(c, back, '', 'head', 'module')
r = np.radians(115); el(c - up * 0.9, unit(np.cos(r) * fwd + np.sin(r) * np.array([1, 0, 0.])), '', 'head', 'bias')

emg = sum(e['layer'] == 'emg' for e in E); bias = sum(e['layer'] == 'bias' for e in E); print(sum(e['layer'] == 'module' for e in E), 'modules')
mods = sorted(set(e['module'] for e in E))
print(emg, 'EMG,', bias, 'bias,', len(C), 'chords,', len(mods), 'units')
for m in mods: print(' ', m, sum(e['module'] == m and e['layer'] == 'emg' for e in E), sum(e['module'] == m and e['pole'] == 'P' for e in E), sum(1 for a, b in C if E[a]['module'] == m))
d = json.load(open(sys.argv[2]))

def rot(v, a, ang):
    return v * np.cos(ang) + np.cross(a, v) * np.sin(ang) + a * (a @ v) * (1 - np.cos(ang))

def path(i, j, steps=24):
    p, q = np.array(E[i]['p']), np.array(E[j]['p']); npn, nq = np.array(E[i]['n']), np.array(E[j]['n'])
    pts = []
    if (i, j) in HELIX:         # half a turn round the limb, from one ring to the other
        c1, c2, a = HELIX[(i, j)]
        u = p - c1; u -= (u @ a) * a; w = q - c2; w -= (w @ a) * a
        ang = np.arctan2(np.cross(unit(u), unit(w)) @ a, unit(u) @ unit(w))
        for t in np.linspace(0, 1, steps * 2):
            d = unit(rot(unit(u), a, ang * t)); o = c1 * (1 - t) + c2 * t
            h, n = cast(o, d); pts.append((h + n * 0.03).tolist())
    elif (i, j) in HUB:          # round the unit's hub, the shorter way
        c0, a, via = HUB[(i, j)]
        u = p - c0; hu = u @ a; u -= hu * a; w = q - c0; hw = w @ a; w -= hw * a
        ang = np.arctan2(np.cross(unit(u), unit(w)) @ a, unit(u) @ unit(w))
        if rot(unit(u), a, ang / 2) @ via < 0: ang -= np.sign(ang) * 2 * np.pi
        for t in np.linspace(0, 1, steps):
            d = unit(rot(unit(u), a, ang * t)); o = c0 + a * (hu * (1 - t) + hw * t)
            try:
                h, n = cast(o, d)
            except RuntimeError:
                continue
            pts.append((h + n * 0.03).tolist())
    elif (i, j) in RING:          # round the limb, the shorter way
        c, a = RING[(i, j)]
        u = p - c; u -= (u @ a) * a; w = q - c; w -= (w @ a) * a
        ang = np.arctan2(np.cross(unit(u), unit(w)) @ a, unit(u) @ unit(w))
        for t in np.linspace(0, 1, steps):
            d = unit(rot(unit(u), a, ang * t)); o = c + a * (((p - c) @ a) * (1 - t) + ((q - c) @ a) * t)
            h, n = cast(o, d); pts.append((h + n * 0.03).tolist())
    else:                        # over the skin between the two
        for t in np.linspace(0, 1, steps):
            d = unit(npn * (1 - t) + nq * t); m = p * (1 - t) + q * t
            try:
                h, n = cast(m - d * 0.3, d)
                if np.linalg.norm(h - m) > 0.6: raise RuntimeError
            except RuntimeError:
                h, n = m, d
            pts.append((h + n * 0.03).tolist())
    return pts

json.dump(dict(positions=d['positions'], index=d['index'], electrodes=E,
               chords=[path(a, b) for a, b in C]), open(sys.argv[3], 'w'))
