import datetime as dt
import os
import tempfile
import unittest

import recorder                                  # noqa: F401, puts software/protocol on the path
from recorder import bdf, Recorder
from recorder.record import MAX_SIGNALS
from recorder.table import Unit
from ci import stp
from suitsim import Suit

START = dt.datetime(2026, 11, 11, 10, 0, 0)


def table_of(suit: Suit) -> list[Unit]:
    return [Unit(u.number, u.name, u.line, u.slot, u.kind, u.ads, u.imus) for u in suit.units]


def run(suit: Suit, seconds: int, path: str, **kw) -> tuple[Recorder, dict, list]:
    """The suit for whole seconds into a recording, and the transfers it sent."""
    rec = Recorder(table_of(suit), path, start=START, **kw)
    sent = []
    for _ in range(seconds * stp.ADS_SPS):
        t1, share = suit.cycle()
        t2 = stp.join(*share)
        sent.append((t1, t2))
        rec.feed(1, t1)
        rec.feed(2, t2)
    return rec, rec.close(), sent


class TestBDF(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "a.bdf")
            signals = [bdf.Signal("EMG 61-01", 4, "uV", -333333, 333333),
                       bdf.Signal("Gyr 61-1 X", 2, "deg/s", -2293.76, 2293.69, -32768, 32767)]
            w = bdf.Writer(path, signals, START, annotation_bytes=120)
            w.annotate(0.25, "gap 61", 0.5)
            w.write_record([[bdf.DIG_MIN, -1, 0, bdf.DIG_MAX], [-32768, 32767]])
            w.annotate(1.5, "Mamka event 1 2")
            w.write_record([[1, 2, 3, 4], [5, 6]])
            w.close()
            r = bdf.read(path)
            self.assertEqual(r.start, START)
            self.assertEqual([s.label for s in r.signals], ["EMG 61-01", "Gyr 61-1 X"])
            self.assertEqual([s.rate for s in r.signals], [4, 2])
            self.assertEqual(r.samples[0], [bdf.DIG_MIN, -1, 0, bdf.DIG_MAX, 1, 2, 3, 4])
            self.assertEqual(r.samples[1], [-32768, 32767, 5, 6])
            self.assertEqual(r.signals[1].phys_min, -2293.76)
            self.assertEqual(r.annotations, [(0.25, 0.5, "gap 61"), (1.5, None, "Mamka event 1 2")])
            with open(path, "rb") as f:
                head = f.read(256)
            self.assertEqual(head[:8], b"\xffBIOSEMI")
            self.assertEqual(head[192:197], b"BDF+C")
            self.assertEqual(head[236:244].strip(), b"2")
            self.assertEqual(os.path.getsize(path), 256 * 4 + 2 * 3 * (4 + 2 + 40))

    def test_limits(self):
        with tempfile.TemporaryDirectory() as d:
            w = bdf.Writer(os.path.join(d, "b.bdf"), [bdf.Signal("S", 1)], START)
            with self.assertRaises(ValueError):
                w.write_record([[bdf.DIG_MAX + 1]])
            with self.assertRaises(ValueError):
                w.write_record([[0, 0]])
            w.close()
            with self.assertRaises(ValueError):
                bdf.Writer(os.path.join(d, "c.bdf"), [bdf.Signal("a label of more than 16", 1)],
                           START)


