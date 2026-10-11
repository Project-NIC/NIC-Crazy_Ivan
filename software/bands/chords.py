"""Which pairs of a band's sixteen electrodes to measure.

A band is a ring of 16 electrodes round a limb, one ADS1299: P1–P8 on the even places 0, 2, …,
14, the N electrodes on the odd ones. Differentially channel k measures P_k − N_π(k); against
the reference each P_k is measured against one point. The script tries every pairing π of the
P with the N electrodes, 8! = 40,320 of them, on many random cross-sections, and scores each.

The model is a sketch, not anatomy:
- the limb is a disk of radius 1 with even conductivity and an insulating skin; a muscle is a
  source whose potential on the skin falls as −ln|e − s|, the 2D field of a line source with its
  image in the insulated boundary (the image doubles it, a constant that cancels in every
  difference);
- against the reference, the reference is the mean over the whole skin, which for this field is
  0 (the mean-value property): a far, quiet point. Such a ring then sees 7 independent mixes at
  most, so 7 muscles are scored;
- each trial puts 7 superficial muscles at random angles, 0.55–0.85 of the radius, and 4 deep
  ones at 0.2–0.45, the same trials for every pairing.

What is scored, as the median over the trials:
- cond: σ_min / σ_max of the lead field of the 7 superficial muscles, how well they can be told
  apart (1 perfect, 0 blind to some mix); bad: the share of trials with cond below 0.05;
- deep: the deep muscles' mean sensitivity against the superficial ones';
- shift: how much the channels change when the band sits half a place (~1 cm) round from where
  it sat, ‖L(shifted) − L‖ / ‖L‖; the suit never sits the same way twice, so lower is better.

Python 3 with NumPy. Run:  python3 chords.py [trials]
"""

import itertools
import math
import sys

import numpy as np

N_EL = 16
P_SLOTS = np.arange(0, N_EL, 2)
N_SLOTS = np.arange(1, N_EL, 2)
ANGLES = 2 * np.pi * np.arange(N_EL) / N_EL
HALF_PLACE = np.pi / N_EL
N_SUP, N_DEEP = 7, 4


def potentials(srcs: np.ndarray, turn: float = 0.0) -> np.ndarray:
    """16 × S: each electrode's potential from each source, the band turned by `turn` rad."""
    a = ANGLES + turn
    el = np.stack([np.cos(a), np.sin(a)], axis=1)
    d = el[:, None, :] - srcs[None, :, :]
    return -np.log(np.hypot(d[..., 0], d[..., 1]))


def random_sources(rng, count: int, r_lo: float, r_hi: float) -> np.ndarray:
    a = rng.uniform(0, 2 * np.pi, count)
    r = rng.uniform(r_lo, r_hi, count)
    return np.stack([r * np.cos(a), r * np.sin(a)], axis=1)


def all_pairings() -> np.ndarray:
    """40,320 × 8: for each pairing, the N place of P_k."""
    return N_SLOTS[np.array(list(itertools.permutations(range(8))))]


def fixed_offset(step: int) -> np.ndarray:
    """P at place 2k paired with the N at place 2k + step (step odd)."""
    return (P_SLOTS + step) % N_EL


def chord_lengths(n_places: np.ndarray) -> list[int]:
    d = (n_places - P_SLOTS) % N_EL
    return [int(min(x, N_EL - x)) for x in d]


def evaluate(pairings: np.ndarray, trials: int, seed: int = 1) -> dict[str, np.ndarray]:
    """For every pairing (rows of N places) the median cond, the bad share and the median deep."""
    rng = np.random.default_rng(seed)
    conds, deeps, shifts = [], [], []
    for _ in range(trials):
        srcs = random_sources(rng, N_SUP, 0.55, 0.85)
        sup, turned = potentials(srcs), potentials(srcs, HALF_PLACE)
        deep = potentials(random_sources(rng, N_DEEP, 0.2, 0.45))
        lf_sup = sup[P_SLOTS][None, :, :] - sup[pairings]          # pairings × 8 × 7
        lf_turned = turned[P_SLOTS][None, :, :] - turned[pairings]
        lf_deep = deep[P_SLOTS][None, :, :] - deep[pairings]
        sv = np.linalg.svd(lf_sup, compute_uv=False)
        conds.append(sv[:, -1] / sv[:, 0])
        deeps.append(np.linalg.norm(lf_deep, axis=1).mean(axis=1)
                     / np.linalg.norm(lf_sup, axis=1).mean(axis=1))
        shifts.append(np.linalg.norm(lf_turned - lf_sup, axis=(1, 2))
                      / np.linalg.norm(lf_sup, axis=(1, 2)))
    conds, deeps, shifts = np.array(conds), np.array(deeps), np.array(shifts)
    return {"cond": np.median(conds, axis=0), "bad": (conds < 0.05).mean(axis=0),
            "deep": np.median(deeps, axis=0), "shift": np.median(shifts, axis=0)}


def evaluate_reference(trials: int, seed: int = 1) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    conds, deeps, shifts = [], [], []
    for _ in range(trials):
        srcs = random_sources(rng, N_SUP, 0.55, 0.85)
        sup, turned = potentials(srcs)[P_SLOTS], potentials(srcs, HALF_PLACE)[P_SLOTS]
        deep = potentials(random_sources(rng, N_DEEP, 0.2, 0.45))[P_SLOTS]
        sv = np.linalg.svd(sup, compute_uv=False)
        conds.append(sv[-1] / sv[0])
        deeps.append(np.linalg.norm(deep, axis=0).mean() / np.linalg.norm(sup, axis=0).mean())
        shifts.append(np.linalg.norm(turned - sup) / np.linalg.norm(sup))
    conds = np.array(conds)
    return {"cond": float(np.median(conds)), "bad": float((conds < 0.05).mean()),
            "deep": float(np.median(deeps)), "shift": float(np.median(shifts))}


def main() -> None:
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    pairings = all_pairings()
    res = evaluate(pairings, trials)
    named = {f"every chord +{s}": fixed_offset(s) for s in (1, 3, 5, 7)}
    mix = fixed_offset(1)
    mix[[0, 4]] = mix[[4, 0]]                      # P1 and P5 swap partners: two diameters
    named["6 neighbours + 2 diameters"] = mix
    index = {tuple(p): i for i, p in enumerate(pairings)}

    def line(name, i):
        print(f"{name:<28} {res['cond'][i]:6.3f} {res['bad'][i]:6.2f} {res['deep'][i]:6.3f} "
              f"{res['shift'][i]:6.2f}  {chord_lengths(pairings[i])}")

    print(f"{trials} trials")
    print(f"{'pairing':<28} {'cond':>6} {'bad':>6} {'deep':>6} {'shift':>6}  chord lengths")
    for name, p in named.items():
        line(name, index[tuple(p)])
    best = int(np.argmax(res["cond"]))
    line("best cond of all 8!", best)
    print(f"{'':<28} P place → N place: {list(zip(P_SLOTS.tolist(), pairings[best].tolist()))}")
    steady = int(np.argmin(res["shift"]))
    line("least shift of all 8!", steady)
    print(f"{'':<28} P place → N place: {list(zip(P_SLOTS.tolist(), pairings[steady].tolist()))}")
    ref = evaluate_reference(trials)
    print(f"{'against the reference':<28} {ref['cond']:6.3f} {ref['bad']:6.2f} {ref['deep']:6.3f} "
          f"{ref['shift']:6.2f}")


if __name__ == "__main__":
    main()
