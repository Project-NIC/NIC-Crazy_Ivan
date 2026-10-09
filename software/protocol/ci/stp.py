"""CI-STP: the control frame, the containers, the frames and the records (porjadok/SOFTWARE.md).

Byte orders, where the pages had to be pinned down while this was written:
- a frame's word is the channel's 3 B of ADS1299 data as the chip sends them, most significant
  first (two's complement, 24 bits), followed by the 1 B of info;
- every 16- and 32-bit field is little-endian.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

from .crc import crc16

# --- the control frame -------------------------------------------------------------------------

CMD_RUNNING, CMD_GET_READY, CMD_START, CMD_STOP, CMD_REPEAT, CMD_RESET = range(6)
ADDR_ALL = 0x00
BEHIND = 0x80  # bit 7: the unit behind that block (a glove, Míša behind Nataša)
MAX_CONTAINERS = 12
CONTROL_FRAME_LEN = 6


@dataclass
class ControlFrame:
    cmd: int
    addr: int
    sample: int
    count: int = 0  # containers that follow in this cycle, 0–12

    def pack(self) -> bytes:
        if not 0 <= self.cmd <= 7 or not 0 <= self.count <= MAX_CONTAINERS:
            raise ValueError("cmd 0–7, count 0–12")
        head = struct.pack("<BBH", (self.cmd << 5) | self.count, self.addr & 0xFF, self.sample & 0xFFFF)
        return head + struct.pack("<H", crc16(head))

    @classmethod
    def unpack(cls, b: bytes) -> "ControlFrame":
        if len(b) != CONTROL_FRAME_LEN:
            raise ValueError("a control frame is 6 B")
        if struct.unpack_from("<H", b, 4)[0] != crc16(b[:4]):
            raise ValueError("bad CRC")
        cc, addr, sample = struct.unpack_from("<BBH", b)
        return cls(cmd=cc >> 5, addr=addr, sample=sample, count=cc & 0x0F)


# --- containers ---------------------------------------------------------------------------------

LINE_DATA_MAX = 60   # on the lines, so one cycle's sound fits
WIRE_DATA_MAX = 122  # on the I2C to Baťa and on Míša's wire
ANSWER = 0x80        # the block's answer: 0x80 + the type it answers

T_ADS_WRITE, T_IMU_WRITE, T_READ_BACK, T_SETTINGS, T_FW_PIECE, T_FW_CONTROL = range(1, 7)
T_REPEAT_MORE, T_SOUND_DOWN, T_HEAD, T_SPHERE, T_MEASURE = range(7, 12)
T_IC_CALL, T_IC_ANSWER = 0x20, 0xA0  # Interconnect, the forearm's module to a Vnučka and back


@dataclass
class Container:
    addr: int
    type: int
    seq: int
    data: bytes = b""

    def pack(self, data_max: int = LINE_DATA_MAX) -> bytes:
        if len(self.data) > data_max:
            raise ValueError(f"data at most {data_max} B here")
        body = struct.pack("<BBBB", self.addr & 0xFF, self.type & 0xFF, len(self.data), self.seq & 0xFF)
        body += self.data
        return body + struct.pack("<H", crc16(body))

    @classmethod
    def unpack(cls, b: bytes, data_max: int = WIRE_DATA_MAX) -> tuple["Container", int]:
        """Returns the container and the number of bytes it took, so a message can be walked."""
        if len(b) < 6:
            raise ValueError("a container is at least 6 B")
        addr, typ, ln, seq = struct.unpack_from("<BBBB", b)
        if ln > data_max or len(b) < 6 + ln:
            raise ValueError("bad length")
        end = 4 + ln
        if struct.unpack_from("<H", b, end)[0] != crc16(b[:end]):
            raise ValueError("bad CRC")
        return cls(addr, typ, seq, bytes(b[4:end])), end + 2

    def answer(self, result: int, data: bytes = b"") -> "Container":
        """The block's answer: 0x80 + type, the same seq, a result byte, then the data."""
        return Container(self.addr, (self.type | ANSWER) & 0xFF, self.seq, bytes([result]) + data)


def pack_message(control: ControlFrame, containers: list[Container]) -> bytes:
    """The master's one message a cycle: the control frame, then the containers it announces."""
    control.count = len(containers)
    return control.pack() + b"".join(c.pack() for c in containers)


