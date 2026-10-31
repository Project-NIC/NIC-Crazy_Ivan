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
        self.assertEqual(len(suit.units), 22)                  # 16, 2 gloves, 2 socks, line 8's two
        self.assertEqual((len(suit.of(1)), len(suit.of(2))), (16, 6))
        self.assertEqual([u.slot for u in suit.of(1) if u.line == 3], [1, 2, 3, 4])
        self.assertEqual((suit.unit("glove L").slot, suit.unit("sock R").slot), (4, 4))
        self.assertEqual([u.number for u in suit.of(2)][-2:], [0x81, 0x82])
        self.assertEqual(sum(u.imus for u in suit.units if u.line < 8), 42 + 40 + 16)
        self.assertEqual(sum(u.imus for u in Suit.standard(16, gloves=False, socks=False).units
                             if u.line < 8), 42)
        self.assertEqual(sum(u.place for u in suit.of(1)), 16 * 58)          # the places of data
        self.assertEqual(sum(u.place for u in suit.of(2)), 3 * 58 + 2 * 34)   # the neck's and Nataša's 34

    def test_line8_data_half_a_round_from_the_diagnostics(self):
        suit = Suit.standard(16)
        u = suit.unit("Nataša")                                       # 34 + 34 + 198 > 256
        self.assertIsNotNone(u.frames(15, 0.0, [])[0])
        self.assertIsNone(u.frames(31, 0.0, [])[0])
        self.assertNotIn(suit.unit("Míša"), suit.placed(2))           # no frame of data
        self.assertEqual(len(suit.placed(2)), 5)
        self.assertEqual(len(suit.unit("head").frames(0, 0.0, [])[0]), 58)    # two ADS1298
        self.assertEqual(len(suit.unit("neck and upper back").frames(0, 0.0, [])[0]), 34)  # one
        self.assertEqual(len(suit.unit("thigh L").frames(0, 0.0, [])[0]), 58) # two ADS1298
        g = suit.unit("glove L").frames(0, 0.0, suit.steps)[0]
        self.assertEqual((len(g), g[1]), (58, stp.K_END))                     # an ADS1298 and steps
        self.assertEqual((suit.unit("glove L").chips, suit.unit("sock R").chips), (25, 11))

    def test_a_quarter_second(self):
        suit = Suit.standard(16)
        left = []

        def before_diagnostics(i, suit):
            if i % 32 == 31:
                left.append(len(suit.queue[1]) + len(suit.queue[2]))
        bata = run(suit, 960, before_diagnostics)
        self.assertEqual((len(suit.p1[0]), len(suit.p2[0][0]), len(suit.p2[0][1])),
                         (1064, 192, 192))
        self.assertEqual((bata.cycles, bata.lost, bata.empty, bata.out_of_step), (960, 0, 0, 0))
        self.assertEqual(bata.steps, 60 * 98)                          # every IMU, every step
        self.assertEqual(len(bata.diagnostics), 22)                    # every unit's came
        out = summarize(btp.Frame.unpack(f) for f in bata.frames_out)
        self.assertEqual(out["packets"][btp.P_SNAPSHOT], 60)           # 960 / 16
        self.assertEqual(out["packets"][btp.P_ECG], 60)
        self.assertEqual(out["packets"][btp.P_SPHERE], 5)              # ten a second
        self.assertEqual(set(left), {0})                               # the four places keep up

    def test_bad_frames_leave_gaps(self):
        suit = Suit.standard(16, bad_frame_rate=0.02)
        bata = run(suit, 400)
        self.assertGreater(suit.stats["bad"], 0)
        self.assertGreater(bata.empty, 0)
        self.assertLessEqual(bata.empty, suit.stats["bad"])            # no repeat for data
        self.assertEqual((bata.lost, bata.out_of_step), (0, 0))
        self.assertLess(bata.steps, 25 * 98)

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
        suit = Suit.standard(4, line8=False, gloves=False, socks=False)
        self.assertEqual(len(suit.of(2)), 0)
        bata = run(suit, 64)
        self.assertEqual(len(suit.p1[0]), 4 * 58 + stp.EXTRA * 34)    # a place of 58 B a module
        self.assertEqual(bata.cycles, 64)
