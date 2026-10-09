import unittest
from suitsim import Suit, Bata, summarize
from ci import btp, stp


class TestSimulator(unittest.TestCase):
    def test_a_quarter_second(self):
        suit = Suit.standard(16)
        bata = Bata()
        for _ in range(960):
            bata.record(suit.cycle(), suit.natasa_frame())
        bata.close()
        self.assertEqual(len(suit.records), 960)
        self.assertEqual(bata.gaps, 0)
        out = summarize(btp.Frame.unpack(f) for f in bata.frames_out)
        self.assertEqual(out["packets"][btp.P_SNAPSHOT], 30)          # 960 / 32
        self.assertGreaterEqual(out["packets"][btp.P_ECG], 29)
        raw = summarize(btp.Frame.unpack(f) for f in bata.raw_out)
        self.assertEqual(raw["packets"][16], 1920)                     # two halves a cycle
        self.assertEqual(raw["packets"][17], 960)
        self.assertEqual(raw["packets"][btp.P_META], 8)                # a recording starts with the set
        for f in bata.raw_out:
            btp.Frame.unpack(f)

    def test_records_are_whole(self):
        suit = Suit.standard(8)
        rec = suit.cycle()
        h0 = stp.RecordHalf.unpack(rec[:384]); h1 = stp.RecordHalf.unpack(rec[384:])
        self.assertEqual((h0.half, h1.half), (0, 1))
        self.assertEqual(sum(1 for f in h0.frames + h1.frames if f), 8)
        self.assertIsNotNone(h0.glove)   # line 1, slot 2 wears a glove
        for f in h0.frames:
            if f:
                stp.BlockFrame.unpack(f)

    def test_bad_frames_are_repeated(self):
        suit = Suit.standard(16, bad_frame_rate=0.02)
        bata = Bata()
        for _ in range(400):
            bata.record(suit.cycle(), suit.natasa_frame())
        self.assertGreater(suit.stats["bad"], 0)
        self.assertEqual(suit.stats["repeated"] + suit.stats["missing"] + len(suit.pending_repeat), suit.stats["bad"])
        self.assertEqual(suit.stats["missing"], 0)
        waited = sum(1 for r in suit.records[:-1] if stp.RecordHalf.unpack(r[:384]).flags & stp.FLAG_WAITED)
        self.assertEqual(waited, 0)      # every wait was filled by its repeat

    def test_buttons_make_events(self):
        suit = Suit.standard(8)
        bata = Bata()
        for i in range(70):
            if i == 10:
                suit.natasa.buttons = 0x0001
            if i == 40:
                suit.natasa.buttons = 0
            bata.record(suit.cycle(), suit.natasa_frame())
        bata.close()
        out = summarize(btp.Frame.unpack(f) for f in bata.frames_out)
        self.assertEqual(out["packets"][btp.P_EVENT], 2)
