import struct
import unittest

from ci import stp
from ci.crc import crc16, crc32


class TestFrames(unittest.TestCase):
    def test_every_kind_has_one_length(self):
        self.assertEqual(set(stp.LENGTH.values()), {8, 34, 198, 519})
        for kind, n in stp.LENGTH.items():
            if n in (8, 34, 198):
                self.assertEqual(len(stp.Frame(1, kind).pack()), n)

    def test_round_trip_and_errors(self):
        f = stp.Frame(0x12, stp.K_DATA, 0xBEEF, bytes(range(28)))
        b = f.pack()
        self.assertEqual(b[:4], bytes([0x12, 0x20, 0xEF, 0xBE]))     # the number little-endian
        self.assertEqual(struct.unpack("<H", b[32:])[0], crc16(b[:32]))
        self.assertEqual(stp.Frame.unpack(b), f)
        bad = bytearray(b); bad[10] ^= 1
        with self.assertRaises(ValueError):
            stp.Frame.unpack(bytes(bad))
        with self.assertRaises(ValueError):                          # a byte too many
            stp.check(b + b"\0")
        with self.assertRaises(ValueError):                          # 28 B at most
            stp.Frame(1, stp.K_DATA, 0, bytes(29)).pack()
        short = stp.Frame(3, stp.K_GET_READY, 7).pack()
        self.assertEqual(short[:6], bytes([3, 0x10, 7, 0, 0, 0]))

    def test_widen(self):
        self.assertEqual(stp.widen(70000, 70000 & 0xFFFF), 70000)
        self.assertEqual(stp.widen(70000, (70000 - 5) & 0xFFFF), 69995)
        self.assertEqual(stp.widen(65535, 2), 65538)                 # past the wrap


class TestCommands(unittest.TestCase):
    def test_read_and_its_answer(self):
        q = stp.read(0x11, stp.CHIP_ADS, 0x01, 3, number=9)
        self.assertEqual(q, stp.Frame(0x11, 0x03, 9, bytes([1, 1, 3])).pack())
        a = stp.read_answer(stp.Frame.unpack(q), b"\xd2\xc0\xe8")
        self.assertEqual(len(a), 34)
        r = stp.Registers.unpack(a)
        self.assertEqual((r.unit, r.kind, r.number, r.chip, r.reg, r.values),
                         (0x11, 0x83, 9, 1, 1, b"\xd2\xc0\xe8"))
        with self.assertRaises(ValueError):
            stp.read(1, 1, 0, 26)

    def test_writes_and_results(self):
        one = stp.write(0x11, stp.CHIP_UNIT, stp.REG_BIAS, 1, number=4)
        self.assertEqual(len(one), 8)
        many = stp.write_many(0, stp.CHIP_ADS, 0x01, bytes(23), number=5)   # 01h-17h in one frame
        r = stp.Registers.unpack(many)
        self.assertEqual((r.kind, r.chip, r.reg, len(r.values)), (0x06, 1, 1, 23))
        ans = stp.result(stp.Frame.unpack(many), stp.NO_CHIP, unit=0x11)
        self.assertEqual(stp.Frame.unpack(ans), stp.Frame(0x11, 0x86, 5, bytes([2, 0, 0])))
        with self.assertRaises(ValueError):
            stp.write_many(1, 1, 0, bytes(26))

    def test_direct_and_the_short_ones(self):
        d = stp.Frame.unpack(stp.direct(0x11, stp.CHIP_ADS, b"\x11\x41\x00\xd2"))
        self.assertEqual(d.body[:6], bytes([1, 4, 0x11, 0x41, 0x00, 0xD2]))
        self.assertEqual(stp.short_value(stp.start(1000)), 1000)
        self.assertEqual(stp.short_value(stp.stop(70000)), 70000 & 0xFFFF)
        self.assertEqual(stp.short_value(stp.heartbeat(5)), 5)
        self.assertEqual(stp.short_value(stp.repeat(stp.NATASA, 300)), 300)
        self.assertEqual(stp.Frame.unpack(stp.mamka(4)).kind, 0x15)

    def test_discover_and_assign(self):
        uid = bytes(range(12))
        a = stp.Frame.unpack(stp.discover_answer(uid))
        self.assertEqual((a.unit, a.kind, a.body[:12], a.body[12:]), (0, 0x81, uid, bytes(16)))
        frame = stp.assign(uid, 0x12)
        self.assertEqual(frame[0], 0)
        self.assertEqual(stp.parse_assign(frame), (uid, 0x12))
        done = stp.Frame.unpack(stp.result(stp.Frame.unpack(frame), unit=0x12))
        self.assertEqual((done.unit, done.kind, done.body[0]), (0x12, 0x82, 0))
        with self.assertRaises(ValueError):
            stp.assign(uid, 0x81)                                     # Nataša's is fixed
        self.assertLess(stp.wait_us(uid), 655_360)
        self.assertNotEqual(stp.wait_us(uid), stp.wait_us(uid, 1))

    def test_bus_test(self):
        for n in (0, 1, 18, 300, 65535):
            b = stp.bus_test(0x11, n)
            self.assertEqual(struct.unpack_from("<H", b, 2)[0], n)
            self.assertEqual(stp.bus_errors(b), 0)
        seq = stp.prbs9(1022)
        self.assertEqual(stp.pattern(1), bytes(seq[28:56]))           # running on from frame 0
        bad = bytearray(stp.bus_test(0x11, 7)); bad[10] ^= 0x81
        bad[32:34] = struct.pack("<H", crc16(bytes(bad[:32])))
        self.assertEqual(stp.bus_errors(bytes(bad)), 2)

    def test_prbs9(self):
        s = stp.prbs9(1022)
        self.assertEqual(s[:511], s[511:])                            # the period, 511
        self.assertEqual(s[:4].hex(), "07be2e64")                     # x^9 + x^5 + 1 from all ones


