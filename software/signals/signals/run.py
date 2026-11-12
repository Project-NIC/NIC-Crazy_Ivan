"""A recording through the chain: the recorder's BDF+ files in, the envelopes a step, the ECG at
480 SPS, the beats and the vitals out. Block by block, causal, as the live chain will run it.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

import numpy as np
from scipy import signal

from .ecg import EcgOut, HeartRemover, QrsDetector, rmssd_ms
from .emg import STEP, EmgChain
from .imu import Orientation, Still

_RECORDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(
    __file__)))), "recorder")
if _RECORDER not in sys.path:
    sys.path.insert(0, _RECORDER)
from recorder import bdf      # noqa: E402

TRUNK_WORDS = ("chest", "abdomen", "back", "neck")     # where the ECG shows strongly


@dataclass
class Emg:
    """The EMG of one or more files of a recording, in µV, and what the annotations held."""
    labels: list[str]
    units: list[str]                 # each channel's unit, "61"
    names: list[str]                 # each channel's unit's name, from the transducer field
    uv: np.ndarray                   # (channels, samples)
    held: np.ndarray                 # (channels, samples), True where a frame was lost
    fs: int


def read_bdf(path: str) -> bdf.Recording:
    """The recorder's BDF+ read with numpy: the header as `bdf.read` reads it, the samples a
    whole signal at a time, 24 bits to int32."""
    with open(path, "rb") as f:
        head = f.read(256)
        ns = int(head[252:256])
        head += f.read(256 * ns)
        data = np.frombuffer(f.read(), np.uint8)
    text = lambda a, b: head[a:b].decode("ascii").strip()           # noqa: E731
    records = int(text(236, 244))
    rates, cols, pos = [], {}, 256
    for name, width in (("label", 16), ("transducer", 80), ("dimension", 8), ("phys_min", 8),
                        ("phys_max", 8), ("dig_min", 8), ("dig_max", 8), ("prefilter", 80),
                        ("rate", 8), ("reserved", 32)):
        cols[name] = [head[pos + i * width:pos + (i + 1) * width].decode("ascii").strip()
                      for i in range(ns)]
        pos += width * ns
    rates = [int(r) for r in cols["rate"]]
    rec = data[:records * 3 * sum(rates)].reshape(records, 3 * sum(rates))
    signals, samples, annotations, at = [], [], [], 0
    for i in range(ns):
        raw = rec[:, at:at + 3 * rates[i]]
        at += 3 * rates[i]
        if cols["label"][i].endswith("Annotations"):
            annotations += bdf._tals(raw.tobytes())
            continue
        b = raw.reshape(-1, 3).astype(np.int32)
        v = b[:, 0] | b[:, 1] << 8 | b[:, 2] << 16
        samples.append(np.where(v & 0x800000, v - (1 << 24), v))
        signals.append(bdf.Signal(cols["label"][i], rates[i], cols["dimension"][i],
                                  float(cols["phys_min"][i]), float(cols["phys_max"][i]),
                                  int(cols["dig_min"][i]), int(cols["dig_max"][i]),
                                  cols["transducer"][i], cols["prefilter"][i]))
    return bdf.Recording(None, float(text(244, 252)), signals, samples, annotations)


def load(paths: list[str]) -> Emg:
    labels, units, names, data, held = [], [], [], [], []
    n = None
    for p in paths:
        r = read_bdf(p)
        gaps = [(a[0], a[1] or 0.0, a[2][4:]) for a in r.annotations if a[2].startswith("gap ")]
        for s, v in zip(r.signals, r.samples):
            if not s.label.startswith("EMG "):
                continue
            fs = int(round(s.rate / r.record_seconds))
            scale = (s.phys_max - s.phys_min) / (s.dig_max - s.dig_min)
            x = (np.asarray(v, float) - s.dig_min) * scale + s.phys_min
            unit = s.label[4:6]
            h = np.zeros(len(x), bool)
            for onset, length, u in gaps:
                if u == unit:
                    h[int(round(onset * fs)):int(round((onset + length) * fs))] = True
            labels.append(s.label)
            units.append(unit)
            names.append(s.transducer.rpartition("unit ")[2])
            data.append(x)
            held.append(h)
            n = len(x) if n is None else min(n, len(x))
    if not data:
        raise ValueError("no EMG in the files")
    return Emg(labels, units, names, np.array([d[:n] for d in data]),
               np.array([h[:n] for h in held]), fs)


@dataclass
class Result:
    envelopes: np.ndarray            # (channels, steps), ln µV RMS, NaN absent
    ecg: np.ndarray                  # (ECG channels, samples at 480 SPS), µV
    ecg_labels: list[str]
    beats: list[int]                 # R, samples from the start
    heart_rate: float                # beats a minute over the recording
    rmssd: float                     # ms
    mains: list[float] = field(default_factory=list)     # the tracked frequency, once a second
    delay: int = 0                   # samples the envelopes are late by the heart's removal
    raw: np.ndarray | None = None    # variant B's input, (channels, samples), i16 of 0.25 µV
    clipped: int = 0                 # its samples that hit the ends


def strongest_r(x: np.ndarray, fs: int, seconds: float = 5.0) -> int:
    """The channel whose 5–15 Hz band swings the most in the first seconds."""
    sos = signal.butter(2, (5, 15), "bandpass", fs=fs, output="sos")
    bp = signal.sosfilt(sos, x[:, :int(seconds * fs)], axis=1)
    return int(np.argmax(np.percentile(np.abs(bp), 99.5, axis=1)))


def process(emg: Emg, highpass: float = 10.0, heart: bool = True, block_s: float = 1.0,
            mains: float = 50.0, raw: bool = False) -> Result:
    """Variant A's envelopes, the ECG, the beats; with `raw`, variant B's conditioned samples
    too, taken before the heart's removal and not late."""
    fs, n = emg.fs, emg.uv.shape[0]
    trunk = [i for i, name in enumerate(emg.names) if any(w in name for w in TRUNK_WORDS)]
    chain = EmgChain(n, fs, highpass=highpass, mains=mains)
    qrs_ch = trunk[strongest_r(emg.uv[trunk], fs)] if trunk else None
    qrs = QrsDetector(fs) if qrs_ch is not None else None
    first_of = {}
    for i, u in enumerate(emg.units):                  # each trunk unit's first channel
        if i in trunk and u not in first_of:
            first_of[u] = i
    ecg_ch = list(first_of.values())[:3]
    ecg = EcgOut(len(ecg_ch), fs) if ecg_ch else None
    remover = HeartRemover(len(trunk), fs) if heart and trunk else None
    delay = remover.delay if remover else 0
    pend = np.zeros((n, delay))                        # the channels not cleaned, kept as late
    held_pend = np.ones((n, delay), bool)             # nothing yet: the first envelopes absent
    block = int(block_s * fs) // STEP * STEP
    envs, ecgs, beats, track, raws, clipped = [], [], [], [], [], 0
    total = emg.uv.shape[1] // STEP * STEP
    for b in range(0, total, block):
        x = emg.uv[:, b:b + block]
        h = emg.held[:, b:b + block]
        y = chain.clean(x)
        if raw:
            q, c = chain.condition(y)
            raws.append(q)
            clipped += c
        found = qrs.process(x[qrs_ch]) if qrs else []
        beats += found
        if ecg:
            ecgs.append(ecg.process(x[ecg_ch]))
        if remover:
            cleaned = remover.process(y[trunk], found)
            late = np.concatenate((pend, y), axis=1)
            late_h = np.concatenate((held_pend, h), axis=1)
            y, pend = late[:, :y.shape[1]], late[:, y.shape[1]:]
            h, held_pend = late_h[:, :h.shape[1]], late_h[:, h.shape[1]:]
            y[trunk] = cleaned
        envs.append(chain.envelope(y, h))
        track.append(chain.f)
    rr = np.diff(beats) / fs if len(beats) > 1 else np.array([])
    return Result(np.concatenate(envs, axis=1),
                  np.concatenate(ecgs, axis=1) if ecgs else np.zeros((0, 0), np.int16),
                  [emg.labels[i] for i in ecg_ch], beats,
                  float(60 / np.mean(rr)) if len(rr) else 0.0, rmssd_ms(beats, fs), track,
                  delay, np.concatenate(raws, axis=1) if raws else None, clipped)


