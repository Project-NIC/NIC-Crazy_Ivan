"""The skin of MakeHuman's base mesh (CC0): its joints, rays cast onto it from inside, a limb's
girth. Units: decimetres, +x the model's left, +y up, +z front."""
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