class TestData(unittest.TestCase):
    def test_module_frame(self):
        ch = [-8388608, 8388607, 0, 1, -1, 12345, -12345, 7]
        b = stp.module_data(0x05, 0x1FF, ch, b"\x10\x20\x30\x40")
        self.assertEqual(len(b), 34)
        self.assertEqual(b[4:7], b"\x80\x00\x00")                     # most significant first
        self.assertEqual(stp.parse_module_data(b), (5, 0x1FF, ch, b"\x10\x20\x30\x40"))

    def test_steps_of_a_module_and_the_glove(self):
        own = [bytes([i] * 12) for i in range(4)]
        self.assertEqual(stp.frames_for(4, stp.MODULE_IMU), 12)       # frames 0-11 of the 32
        self.assertEqual(stp.frames_for(20, stp.GLOVE_IMU), 9)        # frames 0-8
        self.assertEqual(stp.imu_bytes(3, own, 4), bytes([1] * 4))    # bytes 12-15: the second
        self.assertEqual(stp.imu_bytes(12, own, 4), bytes(4))         # zeros after them
        asm = stp.StepAssembler(4, 4)
        for c in range(64, 96):
            asm.feed(c, stp.imu_bytes(c, own, 4))
        self.assertEqual(asm.steps, [(2, i, own[i]) for i in range(4)])
        glove = [bytes([i] * 12) for i in range(20)]
        asm = stp.StepAssembler(20, 28)
        for c in range(32):
            if c != 4:                                                # one frame lost
                asm.feed(c, stp.imu_bytes(c, glove, 28))
        lost = [9, 10, 11]                                            # bytes 112-139 in frame 4
        self.assertEqual([i for _, i, _ in asm.steps], [i for i in range(20) if i not in lost])
        with self.assertRaises(ValueError):
            stp.imu_bytes(0, own * 3, 4)                               # 144 B in 128

    def test_natasa(self):
        b = stp.natasa_data(31, 0x00F0, stp.NATASA_MISA)
        self.assertEqual(b[:7], bytes([0x81, 0x20, 31, 0, 0xF0, 0, 1]))
        self.assertEqual(stp.parse_natasa_data(b), (31, 0xF0, 1))


