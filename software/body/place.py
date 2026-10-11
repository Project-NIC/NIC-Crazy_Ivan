"""Place the suit's electrodes on MakeHuman's base mesh (CC0). Units: decimetres, +x = the model's left,
+y up, +z front."""
import numpy as np, json, sys
sys.path.insert(0, __file__.rsplit('/',1)[0])
from load import load

V, G = load(sys.argv[1])  # the mesh, also when imported
quads = np.array(G['body'])
tris = np.concatenate([quads[:, [0, 1, 2]], quads[:, [0, 2, 3]]])
T0, T1, T2 = V[tris[:, 0]], V[tris[:, 1]], V[tris[:, 2]]
E1, E2 = T1 - T0, T2 - T0

def J(name):
    vs = sorted(set(i for f in G['joint-' + name] for i in f))
    return V[vs].mean(0)

def unit(v): return v / np.linalg.norm(v)

def cast(o, d):
    """Nearest hit of the ray o + t d on the skin, with the face normal."""
    p = np.cross(d, E2); det = (E1 * p).sum(1)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1), 0)
    s = o - T0; u = (s * p).sum(1) * inv
    q = np.cross(s, E1); v = (q * d).sum(1) * inv; t = (q * E2).sum(1) * inv
    hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6)
    if not hit.any(): raise RuntimeError(f'no hit from {o} along {d}')
    t = np.where(hit, t, np.inf); k = t.argmin()
    n = unit(np.cross(E1[k], E2[k]))
    if n @ d < 0: n = -n
    return o + t[k] * d, n

def frame(axis, front):
    a = unit(axis); f = unit(front - (front @ a) * a); s = np.cross(a, f)
    return a, f, s

def around(c, a, f, s, ang):
    """Direction at angle ang (degrees) from f towards s, in the plane across a."""
    r = np.radians(ang); return unit(np.cos(r) * f + np.sin(r) * s)

def contour(c, a, f, s, a0=0, a1=360, step=1.0):
    """Hits of rays from c across the axis a, from angle a0 to a1; their arc length."""
    angs = np.arange(a0, a1 + 1e-9, step)
    hits = [cast(c, around(c, a, f, s, t)) for t in angs]
    P = np.array([h[0] for h in hits]); N = np.array([h[1] for h in hits])
    L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    return P, N, L

def at(P, N, L, x):
    k = int(np.clip(np.searchsorted(L, x), 0, len(L) - 1)); return P[k], N[k]

E = []  # electrodes: pos, normal, layer, module
def put(o, d, layer, module, pole=''):
    p, n = cast(o, d); E.append(dict(p=p.tolist(), n=n.tolist(), layer=layer, module=module, pole=pole))

def add(p, n, layer, module, pole=''):
    E.append(dict(p=list(map(float, p)), n=list(map(float, n)), layer=layer, module=module, pole=pole))

def strip(module, P, N, L, start, end, n, ends=True):
    """n pads at a fixed pitch between arc lengths start and end; the reference and the bias
    half a pitch beyond the two ends."""
    pitch = (end - start) / n
    for k in range(n):
        add(*at(P, N, L, start + pitch * (k + 0.5)), 'emg', module, 'PN'[k % 2])
    if ends:
        add(*at(P, N, L, max(start - 0.5 * pitch, 0)), 'ref', module)
        add(*at(P, N, L, min(end + 0.5 * pitch, L[-1])), 'bias', module)

def ring(module, A, B, frac, n, gap_dir, gap=0.14):
    """n pads round the limb at frac from A to B, at a fixed pitch along the strip, which leaves
    a gap of the girth's fraction gap centred on gap_dir; the reference and the bias at its ends."""
    c = A + frac * (B - A); a, f, s = frame(B - A, gap_dir)
    P, N, L = contour(c, a, f, s)
    g = gap * L[-1]
    strip(module, P, N, L, g / 2 + g * 0.25, L[-1] - g / 2 - g * 0.25, n)

def pair(module, c, axis, d, half=0.1):
    a = unit(axis)
    put(c - a * half, d, 'emg', module, 'P'); put(c + a * half, d, 'emg', module, 'N')

