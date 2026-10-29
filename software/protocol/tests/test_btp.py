import unittest

from ci import btp


class TestFrames(unittest.TestCase):
    def test_classes(self):
        self.assertEqual([btp.data_len(c) for c in (0, 1, 2)], [120, 248, 504])
        for c, n in btp.CLASS_LEN.items():
            b = btp.alive(5, c).pack()
            self.assertEqual(len(b), n)
            self.assertEqual(btp.frame_len(b), n)
            f = btp.Frame.unpack(b)
            self.assertEqual((f.cls, f.kind, f.packets), (c, btp.KIND_ALIVE, []))

    def test_round_trip_and_alignment(self):
        pk = [btp.snapshot(0, bytes(range(127)), 0x80000001), btp.event(1, 2, 3, b"ab"),
              btp.ecg(1000, [bytes(32)] * 4), btp.meta_time(1, 2, 3, 4, 5, 6, 7)]
        f = btp.Frame(123456789, pk)
        b = f.pack()
        self.assertEqual(len(b), 512)
        self.assertEqual(b[4], 0x81)                     # class 512, kind packets
        self.assertEqual(btp.Frame.unpack(b), f)
        self.assertEqual(btp.snapshot(0, bytes(127), 0).size, 136)   # 4 + 131, padded to 8

    def test_bad_crc_and_overflow(self):
        b = bytearray(btp.alive(5).pack()); b[0] ^= 1
        with self.assertRaises(ValueError):
            btp.Frame.unpack(bytes(b))
        with self.assertRaises(ValueError):
            btp.Frame(0, [btp.snapshot(0, bytes(127), 0)], btp.CLASS_128).pack()

    def test_the_snapshot_wants_256(self):
        snap = btp.snapshot(0, bytes(127), 0)
        self.assertEqual(btp.smallest_class([snap]), btp.CLASS_256)
        joints = btp.meta_joints(4, [(1, 1, -10, 70)] * 63, list(range(32)))
        self.assertEqual(btp.smallest_class([joints]), btp.CLASS_512)


class TestMeta(unittest.TestCase):
    def test_suit_and_map(self):
        units = [btp.MapUnit(0x11 + i, 1, i, 4, 0x0100) for i in range(20)] + \
                [btp.MapUnit(0x81, 3, 0, 0, 0x0100), btp.MapUnit(0x82, 4, 0, 1, 0x0100)]
        m = btp.meta_suit(b"CI-0001", 1, 2, 3, 4, 5, btp.RATE_128, 127, 32, 4, units, (1 << 22) - 1)
        self.assertEqual(len(m.data), 163)
        back, present = btp.parse_meta_suit(m.data)
        self.assertEqual((back, present), (units, (1 << 22) - 1))

    def test_place_list(self):
        self.assertEqual(sorted(btp.PLACES), list(range(1, 23)))
        self.assertEqual([btp.place_line(p) for p in (1, 4, 5, 9, 12, 16, 17, 18, 20, 22)],
                         [1, 1, 2, 3, 3, 4, 5, 6, 7, 8])
        with self.assertRaises(ValueError):
            btp.place_line(0)                                         # unknown

    def test_sizes(self):
        self.assertEqual(len(btp.meta_bones(1800, 800, [100] * 16).data), 36)
        self.assertEqual(len(btp.meta_joints(3, [(1, 1, -10, 70)] * 64).data), 256)
        self.assertEqual(len(btp.meta_electrodes(bytes(64), 3, 0xFF, 0).data), 286)
        t = btp.meta_temperatures([250] * 22, [25] * 121, (300, 310, 450), bytes(23), 0x0F, 2100)
        self.assertEqual(len(t.data), 198)
        self.assertEqual(len(btp.meta_fatigue(bytes(280), bytes(64)).data), 344)
        self.assertEqual(btp.smallest_class([btp.meta_fatigue(bytes(280), bytes(64))]), btp.CLASS_512)
        self.assertEqual(btp.smallest_class([btp.meta_electrodes(bytes(280), 1, 1, 0)]), btp.CLASS_512)
        self.assertEqual(len(btp.meta_time(0, 0, 0, 0, 0, 0, 0).data), 24)

    def test_vitals(self):
        self.assertEqual(len(btp.vitals(72, 40, 14, 33, 0x0F).data), 8)


class TestSubscribe(unittest.TestCase):
    def test_round_trip(self):
        b = btp.subscribe(0b11111, btp.RATE_64, btp.CLASS_128)
        self.assertEqual(len(b), 8)
        self.assertEqual(b[:2], b"\xC1\xA1")
        self.assertEqual(btp.unpack_subscribe(b), (0b11111, btp.RATE_64, btp.CLASS_128))

    def test_the_answer_raises_the_class(self):
        largest = {btp.P_SNAPSHOT: 136, btp.P_META: 288, btp.P_EVENT: 16}
        ask = btp.subscribe(1 << btp.P_SNAPSHOT | 1 << btp.P_EVENT, btp.RATE_128, btp.CLASS_128)
        self.assertEqual(btp.unpack_subscribe(btp.answer_subscribe(ask, largest))[2], btp.CLASS_256)
        ask = btp.subscribe(1 << btp.P_META, btp.RATE_128, btp.CLASS_128)
        self.assertEqual(btp.unpack_subscribe(btp.answer_subscribe(ask, largest))[2], btp.CLASS_512)