class TestDiagnostics(unittest.TestCase):
    def test_round_trip(self):
        d = stp.Diagnostics(7, 31, 0xFFFFFFFE, 0xFFFFFFFF, 0xFB, 0xFF, 0xFE, -5, 3270,
                            [132, -265, 0, 1, 2, 3])
        b = d.pack()
        self.assertEqual(b[4:17], bytes.fromhex("feffffffffffffff fb ff fe fb 7f".replace(" ", "")))
        self.assertEqual(b[17:19], b"\x00\x84")                       # TEMP_DATA as the chip gives
        self.assertEqual(b[29:32], bytes(3))
        self.assertEqual(stp.Diagnostics.unpack(b), d)
        self.assertFalse(d.all_well)
        self.assertTrue(stp.Diagnostics(7, 31).all_well)
        self.assertAlmostEqual(stp.temp_c(132), 26.0, places=2)

    def test_by_turns_and_bits(self):
        seen = set()
        for k in range(4):                                            # the glove's 20 in four
            seen |= set(stp.which_imus(31 + 32 * k, 20))
        self.assertEqual(seen, set(range(20)))
        self.assertEqual(list(stp.which_imus(31, 4)), [0, 1, 2, 3])
        self.assertEqual(stp.chip_bits(5, [True, True, False, True, True]), 0xFFFFFFFB)
        self.assertEqual(stp.on_skin([0x00, 0x04, 0x00]), 0xFB)
        self.assertEqual(stp.mv_byte(3300), 130)


class TestTable(unittest.TestCase):
    def test_sizes(self):
        m = stp.module_table(bytes(range(12)))
        b = m.pack()
        self.assertEqual((len(b), b[0]), (28, 28))
        self.assertEqual(stp.UnitTable.unpack(b), m)
        self.assertEqual(m.reads(), [(0x40, 25), (0x59, 3)])          # two reads
        g = stp.glove_table(bytes(12))
        self.assertEqual(len(g.pack()), 58)
        self.assertEqual(len(g.reads()), 3)
        self.assertEqual(g.chips[-1][0], 0x23)
        with self.assertRaises(ValueError):
            stp.glove_table(bytes(12), 21)


class TestSpis(unittest.TestCase):
    def test_places(self):
        data = [stp.module_data(i, 9, [i] * 8, bytes(4)) for i in range(1, 15)]
        data[3] = None                                                # a frame dropped by its CRC
        extra = [stp.result(stp.Frame.unpack(stp.get_ready(2)))]      # 8 B in a place
        t = stp.cycle_transfer(data, extra)
        self.assertEqual(len(t), 612)                                 # 18 × 34
        got, ex = stp.parse_cycle(t, 14)
        self.assertEqual(got, data)
        self.assertEqual(ex, extra)
        self.assertEqual(t[3 * 34:4 * 34], bytes(34))
        with self.assertRaises(ValueError):
            stp.cycle_transfer(data, extra * 5)

    def test_stripe(self):
        t = stp.cycle_transfer([stp.module_data(i, 0, [0] * 8, bytes(4)) for i in range(6)])
        self.assertEqual(len(t), 340)
        a, b = stp.stripe(t)
        self.assertEqual((len(a), len(b)), (172, 172))                # 85 words padded to 86
        self.assertEqual(a[4:8], t[8:12])
        self.assertEqual(stp.join(a, b)[:340], t)
        self.assertEqual(stp.parse_cycle(stp.join(a, b), 6)[0], stp.parse_cycle(t, 6)[0])

    def test_firmware_takes_sixteen_places(self):
        fw = stp.fw_frames(stp.FW_MODULE, bytes(600))
        t = stp.places(fw + [stp.heartbeat(1)])
        self.assertEqual(len(t), 2 * 16 * 34 + 34)
        self.assertEqual(stp.parse_places(t), fw + [stp.heartbeat(1)])


