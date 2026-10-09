import unittest
from ci import btp


class TestFrames(unittest.TestCase):
    def test_round_trip_and_alignment(self):
        pk = [btp.snapshot(0, bytes(range(127)), 0x80000001), btp.event(1, 2, 3, b"ab"),
              btp.ecg(1000, [bytes(32)] * 4), btp.meta_time(1, 2, 3, 4, 5, 6, 7)]
        f = btp.Frame(123456789, pk)
        b = f.pack()
        self.assertEqual(len(b), 512)
        back = btp.Frame.unpack(b)
        self.assertEqual(back, f)
        self.assertEqual(len(btp.snapshot(0, bytes(127), 0).pack()), 136)  # 4 + 131, padded to 8

    def test_idle_and_bad_crc(self):
        b = btp.idle(5).pack()
        self.assertEqual(btp.Frame.unpack(b).type, btp.FRAME_IDLE)
        bad = bytearray(b); bad[0] ^= 1
        with self.assertRaises(ValueError):
            btp.Frame.unpack(bytes(bad))

    def test_overflow(self):
        with self.assertRaises(ValueError):
            btp.Frame(0, [btp.snapshot(0, bytes(127), 0)] * 4).pack()

    def test_meta_sizes(self):
        self.assertEqual(len(btp.meta_suit(b"CI-0001", 1, 2, 3, (4, 5, 6, 7), 0xFFFF, [1] * 16, 1, 127, 32, 8).data), 64)
        self.assertEqual(len(btp.meta_bones(1800, 800, [100] * 16).data), 36)
        self.assertEqual(len(btp.meta_joints(3, [(1, 1, -10, 70)] * 64).data), 256)
        self.assertEqual(len(btp.meta_joints(4, [(1, 1, -10, 70)] * 63, list(range(32))).data), 284)
        for sub, n in btp.META_LEN.items():
            self.assertLessEqual(len(btp.meta(sub, bytes(n)).pack()), 504)

    def test_vitals(self):
        self.assertEqual(len(btp.vitals(72, 40, 14, 33, 0x0F).data), 8)

    def test_subscribe(self):
        b = btp.subscribe(0b11111, btp.RATE_64)
        self.assertEqual(len(b), 8)
        self.assertEqual(btp.unpack_subscribe(b), (0b11111, btp.RATE_64))

    def test_meta_5_6_7(self):
        self.assertEqual(len(btp.meta_electrodes(bytes(128), 3).data), 132)
        t = btp.meta_temperatures([250] * 16, [25] * 64, (300, 310, 450), (3100, 3100, 3100, 3100),
                                  12400, -1500, (250, 260, 270), 0, 55, 6600, 0x0F, 2100)
        self.assertEqual(len(t.data), 132)
        self.assertEqual(len(btp.meta_fatigue(bytes(128), bytes(64)).data), 192)
