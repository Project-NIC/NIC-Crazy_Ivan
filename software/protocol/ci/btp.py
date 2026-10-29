"""CI-BTP: Baťa's output frames in three classes and their packets (porjadok/SOFTWARE.md, "Output")."""
from __future__ import annotations

import struct
from dataclasses import dataclass

from .crc import crc16

CLASS_128, CLASS_256, CLASS_512 = 0, 1, 2
CLASS_LEN = {CLASS_128: 128, CLASS_256: 256, CLASS_512: 512}
HEADER_LEN, CRC_LEN = 6, 2
KIND_ALIVE, KIND_PACKETS = 0, 1

P_SNAPSHOT, P_META, P_ECG, P_SPHERE, P_EVENT, P_VITALS = 1, 2, 3, 4, 5, 6
SNAPSHOT_LEN = 127 + 4       # the joints' bytes and the contacts' 32 bits
META_FIXED = {2: 36, 3: 256, 4: 284, 5: 286, 7: 344, 8: 24}   # 1 and 6 grow with the map
CHANNELS, IMUS = 280, 121     # the suit's EMG channels at most (15 × 16 + 8 + 4 × 8), and
                              # its IMU places in meta 6: 64, the gloves' 40, the socks' 16, Míša's
UNITS = 22                    # units in the map at most: 20 on lines 1-7, Nataša, Míša

SUBSCRIBE_MARK = b"\xC1\xA1"   # C1 first
RATE_32, RATE_64, RATE_128, RATE_256 = 0, 1, 2, 3
RATE_FPS = {RATE_32: 32, RATE_64: 64, RATE_128: 128, RATE_256: 256}


def data_len(cls: int) -> int:
    """120, 248 or 504 B: the class less the header and the CRC."""
    return CLASS_LEN[cls] - HEADER_LEN - CRC_LEN


@dataclass
class Packet:
    type: int
    sub: int
    data: bytes

    def pack(self) -> bytes:
        """The 4 B header and the data, padded so that the next packet starts on an 8 B boundary."""
        body = struct.pack("<BBH", self.type, self.sub, len(self.data)) + self.data
        return body + bytes((-len(body)) % 8)

    @property
    def size(self) -> int:
        return len(self.pack())


def smallest_class(packets: list[Packet]) -> int:
    """The class that holds the largest of these packets: a packet never splits."""
    need = max((p.size for p in packets), default=0)
    for cls in (CLASS_128, CLASS_256, CLASS_512):
        if need <= data_len(cls):
            return cls
    raise ValueError("a packet larger than the largest class")


@dataclass
class Frame:
    sample: int
    packets: list[Packet]
    cls: int = CLASS_512
    kind: int = KIND_PACKETS

    def pack(self) -> bytes:
        area = b"".join(p.pack() for p in self.packets)
        room = data_len(self.cls)
        if len(area) > room:
            raise ValueError(f"the packets do not fit the {room} B")
        head = struct.pack("<IBB", self.sample & 0xFFFFFFFF, self.cls << 6 | self.kind, len(self.packets))
        body = head + area + bytes(room - len(area))
        return body + struct.pack("<H", crc16(body))

    @classmethod
    def unpack(cls, b: bytes) -> "Frame":
        if len(b) < HEADER_LEN:
            raise ValueError("too short for a frame")
        sample, ck, count = struct.unpack_from("<IBB", b)
        c, kind = ck >> 6, ck & 0x3F
        if c not in CLASS_LEN or len(b) != CLASS_LEN[c]:
            raise ValueError("the length is not the class's")
        if struct.unpack_from("<H", b, len(b) - CRC_LEN)[0] != crc16(b[:-CRC_LEN]):
            raise ValueError("bad CRC")
        packets, pos, end = [], HEADER_LEN, len(b) - CRC_LEN
        for _ in range(count):
            t, s, ln = struct.unpack_from("<BBH", b, pos)
            if pos + 4 + ln > end:
                raise ValueError("a packet runs past the data")
            packets.append(Packet(t, s, bytes(b[pos + 4:pos + 4 + ln])))
            pos += (4 + ln + 7) // 8 * 8
        return cls(sample, packets, c, kind)


def frame_len(first_bytes: bytes) -> int:
    """A frame's length from its byte 4, so a stream, or a file it was captured to, can be walked."""
    return CLASS_LEN[first_bytes[4] >> 6]