class TestFirmware(unittest.TestCase):
    def test_blocks(self):
        image = stp.image_with_crc(bytes(range(256)) * 4 + b"\x55" * 7)   # 1,035 B
        self.assertEqual(struct.unpack("<I", image[-4:])[0], crc32(image[:-4]))
        frames = stp.fw_frames(stp.FW_BRATISKA, image)
        self.assertEqual([len(f) for f in frames], [519] * 3)
        f = stp.FirmwareFrame.unpack(frames[2])
        self.assertEqual((f.unit, f.firmware, f.block), (0, 3, 2))
        self.assertEqual(f.data[:11], image[1024:])
        self.assertEqual(f.data[11:16], b"\xFF" * 5)                   # to 16 B for the flash
        self.assertEqual(f.data[16:], bytes(496))
        self.assertEqual(len(stp.fw_frames(1, bytes(131072))), 256)
        with self.assertRaises(ValueError):
            stp.fw_frames(1, bytes(131073))

    def test_begin_and_map(self):
        r = stp.Registers.unpack(stp.fw_begin(stp.FW_NATASA, bytes(131072), 0x0203))
        self.assertEqual((r.unit, r.chip, r.reg), (0, 0, 0x80))
        self.assertEqual(r.values, struct.pack("<BBIH", 1, 4, 131072, 0x0203))
        m = bytearray(b"\xFF" * 32); m[1] = 0b11110111
        self.assertEqual(stp.missing(bytes(m), 256), [11])


class TestLine8(unittest.TestCase):
    def test_sound(self):
        samples = [(i, -i) for i in range(48)]
        down = stp.sound(stp.K_SOUND_DOWN, 0x1234, samples)
        self.assertEqual(len(down), 198)
        self.assertEqual(down[:6], bytes([0x81, 0x22, 0x34, 0x12, 0, 0]))
        self.assertEqual(stp.parse_sound(down), (0x22, 0x1234, samples))
        self.assertEqual(stp.sound(stp.K_SOUND_UP, 5, samples)[1], 0x23)

    def test_sphere(self):
        sph = stp.sphere(1, 0x0F, -3, 10, [(200, -4, 0x9F)] * 36)
        self.assertEqual(sph[4:7], bytes([200, 0xFC, 0x9F]))
        pieces = stp.sphere_answers(sph, 4000)
        regs = [stp.Registers.unpack(p) for p in pieces]
        self.assertEqual([(r.chip, r.reg, len(r.values)) for r in regs],
                         [(5, 0, 25), (5, 25, 25), (5, 50, 25), (5, 75, 25), (5, 100, 12)])
        asm = stp.SphereAssembler()
        for p in reversed(pieces):
            asm.feed(p)
        self.assertEqual(asm.spheres, [(4000, sph)])

    def test_motors(self):
        r = stp.Registers.unpack(stp.motors({stp.MOTOR_LEFT: (5, 80, 0, 0),
                                             stp.MOTOR_NAPE: (1, 50, 2, 0)}))
        self.assertEqual((r.chip, r.reg, len(r.values)), (3, 0, 16))
        self.assertEqual(r.values[12:16], bytes([1, 50, 2, 0]))
        self.assertEqual(stp.Frame.unpack(stp.pulse(stp.MOTOR_FOREHEAD, 5)).body, bytes([3, 11, 5]))
        p = stp.Registers.unpack(stp.pattern_define(9, [5, 10]))
        self.assertEqual((p.reg, p.values), (0x28, bytes([5, 10, 0])))
        self.assertEqual(len(stp.Registers.unpack(stp.pattern_define(15, [1] * 8)).values), 8)
        with self.assertRaises(ValueError):
            stp.pattern_define(9, [1] * 9)


class TestMamka(unittest.TestCase):
    def test_event_gps_utc_battery(self):
        e = stp.Registers.unpack(stp.event(stp.EV_PRESSED, 3, 123456))
        self.assertEqual((e.unit, e.kind, e.number, e.reg), (0xF2, 0x83, 123456 & 0xFFFF, 0xC0))
        self.assertEqual(e.values, struct.pack("<BBI", 1, 3, 123456))
        self.assertEqual(len(stp.Registers.unpack(stp.gps(1, 2, 3, 4, 5, 0)).values), 12)
        self.assertEqual(stp.Registers.unpack(stp.utc(9, 10, )).reg, 0xE0)
        self.assertEqual(stp.Frame.unpack(stp.power(3)).body, bytes([0, 0x10, 3]))
        bat = stp.Battery((3300, 3301, 3302, 3303), 13206, -1500, (250, 260, 270), 0, 55, 6600)
        self.assertEqual(stp.BATTERY_LEN, 23)
        self.assertEqual(stp.Battery.unpack(bat.pack()), bat)
