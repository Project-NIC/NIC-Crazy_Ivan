"""The ECG (bata/SIGNALS.md, *The ECG and the breath*): the QRS by Pan and Tompkins (IEEE Trans.
Biomed. Eng. 1985), the ECG out at 480 SPS and the heart taken out of the EMG by a template a
channel. Causal, block by block, as the live chain will run it.
"""
from __future__ import annotations

from collections import deque

import numpy as np
from scipy import signal

FS = 1920


class QrsDetector:
    """One channel, the trunk's with the strongest R wave. Band-pass 5–15 Hz, the five-point
    derivative, squaring, a moving window of 150 ms, then the adaptive thresholds on the
    window's peaks: a peak over THRESHOLD I1 = NPKI + (SPKI − NPKI) / 4 a beat, its level into
    SPKI, else into NPKI, each by 1/8; 200 ms refractory; a search back at I1 / 2 when no beat
    came within 1.66 of the mean RR. The beat's R is the largest swing above 5 Hz in the window
    before the peak, the band-passed signal's two lobes being too alike to tell the R by.
    `process` returns the beats found in the block, as sample numbers from the start; they come
    ~0.2–0.4 s after their R."""

    def __init__(self, fs: int = FS) -> None:
        self.fs = fs
        self.sos = signal.butter(2, (5, 15), "bandpass", fs=fs, output="sos")
        self.zi = np.zeros((self.sos.shape[0], 2))
        self.hp = signal.butter(1, 5, "highpass", fs=fs, output="sos")   # for the R's place
        self.hp_zi = np.zeros((1, 2))
        self.win = int(0.150 * fs)
        self.refractory = int(0.200 * fs)
        self.bp_hist = np.zeros(0)
        self.sq_tail = np.zeros(self.win)
        self.d_tail = np.zeros(4)
        self.mwi_last = np.zeros(2)
        self.t = 0                               # samples seen
        self.block_end = 0
        self.spki = self.npki = 0.0
        self.learning = int(2 * fs)              # the first 2 s set the levels
        self.learn_max = 0.0
        self.last_beat = -10 ** 9                # the last R
        self.last_peak = -10 ** 9                # the last beat's peak of the window
        self.rr: deque[int] = deque(maxlen=8)
        self.noise_peaks: list[tuple[int, float]] = []
        self.beats: list[int] = []

    def _threshold(self) -> float:
        return self.npki + 0.25 * (self.spki - self.npki)

    def process(self, x: np.ndarray) -> list[int]:
        x = np.asarray(x, float)
        bp, self.zi = signal.sosfilt(self.sos, x, zi=self.zi)
        hp, self.hp_zi = signal.sosfilt(self.hp, x, zi=self.hp_zi)
        ext = np.concatenate((self.d_tail, bp))
        d = (2 * ext[4:] + ext[3:-1] - ext[1:-3] - 2 * ext[:-4]) / 8 * self.fs
        self.d_tail = ext[-4:]
        sq = d * d
        ext_sq = np.concatenate((self.sq_tail, sq))
        c = np.cumsum(ext_sq)
        mwi = (c[self.win:] - c[:-self.win]) / self.win     # the window ending at each sample
        self.sq_tail = ext_sq[-self.win:]
        keep = int(4 * self.fs)                    # a search back reaches 1.66 RR, to 30 bpm
        self.bp_hist = np.concatenate((self.bp_hist, hp))[-(keep + len(hp)):]
        ext_m = np.concatenate((self.mwi_last, mwi))
        peaks = np.nonzero((ext_m[1:-1] > ext_m[:-2]) & (ext_m[1:-1] >= ext_m[2:]))[0]
        self.mwi_last = ext_m[-2:]
        found = []
        self.block_end = self.t + len(x)
        start = self.t - 1                         # ext_m[1] is sample self.t - 1
        for p in peaks:
            at, level = start + p, ext_m[p + 1]
            if at < self.learning:
                self.learn_max = max(self.learn_max, level)
                continue
            if self.spki == 0:
                self.spki, self.npki = 0.5 * self.learn_max, 0.0
            if at - self.last_peak < self.refractory:
                continue
            if level > self._threshold():
                found.append(self._beat(at, level))
            else:
                self.npki = 0.125 * level + 0.875 * self.npki
                self.noise_peaks.append((at, level))
                found += self._search_back(at)
        self.t += len(x)
        return found

    def _search_back(self, now: int) -> list[int]:
        if len(self.rr) < 2 or now - self.last_beat < 1.66 * np.mean(self.rr):
            return []
        cand = [(a, lv) for a, lv in self.noise_peaks
                if a - self.last_peak >= self.refractory and lv > self._threshold() / 2]
        self.noise_peaks = []
        if not cand:
            return []
        at, level = max(cand, key=lambda c: c[1])
        self.spki = 0.25 * level + 0.75 * self.spki
        return [self._beat(at, level, update=False)]

    def _beat(self, at: int, level: float, update: bool = True) -> int:
        if update:
            self.spki = 0.125 * level + 0.875 * self.spki
        # R: the largest swing above 5 Hz in the window before the peak
        end = len(self.bp_hist) - (self.block_end - at) + 1      # bp_hist[end - 1] is `at`
        lo = max(0, end - self.win - int(0.03 * self.fs))
        seg = self.bp_hist[lo:end]
        r = at - (end - 1 - lo) + int(np.argmax(np.abs(seg))) if end > 0 else at
        if self.last_beat > 0:
            self.rr.append(r - self.last_beat)
        self.last_beat, self.last_peak = r, at
        self.noise_peaks = []
        self.beats.append(r)
        return r