def alive(sample: int, cls: int = CLASS_128) -> Frame:
    return Frame(sample, [], cls, KIND_ALIVE)


def snapshot(sub: int, joints: bytes, contacts: int) -> Packet:
    if len(joints) != 127:
        raise ValueError("127 joint values")
    return Packet(P_SNAPSHOT, sub, joints + struct.pack("<I", contacts))


def ecg(first_sample: int, channels: list[bytes], decimation: int = 1) -> Packet:
    """1 B a sample a channel: the first sample's number (u16), the count, the channel count."""
    n = len(channels[0])
    if any(len(c) != n for c in channels) or n > 255:
        raise ValueError("equal counts up to 255")
    data = struct.pack("<HBB", first_sample & 0xFFFF, n, len(channels)) + b"".join(channels)
    return Packet(P_ECG, decimation, data)


def sphere(data: bytes) -> Packet:
    if len(data) != 112:
        raise ValueError("a sphere is 112 B")
    return Packet(P_SPHERE, 0, data)


def event(counter: int, what: int, which: int, detail: bytes = b"") -> Packet:
    return Packet(P_EVENT, 0, bytes([counter & 0xFF, what, which]) + detail.ljust(5, b"\0")[:5])


def vitals(heart_bpm: int, rmssd_ms: int, breaths: int, skin_c: int, quality: int) -> Packet:
    """8 B once a second: the heart rate, its variability, the breathing rate, the skin temperature."""
    return Packet(P_VITALS, 0, struct.pack("<BBBbB3x", heart_bpm, rmssd_ms, breaths, skin_c, quality))


# --- the meta packets -----------------------------------------------------------------------------

def meta(sub: int, data: bytes) -> Packet:
    if sub in META_FIXED and META_FIXED[sub] != len(data):
        raise ValueError(f"meta {sub} is {META_FIXED[sub]} B")
    return Packet(P_META, sub, data)


# The place list (bata/SOFTWARE.md, the map), by line; 0 an unknown place.
PLACES = {
    1: "left shoulder", 2: "left upper arm", 3: "left forearm", 4: "left hand",
    5: "right shoulder", 6: "right upper arm", 7: "right forearm", 8: "right hand",
    9: "left hip", 10: "left thigh", 11: "left calf", 12: "left foot",
    13: "right hip", 14: "right thigh", 15: "right calf", 16: "right foot",
    17: "head", 18: "chest and abdomen", 19: "neck and upper back", 20: "lower back",
    21: "Nataša", 22: "Míša",
}
PLACE_LINES = (range(1, 5), range(5, 9), range(9, 13), range(13, 17), range(17, 18),
               range(18, 19), range(19, 21), range(21, 23))


def place_line(place: int) -> int:
    """The line, 1-8, a place is on; ValueError for 0 or a number not in the list."""
    for line, places in enumerate(PLACE_LINES, 1):
        if place in places:
            return line
    raise ValueError("not a place")


@dataclass
class MapUnit:
    addr: int
    kind: int          # 1 EMG, 2 the glove and the sock, 3 Nataša, 4 Míša
    place: int         # from the place list
    imus: int
    firmware: int


def meta_suit(serial: bytes, run: int, start: int, bata_ver: int, p1_ver: int, p2_ver: int,
              rate: int, joints: int, contacts: int, ecg_ch: int, units: list[MapUnit], present: int) -> Packet:
    """Meta 1: the suit, the run and the map, 6 B a unit, up to 22 units."""
    if len(units) > UNITS:
        raise ValueError("up to 22 units")
    data = serial.ljust(8, b"\0")[:8] + struct.pack("<IIHHH", run, start, bata_ver, p1_ver, p2_ver)
    data += bytes([rate, joints, contacts, ecg_ch, len(units)])
    data += b"".join(struct.pack("<BBBBH", u.addr, u.kind, u.place, u.imus, u.firmware) for u in units)
    return meta(1, data + struct.pack("<I", present))


def parse_meta_suit(data: bytes) -> tuple[list[MapUnit], int]:
    n = data[26]
    units = [MapUnit(*struct.unpack_from("<BBBBH", data, 27 + 6 * i)) for i in range(n)]
    return units, struct.unpack_from("<I", data, 27 + 6 * n)[0]


def meta_bones(height_mm: int, mass_01kg: int, lengths_mm: list[int]) -> Packet:
    if len(lengths_mm) != 16:
        raise ValueError("neck, torso, shoulder width, pelvis width, then left and right: upper arm, "
                         "forearm, hand, thigh, shin, foot")
    return meta(2, struct.pack("<HH16H", height_mm, mass_01kg, *lengths_mm))