class TestRecorder(unittest.TestCase):
    def test_samples_as_the_frames_carried_them(self):
        suit = Suit.standard(2, line8=False, gloves=False, socks=False)
        with tempfile.TemporaryDirectory() as d:
            rec, stats, sent = run(suit, 2, os.path.join(d, "r.bdf"))
            self.assertEqual(stats["seconds"], 2)
            self.assertEqual((stats["gaps"], stats["lost cycles"]), (0, 0))
            r = bdf.read(os.path.join(d, "r.bdf"))
        unit = suit.of(1)[0]
        sizes = [u.place for u in suit.placed(1)]
        truth = [[] for _ in range(16)]
        steps = stp.StepAssembler(unit.imus, stp.MODULE_IMU)
        got_steps = []
        for c, (t1, _) in enumerate(sent):
            data, _ = stp.parse_cycle(t1, sizes)
            _, _, channels, imu = stp.parse_data(data[0])
            for k, v in enumerate(channels):
                truth[k].append(v)
            steps.feed(c, imu)
            got_steps += steps.steps
            steps.steps.clear()
        labels = [s.label for s in r.signals]
        for k in range(16):
            i = labels.index(f"EMG {unit.number:02X}-{k + 1:02d}")
            self.assertEqual(r.samples[i], truth[k])
        first_imu = [s for p, i, s in got_steps if i == 0]
        first_imu = first_imu[1:] + first_imu[-1:]      # a step's turn sent in the next step
        gx = r.samples[labels.index(f"Gyr {unit.number:02X}-1 X")]
        az = r.samples[labels.index(f"Acc {unit.number:02X}-1 Z")]
        self.assertEqual(len(gx), 2 * 120)
        self.assertEqual(gx, [stp.struct.unpack("<3h3h", s)[0] for s in first_imu])
        self.assertEqual(az, [stp.struct.unpack("<3h3h", s)[5] for s in first_imu])

    def test_gaps_held_and_marked(self):
        suit = Suit.standard(2, line8=False, gloves=False, socks=False, bad_frame_rate=0.01)
        with tempfile.TemporaryDirectory() as d:
            rec, stats, _ = run(suit, 2, os.path.join(d, "r.bdf"), imus=False)
            r = bdf.read(os.path.join(d, "r.bdf"))
        self.assertGreater(stats["gaps"], 0)
        self.assertEqual(stats["annotations unwritten"], 0)
        gaps = [a for a in r.annotations if a[2].startswith("gap")]
        self.assertEqual(len(gaps), stats["gaps"])
        labels = [s.label for s in r.signals]
        for onset, duration, text in gaps:
            ch = r.samples[labels.index(f"EMG {text[4:]}-01")]
            a = round(onset * stp.ADS_SPS)
            n = round(duration * stp.ADS_SPS)
            if a > 0:
                self.assertEqual(ch[a:a + n], [ch[a - 1]] * n)      # the last sample held

    def test_the_whole_suit_in_two_files(self):
        suit = Suit.standard(16)
        with tempfile.TemporaryDirectory() as d:
            rec, stats, _ = run(suit, 1, os.path.join(d, "r.bdf"))
            self.assertEqual(stats["files"], 2)
            a, b = bdf.read(os.path.join(d, "r.bdf")), bdf.read(os.path.join(d, "r-2.bdf"))
        self.assertTrue(len(a.signals) <= MAX_SIGNALS and len(b.signals) <= MAX_SIGNALS)
        emg = [s for s in a.signals + b.signals if s.label.startswith("EMG")]
        imu = [s for s in a.signals + b.signals if not s.label.startswith("EMG")]
        self.assertEqual(len(emg), 15 * 16 + 8 + 4 * 8)                # 280 channels
        self.assertEqual(len(imu), 6 * (44 + 2 * 24 + 2 * 8))          # 108 IMUs

    def test_units_asked_for(self):
        suit = Suit.standard(4, line8=False, gloves=False, socks=False)
        number = suit.of(1)[1].number
        with tempfile.TemporaryDirectory() as d:
            run(suit, 1, os.path.join(d, "r.bdf"), units=[number], imus=False)
            r = bdf.read(os.path.join(d, "r.bdf"))
        self.assertEqual({s.label[4:6] for s in r.signals}, {f"{number:02X}"})

    @unittest.skipUnless(__import__("importlib").util.find_spec("pyedflib"), "pyedflib absent")
    def test_read_by_edflib(self):
        import pyedflib
        suit = Suit.standard(2, line8=False, gloves=False, socks=False, bad_frame_rate=0.01)
        with tempfile.TemporaryDirectory() as d:
            _, stats, _ = run(suit, 2, os.path.join(d, "r.bdf"))
            f = pyedflib.EdfReader(os.path.join(d, "r.bdf"))
            self.assertEqual(f.filetype, pyedflib.FILETYPE_BDFPLUS)
            self.assertEqual(f.file_duration, 2)
            self.assertEqual(f.getSampleFrequency(0), stp.ADS_SPS)
            self.assertEqual(len(f.readAnnotations()[0]), stats["gaps"])
            f.close()


if __name__ == "__main__":
    unittest.main()
