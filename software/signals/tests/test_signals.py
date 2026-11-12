import os
import tempfile
import unittest

import numpy as np

from signals import EmgChain, EcgOut, HeartRemover, QrsDetector
from signals.emg import FS, STEP

RNG = np.random.default_rng(7)


def run_chain(chain, x, block=FS):
    out, env = [], []
    for b in range(0, x.shape[1], block):
        y, e = chain.process(x[:, b:b + block])
        out.append(y)
        env.append(e)
    return np.concatenate(out, axis=1), np.concatenate(env, axis=1)


def ecg_like(n, rate=70, seconds=40, jitter=0.04):
    """A QRS of ~1 mV, a T wave, beats a little irregular; the R samples."""
    t = np.arange(int(seconds * FS)) / FS
    x = np.zeros_like(t)
    rs, at = [], 1.0
    while at < seconds - 1:
        r = int(at * FS)
        rs.append(r)
        k = np.arange(-int(0.05 * FS), int(0.4 * FS))
        tt = k / FS
        wave = (1000 * np.exp(-(tt / 0.006) ** 2) - 250 * np.exp(-((tt - 0.018) / 0.006) ** 2)
                + 200 * np.exp(-((tt - 0.25) / 0.04) ** 2))
        x[r + k] += wave
        at += 60 / rate * (1 + jitter * RNG.uniform(-1, 1))
    return x, rs


class TestEmg(unittest.TestCase):
    def test_band(self):
        t = np.arange(10 * FS) / FS
        x = np.vstack([30000 + 2000 * np.sin(2 * np.pi * 0.5 * t),       # offset and drift
                       100 * np.sin(2 * np.pi * 100 * t)])                   # EMG band
        y, _ = run_chain(EmgChain(2, track=False, harmonics=1, notch_width=1e-9), x)
        self.assertLess(np.abs(y[0, 5 * FS:]).max(), 5)
        self.assertAlmostEqual(y[1, 5 * FS:].std() / x[1, 5 * FS:].std(), 1.0, delta=0.02)

    def test_mains_tracked_and_taken_out(self):
        n, t = 16, np.arange(20 * FS) / FS
        noise = RNG.normal(0, 10, (n, len(t)))
        amp, ph = RNG.uniform(5, 30, (n, 1)), RNG.uniform(0, 6.3, (n, 1))
        f = 50.15
        mains = (amp * np.sin(2 * np.pi * f * t + ph) + 0.3 * amp * np.sin(4 * np.pi * f * t)
                 + 0.2 * amp * np.sin(6 * np.pi * f * t + ph))
        chain = EmgChain(n)
        y, _ = run_chain(chain, noise + mains)
        self.assertAlmostEqual(chain.f, f, delta=0.02)
        last = slice(-4 * FS, None)
        for k in (1, 2, 3):
            left = np.abs((y[:, last] * np.exp(-2j * np.pi * k * f * t[last])).mean(axis=1)) * 2
            self.assertLess(left.mean(), 0.5)                               # µV, from 5–30
        self.assertGreater(np.var(y[:, last]) / np.var(noise[:, last]), 0.97)

    def test_no_mains_no_wandering(self):
        chain = EmgChain(8)
        run_chain(chain, RNG.normal(0, 10, (8, 10 * FS)))
        self.assertAlmostEqual(chain.f, 50.0, delta=0.05)

    def test_envelope_and_absent(self):
        t = np.arange(4 * FS) / FS
        x = np.vstack([200 * np.sin(2 * np.pi * 120 * t)] * 2)
        chain = EmgChain(2, track=False)
        y = chain.clean(x)
        held = np.zeros_like(x, bool)
        held[0, STEP * 300:STEP * 300 + 3] = True           # 3 held samples: absent
        held[1, STEP * 300:STEP * 300 + 2] = True           # 2: still there
        env = chain.envelope(y, held)
        self.assertAlmostEqual(np.nanmean(env[1, 200:]), np.log(200 / np.sqrt(2)), delta=0.02)
        self.assertTrue(np.isnan(env[0, 300]))
        self.assertFalse(np.isnan(env[1, 300]))
        self.assertEqual(int(np.isnan(env).sum()), 1)