class EcgOut:
    """The ECG of a few channels, band-passed 0.5–40 Hz from the raw samples, every fourth sample,
    1 µV a step in an i16: the packet of type 3 at 480 SPS."""

    def __init__(self, channels: int, fs: int = FS, decimation: int = 4) -> None:
        self.sos = signal.butter(2, (0.5, 40), "bandpass", fs=fs, output="sos")
        self.zi = None
        self.decimation = decimation
        self.phase = 0

    def process(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, float)
        if self.zi is None:
            self.zi = signal.sosfilt_zi(self.sos)[:, None, :] * x[None, :, :1]
        y, self.zi = signal.sosfilt(self.sos, x, axis=1, zi=self.zi)
        first = (-self.phase) % self.decimation
        self.phase = (self.phase + x.shape[1]) % self.decimation
        return np.clip(np.rint(y[:, first::self.decimation]), -32768, 32767).astype(np.int16)


class HeartRemover:
    """The heart taken out of EMG channels: each channel's beat, from 0.15 s before the R to 0.45 s
    after it, averaged over the last beats (each new one weighs 1/16), subtracted at every beat;
    the template is the earlier beats', so the beat's own EMG stays. Where the template is mostly
    the EMG averaged in, not the heart, it is shrunk before it is taken away, sample by sample, by
    T² / (T² + its noise's variance), the noise from the beats' spread about the template; so the
    QRS goes and the quiet stretches between beats get no noise added. The output is late by
    `delay`, long enough for a beat's whole window and the detector's lag. The first beats make
    a plain mean, then each new one weighs 1/16; nothing is taken away before the eighth. Each
    beat is moved by up to ±5 ms to where it matches the template best, the detector's R being
    a few samples off from beat to beat."""

    def __init__(self, channels: int, fs: int = FS, pre: float = 0.15, post: float = 0.45,
                 lag: float = 0.4, weight: float = 1 / 16, warm: int = 8,
                 align: float = 0.005) -> None:
        self.pre, self.post = int(pre * fs), int(post * fs)
        self.delay = self.pre + self.post + int(lag * fs)
        self.buf = np.zeros((channels, self.delay))
        self.t = 0                                 # samples in, the buffer's end
        self.template = np.zeros((channels, self.pre + self.post))
        self.square = np.zeros_like(self.template)       # the beats' mean square, for the spread
        self.beats: deque[int] = deque()
        self.weight, self.warm, self.seen = weight, warm, 0
        self.align = int(align * fs)               # a beat moved to the template by ±5 ms

    def process(self, x: np.ndarray, beats: list[int] = ()) -> np.ndarray:
        x = np.asarray(x, float)
        n = x.shape[1]
        self.beats.extend(beats)
        out = np.empty_like(x)
        # the buffer as a window over samples [t - delay, t); the block passes through it
        work = np.concatenate((self.buf, x), axis=1)          # samples [t - delay, t + n)
        base = self.t - self.delay
        while self.beats and self.beats[0] + self.post + self.align <= self.t + n:
            r = self.beats.popleft()
            lo, hi = r - self.pre - base, r + self.post - base
            if lo - self.align < 0 or hi + self.align > work.shape[1]:
                continue                                       # too late for this beat
            if self.seen >= self.warm and self.align:
                best, shift = -np.inf, 0
                for k in range(-self.align, self.align + 1):
                    c = float(np.sum(work[:, lo + k:hi + k] * self.template))
                    if c > best:
                        best, shift = c, k
                lo, hi = lo + shift, hi + shift
            seg = work[:, lo:hi].copy()
            if self.seen >= self.warm:
                t2 = self.template ** 2
                spread = np.maximum(self.square - t2, 0.0)
                n_eff = min(self.seen, (2 - self.weight) / self.weight)
                work[:, lo:hi] -= self.template * t2 / (t2 + spread / n_eff + 1e-12)
            w = max(self.weight, 1.0 / (self.seen + 1))   # a plain mean until 1/weight beats
            self.template += w * (seg - self.template)
            self.square += w * (seg * seg - self.square)
            self.seen += 1
        out = work[:, :n]
        self.buf = work[:, n:]
        self.t += n
        return out


def rmssd_ms(beats: list[int], fs: int = FS) -> float:
    """The RMS of successive differences of the RR intervals, ms."""
    rr = np.diff(beats) / fs * 1000
    return float(np.sqrt(np.mean(np.diff(rr) ** 2))) if len(rr) > 1 else 0.0