def unpack_message(b: bytes) -> tuple[ControlFrame, list[Container]]:
    cf = ControlFrame.unpack(b[:CONTROL_FRAME_LEN])
    pos, out = CONTROL_FRAME_LEN, []
    for _ in range(cf.count):
        c, n = Container.unpack(b[pos:], LINE_DATA_MAX)
        out.append(c)
        pos += n
    return cf, out


# --- the block's frame, 40 B ---------------------------------------------------------------------

FRAME_LEN = 40
ROTATION = 32  # positions of the rotating content and of the IMU bytes: sample mod 32
IMU_STEP_LEN = 12  # one IMU's step, 12 B, one byte a frame at positions 0–11


def s24(b: bytes) -> int:
    v = int.from_bytes(b, "big")
    return v - (1 << 24) if v & 0x800000 else v


def u24(v: int) -> bytes:
    return (v & 0xFFFFFF).to_bytes(3, "big")


@dataclass
class BlockFrame:
    block: int                 # the block number, a check against the slot
    sample: int                # 16-bit sample number
    channels: list[int]        # 8 signed 24-bit values
    loff_statp: int = 0
    loff_statn: int = 0
    gpio: int = 0              # GPIO[7:4], tied to DGND on the board
    rotation: bytes = b"\0\0\0\0"  # 4 B at position sample % 32
    imu: bytes = b"\0\0\0\0"       # 1 B per IMU, position sample % 32 of its 12 B step

    def pack(self) -> bytes:
        if len(self.channels) != 8 or len(self.rotation) != 4 or len(self.imu) != 4:
            raise ValueError("8 channels, 4 B of rotation, 4 IMU bytes")
        info = [self.block & 0xFF, self.loff_statp & 0xFF, self.loff_statn & 0xFF,
                0xC0 | (self.gpio & 0x0F)] + list(self.rotation)
        body = b"".join(u24(c) + bytes([i]) for c, i in zip(self.channels, info))
        body += self.imu + struct.pack("<H", self.sample & 0xFFFF)
        return body + struct.pack("<H", crc16(body))

    @classmethod
    def unpack(cls, b: bytes) -> "BlockFrame":
        if len(b) != FRAME_LEN:
            raise ValueError("a block's frame is 40 B")
        if struct.unpack_from("<H", b, 38)[0] != crc16(b[:38]):
            raise ValueError("bad CRC")
        ch = [s24(b[4 * i:4 * i + 3]) for i in range(8)]
        info = [b[4 * i + 3] for i in range(8)]
        if info[3] & 0xF0 != 0xC0:
            raise ValueError("the status word's 1100 is missing")
        return cls(block=info[0], sample=struct.unpack_from("<H", b, 36)[0], channels=ch,
                   loff_statp=info[1], loff_statn=info[2], gpio=info[3] & 0x0F,
                   rotation=bytes(info[4:8]), imu=bytes(b[32:36]))

    @property
    def position(self) -> int:
        return self.sample % ROTATION


class StepAssembler:
    """Collects the IMU bytes and the rotating content of one block, frame by frame.

    An IMU's 12 B step is complete at position 11; the 128 B of rotating content at position 31.
    A second IMU on the same byte (the foot) sits at positions 12–23.
    """

    def __init__(self, imus_per_byte: int = 1) -> None:
        self.imus_per_byte = imus_per_byte  # 2 when a foot's IMUs ride at positions 12–23
        self.imu = [bytearray(IMU_STEP_LEN) for _ in range(8)]
        self.rotation = bytearray(4 * ROTATION)
        self.steps: list[tuple[int, int, bytes]] = []  # (sample, imu index, 12 B) as completed

    def feed(self, f: BlockFrame) -> None:
        p = f.position
        self.rotation[4 * p:4 * p + 4] = f.rotation
        for i, byte in enumerate(f.imu):
            if p < IMU_STEP_LEN:
                self.imu[i][p] = byte
                if p == IMU_STEP_LEN - 1:
                    self.steps.append((f.sample, i, bytes(self.imu[i])))
            elif self.imus_per_byte == 2 and p < 2 * IMU_STEP_LEN:
                self.imu[4 + i][p - IMU_STEP_LEN] = byte
                if p == 2 * IMU_STEP_LEN - 1:
                    self.steps.append((f.sample, 4 + i, bytes(self.imu[4 + i])))


