"""CI-BTP: the 512 B output frames of Baťa and their packets (porjadok/SOFTWARE.md, "Output")."""
from __future__ import annotations

import struct
from dataclasses import dataclass

from .crc import crc16

FRAME_LEN = 512
PACKET_AREA = 504            # 63 blocks of 8 B
FRAME_IDLE, FRAME_SUIT = 0x00, 0x01
P_SNAPSHOT, P_META, P_ECG, P_SPHERE, P_EVENT, P_VITALS = 1, 2, 3, 4, 5, 6
SNAPSHOT_LEN = 127 + 4       # the joints' bytes and the contacts' 32 bits
META_LEN = {1: 64, 2: 36, 3: 256, 4: 284, 5: 132, 6: 132, 7: 192, 8: 24}
SUBSCRIBE_MAGIC = 0xC1A1
RATE_128, RATE_64, RATE_32 = 1, 2, 3


@dataclass
class Packet:
    type: int
    sub: int
    data: bytes

    def pack(self) -> bytes:
        """The 4 B header and the data, padded so the next packet starts on an 8 B boundary."""
        body = struct.pack("<BBH", self.type, self.sub, len(self.data)) + self.data
        return body + bytes((-len(body)) % 8)


@dataclass
class Frame:
    sample: int
    packets: list[Packet]
    type: int = FRAME_SUIT

    def pack(self) -> bytes:
        area = b"".join(p.pack() for p in self.packets)
        if len(area) > PACKET_AREA:
            raise ValueError("the packets do not fit the 504 B")
        area += bytes(PACKET_AREA - len(area))
        control = struct.pack("<IBBH", self.sample & 0xFFFFFFFF, self.type, len(self.packets), 0)
        whole = area + control
        return whole[:-2] + struct.pack("<H", crc16(whole))

    @classmethod
    def unpack(cls, b: bytes) -> "Frame":
        if len(b) != FRAME_LEN:
            raise ValueError("a frame is 512 B")
        if struct.unpack_from("<H", b, 510)[0] != crc16(b[:510] + b"\0\0"):
            raise ValueError("bad CRC")
        sample, typ, count, _ = struct.unpack_from("<IBBH", b, PACKET_AREA)
        packets, pos = [], 0
        for _ in range(count):
            t, s, ln = struct.unpack_from("<BBH", b, pos)
            if pos + 4 + ln > PACKET_AREA:
                raise ValueError("a packet runs past the area")
            packets.append(Packet(t, s, bytes(b[pos + 4:pos + 4 + ln])))
            pos += (4 + ln + 7) // 8 * 8
        return cls(sample, packets, typ)


def idle(sample: int) -> Frame:
    return Frame(sample, [], FRAME_IDLE)


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


def event(counter: int, what: int, which: int, detail: bytes = b"") -> Packet:
    return Packet(P_EVENT, 0, bytes([counter & 0xFF, what, which]) + detail.ljust(5, b"\0")[:5])


def vitals(heart_bpm: int, rmssd_ms: int, breaths: int, skin_c: int, quality: int) -> Packet:
    """8 B once a second: the heart rate, its variability, the breathing rate, the skin temperature."""
    return Packet(P_VITALS, 0, struct.pack("<BBBbB3x", heart_bpm, rmssd_ms, breaths, skin_c, quality))


def meta(sub: int, data: bytes) -> Packet:
    if META_LEN.get(sub) != len(data):
        raise ValueError(f"meta {sub} is {META_LEN.get(sub)} B")
    return Packet(P_META, sub, data)


def meta_suit(serial: bytes, run: int, start: int, bata_ver: int, versions: tuple[int, int, int, int],
              present: int, block_versions: list[int], rate: int, joints: int, contacts: int, ecg_ch: int) -> Packet:
    data = serial.ljust(8, b"\0")[:8] + struct.pack("<IIH4HH", run, start, bata_ver, *versions, present)
    data += struct.pack("<16H", *(block_versions + [0] * 16)[:16]) + bytes([rate, joints, contacts, ecg_ch])
    return meta(1, data)


def meta_bones(height_mm: int, mass_01kg: int, lengths_mm: list[int]) -> Packet:
    if len(lengths_mm) != 16:
        raise ValueError("neck, torso, shoulder width, pelvis width, then left and right: upper arm, forearm, hand, thigh, shin, foot")
    return meta(2, struct.pack("<HH16H", height_mm, mass_01kg, *lengths_mm))


def meta_joints(sub: int, entries: list[tuple[int, int, int, int]], contacts: list[int] | None = None) -> Packet:
    """sub 3: values 0–63; sub 4: values 64–126 and the 32 contact areas."""
    if sub == 3 and len(entries) == 64 and contacts is None:
        return meta(3, b"".join(struct.pack("<BBbb", *e) for e in entries))
    if sub == 4 and len(entries) == 63 and contacts is not None and len(contacts) == 32:
        return meta(4, b"".join(struct.pack("<BBbb", *e) for e in entries) + bytes(contacts))
    raise ValueError("64 entries for sub 3; 63 entries and 32 areas for sub 4")


def meta_electrodes(channels: bytes, bias_block: int) -> Packet:
    """128 B, one per channel: bit 0 P off, 1 N off, 2 on, 3 drives the bias, 4–7 quality; then the bias block."""
    if len(channels) != 128:
        raise ValueError("128 channel bytes")
    return meta(5, channels + bytes([bias_block]) + bytes(3))


def meta_temperatures(blocks: list[int], imus: list[int], boards: tuple[int, int, int],
                      cells: tuple[int, int, int, int], pack: int, current: int, temps: tuple[int, int, int],
                      alarms: int, soc: int, remaining: int, pgood_en: int, fan_rpm: int) -> Packet:
    """The blocks' processors (16 × i16), the IMUs (64 × i8), Mamka's two and Baťa's CPU, the BMS's block."""
    if len(blocks) != 16 or len(imus) != 64:
        raise ValueError("16 block temperatures and 64 IMU temperatures")
    data = struct.pack("<16h", *blocks) + struct.pack("<64b", *imus) + struct.pack("<3h", *boards)
    data += struct.pack("<4HHh3hHBH", *cells, pack, current, *temps, alarms, soc, remaining)
    data += struct.pack("<BH4x", pgood_en, fan_rpm)
    return meta(6, data)


def meta_fatigue(groups: bytes, fatigue: bytes) -> Packet:
    """The muscle group of each of the 128 channels, then the fatigue of groups 1–64."""
    if len(groups) != 128 or len(fatigue) != 64:
        raise ValueError("128 groups and 64 fatigue bytes")
    return meta(7, groups + fatigue)


def meta_time(utc_sample: int, utc_second: int, lat: int, lon: int, height_m: int, fix: int, sats: int) -> Packet:
    return meta(8, struct.pack("<IIiihBB4x", utc_sample, utc_second, lat, lon, height_m, fix, sats))


def subscribe(types: int, rate: int) -> bytes:
    return struct.pack("<HIBB", SUBSCRIBE_MAGIC, types, rate, 0)


def unpack_subscribe(b: bytes) -> tuple[int, int]:
    magic, types, rate, _ = struct.unpack("<HIBB", b)
    if magic != SUBSCRIBE_MAGIC or rate not in (RATE_128, RATE_64, RATE_32):
        raise ValueError("not a subscribe message")
    return types, rate