def meta_joints(sub: int, entries: list[tuple[int, int, int, int]], contacts: list[int] | None = None) -> Packet:
    """sub 3: values 0-63; sub 4: values 64-126 and the 32 contact areas."""
    if sub == 3 and len(entries) == 64 and contacts is None:
        return meta(3, b"".join(struct.pack("<BBbb", *e) for e in entries))
    if sub == 4 and len(entries) == 63 and contacts is not None and len(contacts) == 32:
        return meta(4, b"".join(struct.pack("<BBbb", *e) for e in entries) + bytes(contacts))
    raise ValueError("64 entries for sub 3; 63 entries and 32 areas for sub 4")


def meta_electrodes(channels: bytes, bias_unit: int, bias_found: int, bias_stat: int) -> Packet:
    """Meta 5: the EMG units' channels in the map's order, 16 a module of two chips and 8 of one,
    the glove's and the sock's 8, 280 B, zeros beyond the last; the unit driving the bias as its
    place in the map; the bias electrodes found (u32); BIAS_STAT now."""
    if len(channels) > CHANNELS:
        raise ValueError("280 channel bytes at most")
    return meta(5, channels.ljust(CHANNELS, b"\0") + struct.pack("<BIB", bias_unit, bias_found, bias_stat))


def meta_temperatures(processors: list[int], imus: list[int], boards: tuple[int, int, int],
                      battery: bytes, power: int, fan_rpm: int) -> Packet:
    """Meta 6: the units' processors (22 × i16), the IMUs as many as meta 1 says (i8), up to 121:
    the modules' 64 places, the gloves' 40, the socks' 16 and Míša's; Mamka's two and Baťa's CPU
    (3 × i16), the battery's 23 B, the power's bits (u16) and the fan."""
    if len(processors) != UNITS or len(imus) > IMUS or len(battery) != 23:
        raise ValueError("22 processors, up to 121 IMUs, 23 B of the battery")
    data = struct.pack(f"<{UNITS}h", *processors) + struct.pack(f"<{len(imus)}b", *imus)
    data += struct.pack("<3h", *boards) + battery + struct.pack("<HH", power, fan_rpm)
    return meta(6, data)


def meta_fatigue(groups: bytes, fatigue: bytes) -> Packet:
    """The muscle group of each of the 280 channels in the map's order, then the fatigue of 1-64."""
    if len(groups) != CHANNELS or len(fatigue) != 64:
        raise ValueError("280 groups and 64 fatigue bytes")
    return meta(7, groups + fatigue)


def meta_time(utc_sample: int, utc_second: int, lat: int, lon: int, height_m: int, fix: int, sats: int) -> Packet:
    return meta(8, struct.pack("<IIiihBB4x", utc_sample, utc_second, lat, lon, height_m, fix, sats))


# --- subscribe ------------------------------------------------------------------------------------

def subscribe(types: int, rate: int, cls: int) -> bytes:
    """8 B: the mark, the packet types as a mask, the rate's code, the class's code; Baťa answers
    with the same 8 B, saying what he sends."""
    if rate not in RATE_FPS or cls not in CLASS_LEN:
        raise ValueError("a rate 0-3, a class 0-2")
    return SUBSCRIBE_MARK + struct.pack("<IBB", types & 0xFFFFFFFF, rate, cls)


def unpack_subscribe(b: bytes) -> tuple[int, int, int]:
    if len(b) != 8:
        raise ValueError("subscribe is 8 B")
    types, rate, cls = struct.unpack_from("<IBB", b, 2)
    if bytes(b[:2]) != SUBSCRIBE_MARK or rate not in RATE_FPS or cls not in CLASS_LEN:
        raise ValueError("not a subscribe message")
    return types, rate, cls


def answer_subscribe(b: bytes, largest: dict[int, int]) -> bytes:
    """Baťa's answer: the class raised to hold the largest packet of the types asked for, given as
    {type: its largest packet's size with the header}."""
    types, rate, cls = unpack_subscribe(b)
    need = max((size for t, size in largest.items() if types >> t & 1), default=0)
    while need > data_len(cls):
        cls += 1
        if cls not in CLASS_LEN:
            raise ValueError("no class holds it")
    return subscribe(types, rate, cls)