class TestRaw(unittest.TestCase):
    def test_conditioned(self):
        y = np.array([[0.0, 0.25, -0.25, 1000.0, 8191.75, 9000.0, -9000.0]])
        q, clipped = EmgChain.condition(y)
        self.assertEqual(q.dtype, np.int16)
        self.assertEqual(q.tolist(), [[0, 1, -1, 4000, 32767, 32767, -32768]])
        self.assertEqual(clipped, 2)


class TestEcg(unittest.TestCase):
    def test_qrs(self):
        x, rs = ecg_like(1)
        x = x + RNG.normal(0, 20, len(x))
        q = QrsDetector()
        beats = []
        for b in range(0, len(x), STEP * 8):
            beats += q.process(x[b:b + STEP * 8])
        late = [r for r in rs if r > 2.5 * FS]                     # after the 2 s of learning
        hit = sum(any(abs(b - r) < 0.05 * FS for b in beats) for r in late)
        self.assertGreaterEqual(hit / len(late), 0.97)
        self.assertLessEqual(len([b for b in beats if b > 2.5 * FS]), len(late) + 1)

    def test_heart_removed(self):
        ecg, rs = ecg_like(1, seconds=60)
        n = 4
        gains = np.array([1.0, -0.6, 0.3, 0.15])[:, None]
        clean = RNG.normal(0, 20, (n, len(ecg)))
        x = clean + gains * np.vstack([np.roll(ecg, d) for d in (0, 10, 20, -15)])
        h = HeartRemover(n)
        out = []
        for b in range(0, x.shape[1], FS):
            out.append(h.process(x[:, b:b + FS], [r for r in rs if b <= r < b + FS]))
        y = np.concatenate(out, axis=1)[:, h.delay:]
        x, clean = x[:, :y.shape[1]], clean[:, :y.shape[1]]
        late = slice(30 * FS, None)
        before = np.mean((x - clean)[:, late] ** 2)
        after = np.mean((y - clean)[:, late] ** 2)
        self.assertLess(10 * np.log10(after / before), -15)                 # the heart, dB

    def test_heart_adds_no_noise(self):
        x = RNG.normal(0, 30, (4, 40 * FS))
        rs = list(range(3000, 38 * FS, 1600))
        h = HeartRemover(4)
        out = [h.process(x[:, b:b + FS], [r for r in rs if b <= r < b + FS])
               for b in range(0, x.shape[1], FS)]
        y = np.concatenate(out, axis=1)[:, h.delay:]
        self.assertLess(y[:, 20 * FS:].std() / x[:, 20 * FS:y.shape[1]].std(), 1.03)

    def test_ecg_out(self):
        t = np.arange(4 * FS) / FS
        x = np.vstack([1000 * np.sin(2 * np.pi * 10 * t)])
        e = EcgOut(1)
        y = np.concatenate([e.process(x[:, b:b + 100 * STEP // 10 * 10])
                            for b in range(0, x.shape[1], 100 * STEP // 10 * 10)], axis=1)
        self.assertEqual(y.dtype, np.int16)
        self.assertEqual(y.shape[1], x.shape[1] // 4)
        self.assertAlmostEqual(np.abs(y[0, 480:]).max(), 1000, delta=40)


class TestRecording(unittest.TestCase):
    def test_from_the_recorder(self):
        import sys
        here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, os.path.join(here, "recorder"))
        import recorder                                   # noqa: F401, the protocol's path
        from recorder import Recorder
        from recorder.table import Unit
        from suitsim import Suit
        from ci import stp
        from signals.run import load, process
        suit = Suit.standard(16, gloves=False, socks=False, line8=False)
        table = [Unit(u.number, u.name, u.line, u.slot, u.kind, u.ads, u.imus)
                 for u in suit.units]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "r.bdf")
            rec = Recorder(table, path, imus=False)
            for _ in range(12 * stp.ADS_SPS):
                t1, share = suit.cycle()
                rec.feed(1, t1)
                rec.feed(2, stp.join(*share))
            rec.close()
            emg = load([path])
        r = process(emg, raw=True)
        self.assertEqual(r.envelopes.shape, (emg.uv.shape[0], 12 * 120))
        self.assertEqual(r.raw.shape, emg.uv.shape)
        self.assertEqual(r.clipped, 0)
        self.assertAlmostEqual(r.heart_rate, 72.0, delta=1.0)          # the simulator's 72
        self.assertEqual(r.ecg.shape, (3, 12 * 480))
        self.assertGreaterEqual(len(r.beats), 11)


if __name__ == "__main__":
    unittest.main()
