import unittest

from suitsim import Suit, Bata, summarize
from ci import btp, stp


def run(suit: Suit, cycles: int, at=None) -> Bata:
    bata = Bata({1: suit.of(1), 2: suit.of(2)})
    for i in range(cycles):
        if at:
            at(i, suit)
        t1, share = suit.cycle()
        bata.transfer1(t1)
        bata.transfer2(*share)
    bata.close()
    return bata


class TestSimulator(unittest.TestCase):
    def test_the_map(self):
        suit = Suit.standard(16)
        self.assertEqual(len(suit.units), 20)                          # 16, 2 gloves, line 8's two
        self.assertEqual((len(suit.of(1)), len(suit.of(2))), (14, 6))
        self.assertEqual([u.slot for u in suit.of(1) if u.line == 1], [1, 2, 3, 4])
        self.assertEqual(suit.unit("glove L").slot, 4)
        self.assertEqual([u.number for u in suit.of(2)][-2:], [0x81, 0x82])
        self.assertEqual(sum(u.imus for u in suit.units if u.line < 8), 44 + 40)
        self.assertEqual(sum(u.imus for u in Suit.standard(16, gloves=False).units
                             if u.line < 8), 48)

    def test_line8_data_half_a_round_from_the_diagnostics(self):
        suit = Suit.standard(16)
        for name in ("Nataša", "Míša"):                                # 34 + 34 + 198 > 256
            u = suit.unit(name)
            self.assertIsNotNone(u.frame(15, 0.0, []))
            self.assertIsNone(u.frame(31, 0.0, []))

    def test_a_quarter_second(self):
        suit = Suit.standard(16)
        left = []

        def before_diagnostics(i, suit):
            if i % 32 == 31:
                left.append(len(suit.queue[1]) + len(suit.queue[2]))
        bata = run(suit, 960, before_diagnostics)
        self.assertEqual((len(suit.p1[0]), len(suit.p2[0][0]), len(suit.p2[0][1])),
                         (612, 172, 172))
        self.assertEqual((bata.cycles, bata.lost, bata.empty, bata.out_of_step), (960, 0, 0, 0))
        self.assertEqual(bata.steps, 30 * 84)                          # every IMU, every step
        self.assertEqual(len(bata.diagnostics), 20)                    # every unit's came
        out = summarize(btp.Frame.unpack(f) for f in bata.frames_out)
        self.assertEqual(out["packets"][btp.P_SNAPSHOT], 30)           # 960 / 32
        self.assertEqual(out["packets"][btp.P_ECG], 30)
        self.assertEqual(out["packets"][btp.P_SPHERE], 3)              # ten a second
        self.assertEqual(set(left), {0})                               # the four places keep up

    def test_bad_frames_leave_gaps(self):
        suit = Suit.standard(16, bad_frame_rate=0.02)
        bata = run(suit, 400)
        self.assertGreater(suit.stats["bad"], 0)
        self.assertGreater(bata.empty, 0)
        self.assertLessEqual(bata.empty, suit.stats["bad"])            # no repeat for data
        self.assertEqual((bata.lost, bata.out_of_step), (0, 0))
        self.assertLess(bata.steps, 13 * 84)

    def test_buttons_make_events(self):
        def press(i, suit):
            if i == 10:
                suit.unit("Nataša").buttons = 0x0001
            if i == 100:
                suit.unit("Nataša").buttons = 0
        bata = run(Suit.standard(8), 200, press)
        out = summarize(btp.Frame.unpack(f) for f in bata.frames_out)
        self.assertEqual(out["packets"][btp.P_EVENT], 2)

    def test_a_small_suit(self):
        suit = Suit.standard(4, line8=False, gloves=False)
        self.assertEqual(len(suit.of(2)), 0)
        bata = run(suit, 64)
        self.assertEqual(len(suit.p1[0]), (4 + stp.EXTRA) * 34)
        self.assertEqual(bata.cycles, 64)
