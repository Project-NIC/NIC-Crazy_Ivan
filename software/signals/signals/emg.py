"""The EMG channel (bata/SIGNALS.md, *The EMG channel*), every channel at once, a step at a time.

In: the samples in µV, the units' lost frames already held by the recorder or the reader, a
mask of the samples that were held. Out: the cleaned EMG and, every step of 16 samples (1/120 s),
each channel's log-RMS envelope, NaN where the channel is absent.

- **The band:** a Butterworth high-pass at 10 Hz (20 Hz to be tried), causal, its state kept
  from block to block; the upper edge is the chips' own.
- **The mains:** an adaptive canceller at 50 Hz and its harmonics, every channel its own
  amplitude and phase for each harmonic, learnt by block LMS once a step against one shared
  oscillator, the notch ~0.5 Hz wide; the oscillator follows the mains' frequency from the
  turning of the fundamental's weights, a frequency-locked loop, within ±0.2 Hz of 50, where the
  grid runs, and only while half the channels or more hear the mains ten times over the noise
  their estimate carries from the EMG: the mains comes in on every lead, the heart mostly on the
  trunk's, and an ECG beating as evenly as the simulator's has lines every 1.2 Hz, one at 50.4.
- **The envelope:** ln of the RMS over each step; a channel with more than 2 held samples in the
  step is absent, NaN, which the model's input turns into its "absent" value: variant A's input.
- **Conditioned:** the cleaned samples as i16 of 0.25 µV, variant B's input, the heart left in.
"""
from __future__ import annotations

import numpy as np
from scipy import signal

FS = 1920                 # SPS, the ADS1298s' rate in the suit
STEP = 16                 # samples a step, 1/120 s
ABSENT = np.nan
HELD_MAX = 2              # held samples a step before the envelope is absent (SIGNALS: ~2)
EPS_UV = 0.01             # under the log, far below the chip's 0.8 µVrms
RAW_UV = 0.25             # variant B's step: an i16 of 0.25 µV, ±8.2 mV, the chip's noise ~3 steps


class EmgChain:
    """All the channels of a recording or of the suit, `process` fed blocks of whole steps."""

    def __init__(self, channels: int, fs: int = FS, step: int = STEP, highpass: float = 10.0,
                 order: int = 2, mains: float = 50.0, harmonics: int = 3,
                 notch_width: float = 0.5, track: bool = True, mains_min_uv: float = 1.0,
                 loop_gain: float = 0.1, mains_range: float = 0.2) -> None:
        self.n, self.fs, self.step = channels, fs, step
        self.sos = signal.butter(order, highpass, "highpass", fs=fs, output="sos")
        self.zi = None                                   # set from the first samples
        self.k = np.arange(1, harmonics + 1)[:, None]    # (K, 1)
        self.f0 = mains
        self.f = mains
        self.f_range = mains_range
        self.phase = 0.0
        t = step / fs
        self.alpha = 2 * np.pi * (notch_width / 2) * t   # one pole at half the notch's width
        self.loop_gain = loop_gain
        self.min_power = (mains_min_uv / 2) ** 2         # |W|² of a sine of that amplitude
        self.track = track
        self.W = np.zeros((channels, harmonics), complex)
        self.power = np.zeros(channels)                  # each channel's e², slowly
        self.snr = 10.0                                  # the mains over its estimate's noise
        self.n_t = np.arange(1, step + 1)

    def clean(self, x: np.ndarray) -> np.ndarray:
        """x: (channels, s × step) in µV. The band and the mains: the cleaned EMG."""
        x = np.asarray(x, float)
        if x.shape[0] != self.n or x.shape[1] % self.step:
            raise ValueError(f"({self.n}, a multiple of {self.step}) samples")
        if self.zi is None:                              # start settled on the first sample
            self.zi = signal.sosfilt_zi(self.sos)[:, None, :] * x[None, :, :1]
        y, self.zi = signal.sosfilt(self.sos, x, axis=1, zi=self.zi)
        steps = x.shape[1] // self.step
        y = y.reshape(self.n, steps, self.step)
        out = np.empty_like(y)
        w = 2 * np.pi / self.fs
        block = self.step / self.fs
        for s in range(steps):
            ph = self.phase + w * self.f * self.n_t     # (step,)
            R = np.exp(1j * self.k * ph)                # (K, step)
            e = y[:, s] - (self.W @ R).real             # (n, step)
            out[:, s] = e
            old = self.W[:, 0].copy()
            self.W += self.alpha * (2 / self.step) * (e @ R.conj().T)
            self.power += 0.01 * (np.mean(e * e, axis=1) - self.power)
            # the weights' own noise: 2 α σ² / step a channel, the block LMS's steady state
            heard = np.abs(self.W[:, 0]) ** 2 > np.maximum(
                self.min_power, self.snr * 2 * self.alpha * self.power / self.step)
            if self.track and np.count_nonzero(heard) * 2 >= self.n:
                df = np.angle(np.sum(self.W[:, 0] * old.conj())) / (2 * np.pi * block)
                self.f = float(np.clip(self.f + self.loop_gain * df,
                                       self.f0 - self.f_range, self.f0 + self.f_range))
            self.phase = float(ph[-1] % (2 * np.pi))
        return out.reshape(self.n, steps * self.step)

    def envelope(self, y: np.ndarray, held: np.ndarray | None = None) -> np.ndarray:
        """ln RMS of each step, (channels, s); NaN where more than 2 samples were held."""
        steps = y.shape[1] // self.step
        env = 0.5 * np.log(np.mean(y.reshape(self.n, steps, self.step) ** 2, axis=2)
                           + EPS_UV ** 2)
        if held is not None:
            many = np.asarray(held).reshape(self.n, steps, self.step).sum(axis=2) > HELD_MAX
            env[many] = ABSENT
        return env

    @staticmethod
    def condition(y: np.ndarray) -> tuple[np.ndarray, int]:
        """Variant B's input (bata/SIGNALS.md, *The model*): the cleaned EMG as i16 of 0.25 µV,
        and how many samples hit the ends."""
        q = np.rint(np.asarray(y) / RAW_UV)
        clipped = int(np.count_nonzero((q > 32767) | (q < -32768)))
        return np.clip(q, -32768, 32767).astype(np.int16), clipped

    def process(self, x: np.ndarray, held: np.ndarray | None = None
                ) -> tuple[np.ndarray, np.ndarray]:
        """The cleaned EMG and its envelopes."""
        y = self.clean(x)
        return y, self.envelope(y, held)
