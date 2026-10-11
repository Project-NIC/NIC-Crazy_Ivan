"""The two CRCs of the suit (porjadok/SOFTWARE.md, "The frame" and "Updating firmware")."""
import zlib

_TABLE = []
for _i in range(256):
    _c = _i << 8
    for _ in range(8):
        _c = ((_c << 1) ^ 0x1021) & 0xFFFF if _c & 0x8000 else (_c << 1) & 0xFFFF
    _TABLE.append(_c)


def crc16(data: bytes) -> int:
    """CRC-16/CCITT-FALSE: polynomial 0x1021, initial 0xFFFF, no reflection, no final XOR.

    "123456789" gives 0x29B1. Used on every frame, container, record half and output frame,
    always stored little-endian.
    """
    c = 0xFFFF
    for b in data:
        c = ((c << 8) & 0xFFFF) ^ _TABLE[((c >> 8) ^ b) & 0xFF]
    return c


def crc32(data: bytes) -> int:
    """CRC-32 as zlib computes it (0x04C11DB7 reflected, init and final XOR 0xFFFFFFFF).

    "123456789" gives 0xCBF43926. Used on a firmware image.
    """
    return zlib.crc32(data) & 0xFFFFFFFF