def main():
    global E
    for side, sx in (('l', 1), ('r', -1)):
        lat = np.array([sx, 0, 0.]); fwd = np.array([0, 0, 1.]); up = np.array([0, 1, 0.])
        sh, el, wr = J(f'{side}-shoulder'), J(f'{side}-elbow'), J(f'{side}-hand')
        hip, kn, an = J(f'{side}-upper-leg'), J(f'{side}-knee'), J(f'{side}-ankle')
        # upper arm and shoulder: a ring of ten halfway, the gap on the inner side; the deltoid's three pairs
        m = f'upper arm {side}'
        ring(m, sh, el, 0.5, 10, -lat)
        a, f, s = frame(el - sh, fwd)
        c = sh + 0.22 * (el - sh)
        lat_p = unit(lat - (lat @ a) * a)
        for ang in (-55, 0, 55):   # anterior, middle, posterior
            d = unit(np.cos(np.radians(ang)) * lat_p + np.sin(np.radians(ang)) * -f)
            pair(m, c, a, d)
        # forearm and hand: a ring of ten in the upper third, the gap over the ulna; three pairs on the hand
        m = f'forearm {side}'
        f1, f2, f5 = J(f'{side}-finger-1-2'), J(f'{side}-finger-2-1'), J(f'{side}-finger-5-1')
        ulnar = f5 - f2
        ring(m, el, wr, 0.33, 10, ulnar)
        L = (f2 + f5) / 2 - wr; A = ulnar
        N = unit(np.cross(L, A)) * sx    # the back of the hand, away from the body
        if N @ lat < 0: N = -N
        c = wr + 0.62 * (((f1 + f2) / 2) - wr)
        pair(m, c, f2 - wr, N, 0.07)                                  # first dorsal interosseous
        c = wr + 0.45 * (f1 - wr)
        pair(m, c, f1 - wr, unit(-unit(A) * 0.8 - N * 0.6), 0.07)      # the thenar's edge
        c = wr + 0.5 * (f5 - wr)
        pair(m, c, f5 - wr, unit(unit(A) * 0.9 - N * 0.3), 0.07)       # the hypothenar's edge
        # thigh halfway, the gap on the inner side; calf in the upper third, the gap over the tibia
        ring(f'thigh {side}', hip, kn, 0.5, 16, -lat)
        ring(f'calf {side}', kn, an, 0.33, 16, unit(fwd - 0.6 * lat))
        # hip: an arc of sixteen on the side, between the iliac crest and the trochanter
        m = f'hip {side}'
        c = np.array([hip[0] * 0.55, hip[1] + 0.55, hip[2]])
        a_, f_, s_ = frame(np.array([0, 1, 0.]), lat)
        if s_ @ fwd < 0: s_ = -s_          # from the front round the side to the back
        P, N, L = contour(c, a_, f_, s_, -65, 65)
        strip(m, P, N, L, 0.06 * L[-1], 0.94 * L[-1], 16)

    up = np.array([0, 1, 0.]); fwd = np.array([0, 0, 1.]); lat = np.array([1, 0, 0.])
    def torso_ring(name, y, z0):
        c = np.array([0, y, z0]); a_, f_, s_ = frame(up, fwd)   # angle 0 front, 90 towards s_
        for half, (lo, hi) in (('front', (-90, 90)), ('back', (90, 270))):
            P, N, L = contour(c, a_, f_, s_, lo, hi)
            strip(f'{name} {half}', P, N, L, 0.05 * L[-1], 0.95 * L[-1], 16, ends=False)
            dz = 0.22 if half == 'front' else -0.22
            for k, layer in ((0, 'ref'), (-1, 'bias')):
                o = c + up * dz; d = unit(P[k] - c); d[1] = 0; put(o, unit(d), layer, f'{name} {half}')

    torso_ring('chest', J('spine-1')[1] - 0.6, 0.35)
    torso_ring('waist', J('spine-3')[1] + 0.15, 0.1)
    # neck: a ring of sixteen at its root, the gap behind over C7
    nk = J('neck'); c = nk + np.array([0, -0.25, 0.05])
    ring('neck', c - up, c + up, 0.5, 16, -fwd, gap=0.12)
    # head: the front half from ear to ear, the reference and the bias behind the ears
    hd = J('head'); c = np.array([0, hd[1] + 0.75, hd[2] + 0.1])
    a_, f_, s_ = frame(up, fwd)
    P, N, L = contour(c, a_, f_, s_, -90, 90)
    strip('head', P, N, L, 0.03 * L[-1], 0.97 * L[-1], 16, ends=False)
    put(c - up * 0.9, unit(np.cos(np.radians(115)) * fwd + np.sin(np.radians(115)) * s_), 'ref', 'head')
    put(c - up * 0.9, unit(np.cos(np.radians(-115)) * fwd + np.sin(np.radians(-115)) * s_), 'bias', 'head')

    layers = {l: sum(e['layer'] == l for e in E) for l in ('emg', 'ref', 'bias')}
    mods = sorted(set(e['module'] for e in E))
    print(layers, len(mods), mods)
    for mname in mods:
        print(mname, sum(e['module'] == mname and e['layer'] == 'emg' for e in E))
    json.dump(dict(positions=V.astype(np.float32).round(4).ravel().tolist(),
                   index=tris.ravel().tolist(), electrodes=E), open(sys.argv[2], 'w'))


if __name__ == '__main__':
    main()
