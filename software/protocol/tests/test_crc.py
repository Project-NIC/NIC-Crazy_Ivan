import unittest
from ci.crc import crc16, crc32


class TestCRC(unittest.TestCase):
    def test_known_vectors(self):
        self.assertEqual(crc16(b"123456789"), 0x29B1)
        self.assertEqual(crc32(b"123456789"), 0xCBF43926)

    def test_empty(self):
        self.assertEqual(crc16(b""), 0xFFFF)