def imu_step(dtheta: tuple[int, int, int], force: tuple[int, int, int]) -> bytes:
    """One IMU's 12 B: the step's turn then its mean force, three i16 each, in the raw scale."""
    return struct.pack("<3h3h", *dtheta, *force)


# --- Nataša's frame, 68 B ------------------------------------------------------------------------

NATASA_FRAME_LEN = 68
NATASA_ROTATION = 16
MIC_PLACES = 13


@dataclass
class NatasaFrame:
    sample: int
    state: int = 0
    buttons: int = 0
    rotation: bytes = bytes(8)
    mics: list[tuple[int, int]] = field(default_factory=list)  # (left, right), 12 or 13
    addr: int = 1

    def pack(self) -> bytes:
        if len(self.mics) not in (12, 13) or len(self.rotation) != 8:
            raise ValueError("12 or 13 samples, 8 B of rotation")
        state = (self.state & ~1) | (1 if len(self.mics) == 13 else 0)
        body = struct.pack("<BBHH", self.addr, state, self.sample & 0xFFFF, self.buttons & 0xFFFF)
        body += self.rotation
        for l, r in self.mics:
            body += struct.pack("<hh", l, r)
        body += bytes(4 * (MIC_PLACES - len(self.mics)))
        return body + struct.pack("<H", crc16(body))

    @classmethod
    def unpack(cls, b: bytes) -> "NatasaFrame":
        if len(b) != NATASA_FRAME_LEN:
            raise ValueError("Nataša's frame is 68 B")
        if struct.unpack_from("<H", b, 66)[0] != crc16(b[:66]):
            raise ValueError("bad CRC")
        addr, state, sample, buttons = struct.unpack_from("<BBHH", b)
        n = 13 if state & 1 else 12
        mics = [struct.unpack_from("<hh", b, 14 + 4 * i) for i in range(n)]
        return cls(sample, state, buttons, bytes(b[6:14]), mics, addr)

    @property
    def position(self) -> int:
        return self.sample % NATASA_ROTATION


# --- the record to Baťa, two halves of 384 B -----------------------------------------------------

HALF_LEN = 384
RECORD_LEN = 2 * HALF_LEN
FLAG_HALF, FLAG_WAITED, FLAG_MISSING, FLAG_DROPPED = 1, 2, 4, 8


@dataclass
class RecordHalf:
    sample: int
    half: int                      # 0: lines 1 and 2, 1: lines 3 and 4
    frames: list[bytes | None]     # eight slots, 40 B each or None
    glove: bytes | None = None     # the glove's frame on that half's forearm module
    pending: int = 0
    flags: int = 0                 # FLAG_WAITED, FLAG_MISSING, FLAG_DROPPED

    def pack(self) -> bytes:
        if len(self.frames) != 8:
            raise ValueError("eight slots")
        present = sum(1 << i for i, f in enumerate(self.frames) if f) | (0x100 if self.glove else 0)
        flags = (self.flags & ~FLAG_HALF) | (self.half & 1)
        body = struct.pack("<HBBHH", self.sample & 0xFFFF, flags, self.pending & 0xFF, present, 0)
        body += b"".join(f or bytes(FRAME_LEN) for f in self.frames)
        body += self.glove or bytes(FRAME_LEN)
        body += bytes(14)
        return body + struct.pack("<H", crc16(body))

    @classmethod
    def unpack(cls, b: bytes) -> "RecordHalf":
        if len(b) != HALF_LEN:
            raise ValueError("a half is 384 B")
        if struct.unpack_from("<H", b, 382)[0] != crc16(b[:382]):
            raise ValueError("bad CRC")
        sample, flags, pending, present, _ = struct.unpack_from("<HBBHH", b)
        frames = [bytes(b[8 + 40 * i:48 + 40 * i]) if present & (1 << i) else None for i in range(8)]
        glove = bytes(b[328:368]) if present & 0x100 else None
        return cls(sample, flags & 1, frames, glove, pending, flags & ~FLAG_HALF)


# --- the UART and the I2C to Baťa -----------------------------------------------------------------

UART_SYNC = 0xC1A1
LINE_ALL, LINE_PROC1 = 0xFF, 0
I2C_TRANSFER = 128


def pack_uart(line: int, c: Container) -> bytes:
    return struct.pack("<HB", UART_SYNC, line & 0xFF) + c.pack()


