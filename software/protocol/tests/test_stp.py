import unittest
from ci import stp
from ci.crc import crc32


class TestControlAndContainers(unittest.TestCase):
    def test_control_frame_round_trip(self):
        cf = stp.ControlFrame(stp.CMD_REPEAT, 3, 0xBEEF, 2)
        b = cf.pack()
        self.assertEqual(len(b), 6)
        self.assertEqual(stp.ControlFrame.unpack(b), cf)
        bad = bytearray(b); bad[2] ^= 1
        with self.assertRaises(ValueError):
            stp.ControlFrame.unpack(bytes(bad))

    def test_message_fits_a_cycle(self):
        cs = [stp.Container(0, stp.T_SOUND_DOWN, i, bytes(52)) for i in range(7)]
        msg = stp.pack_message(stp.ControlFrame(stp.CMD_RUNNING, 0, 1), cs)
        self.assertLessEqual(len(msg), 512)
        cf, back = stp.unpack_message(msg)
        self.assertEqual(cf.count, 7)
        self.assertEqual(back, cs)

    def test_container_limits(self):
        with self.assertRaises(ValueError):
            stp.Container(1, 1, 0, bytes(61)).pack()
        stp.Container(1, 10, 0, bytes(112)).pack(stp.WIRE_DATA_MAX)

    def test_answer(self):
        c = stp.Container(2, stp.T_READ_BACK, 9, b"\x01\x00\x03")
        a = c.answer(0, b"\xd2\xc0\xe8")
        self.assertEqual(a.type, 0x83)
        self.assertEqual(a.seq, 9)
        self.assertEqual(a.data[0], 0)


class TestFrames(unittest.TestCase):
    def test_block_frame_round_trip(self):
        f = stp.BlockFrame(block=3, sample=65535, channels=[-8388608, 8388607, 0, 1, -1, 12345, -12345, 7],
                           loff_statp=0x81, loff_statn=0x02, gpio=0, rotation=b"\x01\x02\x03\x04", imu=b"\x10\x20\x30\x40")
        b = f.pack()
        self.assertEqual(len(b), 40)
        self.assertEqual(stp.BlockFrame.unpack(b), f)
        self.assertEqual(f.position, 31)

    def test_step_assembly(self):
        asm = stp.StepAssembler()
        for s in range(64):
            asm.feed(stp.BlockFrame(1, s, [0] * 8, imu=bytes([s % 32] * 4)))
        self.assertEqual(len(asm.steps), 8)  # 4 IMUs, two steps each
        self.assertEqual(asm.steps[0][2], bytes(range(12)))
        foot = stp.StepAssembler(imus_per_byte=2)
        for s in range(32):
            foot.feed(stp.BlockFrame(1, s, [0] * 8, imu=bytes([s] * 4)))
        self.assertEqual(len(foot.steps), 8)
        self.assertEqual(foot.steps[-1][2], bytes(range(12, 24)))

    def test_natasa_frame(self):
        mics = [(i, -i) for i in range(13)]
        f = stp.NatasaFrame(sample=16, state=0b10, buttons=0x00F0, rotation=bytes(range(8)), mics=mics)
        b = f.pack()
        self.assertEqual(len(b), 68)
        back = stp.NatasaFrame.unpack(b)
        self.assertEqual(back.mics, mics)
        self.assertTrue(back.state & 1)
        self.assertEqual(back.position, 0)
        f12 = stp.NatasaFrame(sample=1, mics=mics[:12])
        self.assertFalse(stp.NatasaFrame.unpack(f12.pack()).state & 1)

    def test_record_half(self):
        frames = [stp.BlockFrame(i + 1, 5, [i] * 8).pack() if i != 2 else None for i in range(8)]
        h = stp.RecordHalf(5, 1, frames, glove=stp.BlockFrame(0x82, 5, [0] * 8).pack(), pending=3, flags=stp.FLAG_MISSING)
        b = h.pack()
        self.assertEqual(len(b), 384)
        back = stp.RecordHalf.unpack(b)
        self.assertEqual(back, h)
        self.assertIsNone(back.frames[2])


class TestChannelsToBata(unittest.TestCase):
    def test_uart(self):
        c = stp.Container(1, stp.T_ADS_WRITE, 1, b"\x01\xd2")
        p = stp.pack_uart(stp.LINE_ALL, c)
        self.assertEqual(p[:2], b"\xa1\xc1")
        line, back, n = stp.unpack_uart(p)
        self.assertEqual((line, back, n), (0xFF, c, len(p)))

    def test_i2c(self):
        c = stp.Container(0x81, stp.T_SPHERE, 7, bytes(112))
        t = stp.pack_i2c(c)
        self.assertEqual(len(t), 128)
        self.assertEqual(stp.unpack_i2c(t), c)
        self.assertIsNone(stp.unpack_i2c(bytes(128)))


class TestFirmware(unittest.TestCase):
    def test_pieces(self):
        image = bytes(range(256)) * 3 + b"\x55" * 7   # 775 B
        pieces = stp.fw_pieces(0, 0, image)
        self.assertEqual(len(pieces), 17)
        self.assertEqual(len(pieces[-1].data), 4 + 16)  # 7 B padded to a word
        rebuilt = b"".join(p.data[4:] for p in pieces)
        self.assertEqual(rebuilt[:len(image)], image)
        self.assertEqual(len(rebuilt) % 16, 0)
        for p in pieces:
            self.assertLessEqual(len(p.pack()), 66)
        begin = stp.fw_begin(0, 0, stp.KIND_BLOCK, 0x0102, image)
        self.assertEqual(len(begin.data), 12)
        self.assertEqual(int.from_bytes(begin.data[8:], "little"), crc32(image))


class TestHead(unittest.TestCase):
    def test_interconnect_sizes(self):
        self.assertEqual(len(stp.ic_call(1, 0).pack()), 6)
        self.assertEqual(len(stp.ic_answer(1, 0, 0x3F, [bytes(12)] * 4).pack()), 55)

    def test_sphere_and_head(self):
        s = stp.sphere(1, 0x0F, -3, 10, [(200, 0, 0x0F)] * 36)
        self.assertEqual(len(s), 112)
        self.assertEqual(len(stp.Container(1, stp.T_SPHERE, 1, s).pack(stp.WIRE_DATA_MAX)), 118)
        self.assertEqual(len(stp.head_define(1, 8, [(5, 10)] * 8).data), 18)
        self.assertEqual(len(stp.head_define(1, 9, [(5, 10)]).data), 5)
