import unittest
import random

from ci.crc import crc16, crc16_table, crc32


class TestCRC(unittest.TestCase):
    def test_known_vectors(self):
        self.assertEqual(crc16(b"123456789"), 0x29B1)
        self.assertEqual(crc32(b"123456789"), 0xCBF43926)

    def test_empty(self):
        self.assertEqual(crc16(b""), 0xFFFF)

    def test_the_table_agrees(self):
        rng = random.Random(5)
        for n in (0, 1, 6, 32, 56, 196, 517):
            data = bytes(rng.getrandbits(8) for _ in range(n))
            self.assertEqual(crc16(data), crc16_table(data))