def unpack_uart(b: bytes) -> tuple[int, Container, int]:
    """Returns the line, the container and the bytes taken; b must start at the sync word."""
    if len(b) < 3 or struct.unpack_from("<H", b)[0] != UART_SYNC:
        raise ValueError("no sync word")
    c, n = Container.unpack(b[3:], LINE_DATA_MAX)
    return b[2], c, 3 + n


def pack_i2c(c: Container) -> bytes:
    body = c.pack(WIRE_DATA_MAX)
    return body + bytes(I2C_TRANSFER - len(body))


def unpack_i2c(b: bytes) -> Container | None:
    """None for the empty transfer, a container of type 0 and zeros."""
    if len(b) != I2C_TRANSFER:
        raise ValueError("an I2C transfer is 128 B")
    if b[1] == 0 and not any(b):
        return None
    return Container.unpack(b, WIRE_DATA_MAX)[0]


# --- firmware -------------------------------------------------------------------------------------

FW_PIECE = 48
FW_BEGIN, FW_COMMIT, FW_ABORT, FW_CONFIRM = 1, 2, 3, 4
KIND_BLOCK, KIND_VNUCKA, KIND_NATASA, KIND_MISA, KIND_PROC1, KIND_PROC2 = range(1, 7)


def fw_begin(addr: int, seq: int, kind: int, version: int, image: bytes) -> Container:
    from .crc import crc32
    data = struct.pack("<BBHII", FW_BEGIN, kind, version, len(image), crc32(image))
    return Container(addr, T_FW_CONTROL, seq, data)


def fw_pieces(addr: int, seq0: int, image: bytes, piece: int = FW_PIECE) -> list[Container]:
    """The image in pieces of 48 B, offsets in order; the last padded with 0xFF to a word."""
    out, seq = [], seq0
    for off in range(0, len(image), piece):
        chunk = image[off:off + piece]
        pad = (-len(chunk)) % 16
        out.append(Container(addr, T_FW_PIECE, seq & 0xFF, struct.pack("<I", off) + chunk + b"\xFF" * pad))
        seq += 1
    return out


def fw_control(addr: int, seq: int, what: int) -> Container:
    return Container(addr, T_FW_CONTROL, seq, bytes([what]))


# --- Interconnect, Míša's wire, the head ------------------------------------------------------------

def ic_call(finger: int, seq: int) -> Container:
    return Container(finger, T_IC_CALL, seq)


def ic_answer(finger: int, seq: int, state: int, steps: list[bytes]) -> Container:
    if len(steps) != 4 or any(len(s) != IMU_STEP_LEN for s in steps):
        raise ValueError("four steps of 12 B")
    return Container(finger, T_IC_ANSWER, seq, bytes([state]) + b"".join(steps))


SPHERE_LEN = 112
SPHERE_FIELDS = 36


def sphere(frame_no: int, status: int, turn: int, pitch: int, fields: list[tuple[int, int, int]]) -> bytes:
    """Míša's sphere: 4 B header, then 36 fields of (distance, speed, confidence byte)."""
    if len(fields) != SPHERE_FIELDS:
        raise ValueError("36 fields")
    out = struct.pack("<BBbb", frame_no & 0xFF, status & 0xFF, turn, pitch)
    for d, s, c in fields:
        out += struct.pack("<Bbb", d & 0xFF, s, c)
    return out


HEAD_VIBRATE, HEAD_PULSE, HEAD_STOP, HEAD_DEFINE, HEAD_SETTINGS = 1, 2, 3, 4, 5


def head_vibrate(seq: int, motors: int, pattern: int, strength: int, repeats: int = 1) -> Container:
    return Container(1, T_HEAD, seq, bytes([HEAD_VIBRATE, motors, pattern, strength, repeats]))


def head_pulse(seq: int, motors: int, length_10ms: int, strength: int) -> Container:
    return Container(1, T_HEAD, seq, bytes([HEAD_PULSE, motors, length_10ms, strength]))


def head_define(seq: int, pattern: int, steps: list[tuple[int, int]]) -> Container:
    if not 8 <= pattern <= 15 or len(steps) > 8:
        raise ValueError("patterns 8–15, up to 8 steps")
    data = bytes([HEAD_DEFINE, pattern]) + b"".join(bytes(s) for s in steps) + (b"\0" if len(steps) < 8 else b"")
    return Container(1, T_HEAD, seq, data)