def orientations(paths: list[str]) -> tuple[list[str], np.ndarray]:
    """Every IMU of a recording turned into its orientation step by step: the IMUs' names
    ("61-1"), the quaternions (IMUs, steps, 4). Each unit's still seconds set its gyros'
    offsets before the filter."""
    rates, forces, names = {}, {}, []
    for p in paths:
        r = read_bdf(p)
        for sig, v in zip(r.signals, r.samples):
            kind, _, rest = sig.label.partition(" ")
            if kind not in ("Gyr", "Acc"):
                continue
            imu, _, axis = rest.rpartition(" ")
            scale = (sig.phys_max - sig.phys_min) / (sig.dig_max - sig.dig_min)
            x = (np.asarray(v, float) - sig.dig_min) * scale + sig.phys_min
            (rates if kind == "Gyr" else forces).setdefault(imu, [None] * 3)["XYZ".index(axis)] = x
            if imu not in names:
                names.append(imu)
    if not names:
        return [], np.zeros((0, 0, 4))
    w = np.stack([np.stack(rates[i], axis=1) for i in names], axis=1)     # (steps, imus, 3)
    a = np.stack([np.stack(forces[i], axis=1) for i in names], axis=1)
    units = sorted({i.split("-")[0] for i in names})
    still = {u: Still(sum(1 for i in names if i.startswith(u + "-"))) for u in units}
    member = {u: [k for k, i in enumerate(names) if i.startswith(u + "-")] for u in units}
    f = Orientation(len(names))
    out = np.empty((w.shape[0], len(names), 4))
    for t in range(w.shape[0]):
        wt = w[t].copy()
        for u in units:
            wt[member[u]] -= still[u].feed(w[t, member[u]])
        out[t] = f.step(wt, a[t])
    return names, out.transpose(1, 0, 2)
