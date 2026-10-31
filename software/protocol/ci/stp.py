"""CI-STP: the suit's four frames, their kinds and layouts, the units' registers, the places on the
SPIs to Baťa and the firmware's blocks (porjadok/SOFTWARE.md).

Byte orders, as the pages give them:
- every field of 16 and 32 bits is little-endian, the frame's number and the CRC too;
- an ADS129x channel is its 3 B as the chip sends them, most significant first (two's complement);
- an IMU's temperature is its OUT_TEMP, 2 B as the chip gives them, OUT_TEMP_L first.

Where the pages leave a detail to the code, the choice is said in the docstring.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

from .crc import crc16, crc32

# --- the five frames and their kinds -------------------------------------------------------------

FRAME_LEN, SHORT_LEN, FIRMWARE_LEN, SOUND_LEN = 34, 8, 519, 198
DATA2_LEN = 58         # a frame of data of 58 B: a module of two chips' 0x24, the glove's 0x25
BODY_LEN = 28          # bytes 4-31 of a frame of 34 B
SHORT_BODY = 3         # bytes 3-5 of a frame of 8 B
VALUES = 25            # the values in a read's answer or a write of several registers
ANSWER = 0x80          # bit 7 of the kind: an answer

K_DISCOVER, K_ASSIGN, K_READ, K_WRITE, K_DIRECT, K_WRITE_MANY = 0x01, 0x02, 0x03, 0x04, 0x05, 0x06
K_GET_READY, K_START, K_STOP, K_REPEAT, K_HEARTBEAT, K_MAMKA, K_BUS_TEST = range(0x10, 0x17)
K_DATA, K_DIAGNOSTICS, K_SOUND_DOWN, K_SOUND_UP = 0x20, 0x21, 0x22, 0x23
K_DATA2 = 0x24                         # the data of a module with two ADS1298, 58 B
K_END = 0x25                           # the glove's and the sock's: 8 channels and 28 B of steps, 58 B
K_FIRMWARE = 0x30

LENGTH = {
    K_DISCOVER: 8, K_DISCOVER | ANSWER: 34, K_ASSIGN: 34, K_ASSIGN | ANSWER: 8,
    K_READ: 8, K_READ | ANSWER: 34, K_WRITE: 8, K_WRITE_MANY: 34,
    K_WRITE | ANSWER: 8, K_WRITE_MANY | ANSWER: 8, K_DIRECT: 34,
    K_GET_READY: 8, K_GET_READY | ANSWER: 8, K_START: 8, K_STOP: 8, K_REPEAT: 8,
    K_HEARTBEAT: 8, K_MAMKA: 8, K_BUS_TEST: 34,
    K_DATA: 34, K_DATA2: 58, K_END: 58, K_DIAGNOSTICS: 34, K_SOUND_DOWN: 198, K_SOUND_UP: 198,
    K_FIRMWARE: 519,
}

# --- the units' numbers, the chips, the results ---------------------------------------------------

EVERY = 0x00                           # every unit; also a unit's own number before *assign*
P1, P2 = 0xF1, 0xF2                    # Mamka's two processors
NATASA, MISA = 0x81, 0x82              # line 8's, fixed
SENSING = range(0x01, 0x80)            # given at the start by *assign*

CHIP_UNIT, CHIP_ADS, CHIP_SOUND, CHIP_MOTORS, CHIP_BMS, CHIP_SPHERE, CHIP_ADS2 = range(7)
CHIP_BRATISKA = 0x07                   # 0x07-0x0A the glove's and the sock's Bratiški, her chips
CHIP_EVERY_IMU, CHIP_IMU = 0x0F, 0x10  # 0x10... the IMUs in the order of the unit's table

DONE, NO_ANSWER, NO_CHIP, NO_REGISTER, REFUSED = range(5)              # a write's result
READY, READY_NO_ADS, READY_IMU_MISSING, READY_NO_SETTINGS = range(4)   # *get ready*'s


def seal(body: bytes) -> bytes:
    """A frame's bytes and their CRC-16/CCITT-FALSE, little-endian."""
    return bytes(body) + struct.pack("<H", crc16(body))


def check(frame: bytes) -> bytes:
    """The frame if its length is its kind's and its CRC holds; ValueError otherwise. The length
    is checked before anything else in it is read."""
    if len(frame) < 2 or frame[1] not in LENGTH or len(frame) != LENGTH[frame[1]]:
        raise ValueError("not a frame of its kind's length")
    if struct.unpack_from("<H", frame, len(frame) - 2)[0] != crc16(frame[:-2]):
        raise ValueError("bad CRC")
    return bytes(frame)


@dataclass
class Frame:
    """A frame of 34 B, 58 B, 8 B or a sound packet: the unit's number, the kind, the number, the
    body.
    The number is the frame's, a cycle's, in data and in what goes unasked; the command's in the
    commands and their answers; the test's running number in the bus test; the packet's in sound.
    It takes 2 B, but 1 B in a frame of 8 B."""
    unit: int
    kind: int
    number: int = 0
    body: bytes = b""

    def pack(self) -> bytes:
        n = LENGTH[self.kind]
        if n == SHORT_LEN:
            head, room = bytes([self.unit & 0xFF, self.kind, self.number & 0xFF]), SHORT_BODY
        elif n in (FRAME_LEN, DATA2_LEN, SOUND_LEN):
            head = struct.pack("<BBH", self.unit & 0xFF, self.kind, self.number & 0xFFFF)
            room = n - 6
        else:
            raise ValueError("a firmware block is a FirmwareFrame")
        if len(self.body) > room:
            raise ValueError(f"{room} B at most in a frame of {n} B")
        return seal(head + self.body.ljust(room, b"\0"))

    @classmethod
    def unpack(cls, frame: bytes) -> "Frame":
        b = check(frame)
        if len(b) == SHORT_LEN:
            return cls(b[0], b[1], b[2], b[3:6])
        if len(b) == FIRMWARE_LEN:
            raise ValueError("a firmware block is a FirmwareFrame")
        return cls(b[0], b[1], struct.unpack_from("<H", b, 2)[0], b[4:-2])

    @property
    def is_answer(self) -> bool:
        return bool(self.kind & ANSWER)


def u16(v: int) -> bytes:
    return struct.pack("<H", v & 0xFFFF)


def widen(near: int, low: int) -> int:
    """The full cycle count nearest `near` whose low 16 bits are `low`: the frames' numbers
    wrap after 17 s, and Mamka and Baťa keep the whole count."""
    d = (low - near) & 0xFFFF
    return near + d - 0x10000 if d >= 0x8000 else near + d


# --- the commands and their answers ---------------------------------------------------------------

def discover(number: int = 0) -> bytes:
    return Frame(EVERY, K_DISCOVER, number).pack()


UID_LEN = 12
WAIT_STEP_US = 10      # a unit waits CRC-16 of its UID × 10 µs before it answers *discover*


def wait_us(uid: bytes, attempt: int = 0) -> int:
    """The wait before *discover*'s answer: the CRC-16 over the 96-bit UID, and after a collision
    over the UID and the attempt's number. The attempt's number as one byte is the code's choice."""
    if len(uid) != UID_LEN:
        raise ValueError("the UID is 96 bits, 12 B")
    return WAIT_STEP_US * crc16(uid if attempt == 0 else uid + bytes([attempt & 0xFF]))


def discover_answer(uid: bytes, number: int = 0) -> bytes:
    """0x81 from a unit with no number yet, so its byte 0 is 0: the whole UID, then zeros."""
    if len(uid) != UID_LEN:
        raise ValueError("the UID is 12 B")
    return Frame(EVERY, K_DISCOVER | ANSWER, number, uid).pack()


def assign(uid: bytes, new: int, number: int = 0) -> bytes:
    """To every unit, the UID and the new number: the unit with that UID takes it."""
    if len(uid) != UID_LEN or new not in SENSING:
        raise ValueError("a UID of 12 B and a number 1-0x7F")
    return Frame(EVERY, K_ASSIGN, number, uid + bytes([new])).pack()


def parse_assign(frame: bytes) -> tuple[bytes, int]:
    f = Frame.unpack(frame)
    if f.kind != K_ASSIGN:
        raise ValueError("not assign")
    return f.body[:UID_LEN], f.body[UID_LEN]


def result(to: Frame, code: int = DONE, unit: int | None = None) -> bytes:
    """The short answer to a question: its kind with bit 7, its command's number, the result.
    *Assign*'s comes from the new number."""
    return Frame(to.unit if unit is None else unit, to.kind | ANSWER, to.number,
                 bytes([code])).pack()


def read(unit: int, chip: int, reg: int, count: int, number: int = 0) -> bytes:
    if not 1 <= count <= VALUES:
        raise ValueError("1-25 registers")
    return Frame(unit, K_READ, number, bytes([chip, reg, count])).pack()


@dataclass
class Registers:
    """A read's answer or a write of several registers: the chip, the first register, the count
    and up to 25 B of values, in bytes 4-31."""
    unit: int
    kind: int
    number: int
    chip: int
    reg: int
    values: bytes

    def pack(self) -> bytes:
        if not 1 <= len(self.values) <= VALUES:
            raise ValueError("1-25 values")
        return Frame(self.unit, self.kind, self.number,
                     bytes([self.chip, self.reg, len(self.values)]) + self.values).pack()

    @classmethod
    def unpack(cls, frame: bytes) -> "Registers":
        f = Frame.unpack(frame)
        if f.kind not in (K_READ | ANSWER, K_WRITE_MANY):
            raise ValueError("not registers")
        chip, reg, count = f.body[:3]
        return cls(f.unit, f.kind, f.number, chip, reg, f.body[3:3 + count])


def read_answer(to: Frame, values: bytes) -> bytes:
    """The values a read asked for, with its command's number back."""
    chip, reg, _ = to.body
    return Registers(to.unit, K_READ | ANSWER, to.number, chip, reg, bytes(values)).pack()


def unasked(unit: int, chip: int, reg: int, values: bytes, cycle: int) -> bytes:
    """What a unit sends by itself: a read's answer nobody asked, the cycle's number in it."""
    return Registers(unit, K_READ | ANSWER, cycle, chip, reg, bytes(values)).pack()


def write(unit: int, chip: int, reg: int, value: int, number: int = 0) -> bytes:
    """One register in 8 B."""
    return Frame(unit, K_WRITE, number, bytes([chip, reg, value & 0xFF])).pack()


def write_many(unit: int, chip: int, reg: int, values: bytes, number: int = 0) -> bytes:
    """Up to 25 registers from `reg` in 34 B, carried out by the unit as a whole."""
    return Registers(unit, K_WRITE_MANY, number, chip, reg, bytes(values)).pack()


def direct(unit: int, chip: int, raw: bytes, number: int = 0) -> bytes:
    """Up to 26 B the unit passes to the chip as they are, for debugging; no answer."""
    if not 1 <= len(raw) <= 26:
        raise ValueError("1-26 bytes")
    return Frame(unit, K_DIRECT, number, bytes([chip, len(raw)]) + raw).pack()


def get_ready(unit: int, number: int = 0) -> bytes:
    return Frame(unit, K_GET_READY, number).pack()


def start(first_cycle: int, number: int = 0) -> bytes:
    """To every unit: the first cycle's number, which every unit counts its cycles from."""
    return Frame(EVERY, K_START, number, u16(first_cycle)).pack()


def stop(cycle: int, number: int = 0) -> bytes:
    """The cycle from which the data no longer count; START stays high."""
    return Frame(EVERY, K_STOP, number, u16(cycle)).pack()


def heartbeat(cycle: int) -> bytes:
    """Mamka's every second: her cycle's number."""
    return Frame(EVERY, K_HEARTBEAT, 0, u16(cycle)).pack()


def mamka(unit: int) -> bytes:
    """*Mamka?*, after 3 s without a heartbeat."""
    return Frame(unit, K_MAMKA).pack()


def repeat(unit: int, packet: int, number: int = 0) -> bytes:
    """Ask a sound packet again by its number."""
    return Frame(unit, K_REPEAT, number, u16(packet)).pack()


def short_value(frame: bytes) -> int:
    """The 2 B in bytes 3-4 of *start*, *stop*, *heartbeat* and *repeat*."""
    return struct.unpack_from("<H", check(frame), 3)[0]


# --- the bus test --------------------------------------------------------------------------------

def prbs9(n: int, state: int = 0x1FF) -> bytes:
    """PRBS-9, x^9 + x^5 + 1, as Osmocom's libosmocore implements ITU-T O.150's 2^9 - 1, bit by
    bit, most significant first in each byte."""
    out = bytearray()
    for _ in range(n):
        byte = 0
        for _ in range(8):
            bit = ((state >> 8) ^ (state >> 4)) & 1
            state = ((state << 1) | bit) & 0x1FF
            byte = byte << 1 | bit
        out.append(byte)
    return bytes(out)


PRBS9_PERIOD = 511     # bytes: 511 bits, and 8 shares no factor with 511
_PRBS9 = prbs9(PRBS9_PERIOD)


def pattern(n: int) -> bytes:
    """Frame n's 28 B: the sequence's bytes 28n to 28n + 27, running on and repeating every 511."""
    return bytes(_PRBS9[(BODY_LEN * n + k) % PRBS9_PERIOD] for k in range(BODY_LEN))


def bus_test(unit: int, n: int) -> bytes:
    """The test's running number in bytes 2-3, the pattern in 4-31; the same kind both ways."""
    return Frame(unit, K_BUS_TEST, n, pattern(n)).pack()


def bus_errors(frame: bytes) -> int:
    """The bits that differ from the pattern its number asks for."""
    f = Frame.unpack(frame)
    return sum(bin(a ^ b).count("1") for a, b in zip(f.body, pattern(f.number)))


# --- a unit's data --------------------------------------------------------------------------------

ADS_SPS = 1920         # the EMG's rate; 3,840 the setting to try, with a step of 32
STEP = 16              # cycles a step: 16 ADS samples at 1,920 SPS, 1/120 s
PERIOD = 32            # cycles between a unit's diagnostics, and Nataša's frames of data
IMU_STEP_LEN = 12      # an IMU's step: the turn and the mean force, three i16 each
MODULE_IMU, END_IMU = 4, 28        # IMU bytes a frame of data: a module's; the glove's and the sock's


def s24(b: bytes) -> int:
    v = int.from_bytes(b, "big")
    return v - (1 << 24) if v & 0x800000 else v


def b24(v: int) -> bytes:
    return (v & 0xFFFFFF).to_bytes(3, "big")


def imu_step(turn: tuple[int, int, int], force: tuple[int, int, int]) -> bytes:
    """An IMU's 12 B: the step's turn divided by the step, then its mean force, three i16 each in
    the raw scales of ±2000 °/s and ±16 g. The turn first is the code's choice."""
    return struct.pack("<3h3h", *turn, *force)


def imu_bytes(cycle: int, steps: list[bytes], per_frame: int) -> bytes:
    """A unit's IMU bytes in this cycle's frame of data: its steps one after another in its
    table's order, the frame whose number mod STEP is k carrying bytes per_frame × k on, zeros
    past the last."""
    stream = b"".join(steps)
    if len(stream) > STEP * per_frame:
        raise ValueError(f"more steps than {STEP} frames hold")
    k = cycle % STEP
    return stream[per_frame * k:per_frame * (k + 1)].ljust(per_frame, b"\0")


def frames_for(imus: int, per_frame: int) -> int:
    """How many frames of the STEP a unit's steps take: a module's four 12, the glove's 20 nine."""
    return -(-imus * IMU_STEP_LEN // per_frame)


class StepAssembler:
    """One unit's IMU steps put together from its frames of data: an IMU's step is whole when
    every frame holding its bytes came in the same step; a frame lost loses only the steps in it."""

    def __init__(self, imus: int, per_frame: int) -> None:
        self.imus, self.per = imus, per_frame
        self.period: int | None = None
        self.stream = bytearray(STEP * per_frame)
        self.got: set[int] = set()
        self.steps: list[tuple[int, int, bytes]] = []    # (cycle // STEP, the IMU, 12 B)

    def feed(self, cycle: int, imu: bytes) -> None:
        period, k = divmod(cycle, STEP)
        if period != self.period:
            self.period, self.got = period, set()
        self.stream[self.per * k:self.per * (k + 1)] = imu
        self.got.add(k)
        for i in range(self.imus):
            first, last = IMU_STEP_LEN * i // self.per, (IMU_STEP_LEN * (i + 1) - 1) // self.per
            if last == k and all(j in self.got for j in range(first, last + 1)):
                self.steps.append((period, i, bytes(self.stream[12 * i:12 * i + 12])))


def module_data(unit: int, cycle: int, channels: list[int], imu: bytes) -> bytes:
    """A module's frame of data: 0x20, 34 B, one chip's eight channels as the chip sends them and
    4 B of IMU steps; 0x24, 58 B, both chips' sixteen and the 4 B after them."""
    if len(channels) not in (8, 16) or len(imu) != MODULE_IMU:
        raise ValueError("8 or 16 channels and 4 IMU bytes")
    kind = K_DATA if len(channels) == 8 else K_DATA2
    return Frame(unit, kind, cycle, b"".join(b24(c) for c in channels) + imu).pack()


def end_data(unit: int, cycle: int, channels: list[int], imu: bytes) -> bytes:
    """The glove's and the sock's frame of data: 0x25, 58 B, its ADS1298's eight channels as the
    chip sends them in bytes 4-27, as a module's first chip's, and 28 B of its IMUs' steps in
    bytes 28-55."""
    if len(channels) != 8 or len(imu) != END_IMU:
        raise ValueError("8 channels and 28 IMU bytes")
    return Frame(unit, K_END, cycle, b"".join(b24(c) for c in channels) + imu).pack()


def parse_data(frame: bytes) -> tuple[int, int, list[int], bytes]:
    """The unit, the cycle's 16 bits, the 8 or 16 channels and the IMU bytes of 0x20, 0x24 or
    0x25: 4 B after a module's channels, 28 B after the glove's and the sock's eight."""
    f = Frame.unpack(frame)
    if f.kind not in (K_DATA, K_DATA2, K_END):
        raise ValueError("not data")
    n = 16 if f.kind == K_DATA2 else 8
    channels = [s24(f.body[3 * i:3 * i + 3]) for i in range(n)]
    return f.unit, f.number, channels, f.body[3 * n:]


# --- the Bratiški, on the glove's and the sock's board (rubaska/SOFTWARE.md, the Bratiški) --------

BRATISKI, BRATISKA_IMUS = 4, 4     # four on the board, one a finger; four IMUs each, two a bus
BRATISKA_STEP_LEN = 52             # his step to Staršaja: 1 + 1 + 4 × 12 + 2


def bratiska_step(step: int, imus: list[bytes | None]) -> bytes:
    """A Bratiška's step on his UART to Staršaja, 52 B: a bit for each of his four IMUs that
    answers in bits 3-0 of byte 0, the step's number mod 256, the four IMUs' 12 B, zeros for one
    that does not answer, and the CRC-16. Nothing says which Bratiška: the UART does."""
    if len(imus) != BRATISKA_IMUS:
        raise ValueError("four IMUs")
    if any(i is not None and len(i) != IMU_STEP_LEN for i in imus):
        raise ValueError("12 B an IMU")
    present = sum(1 << n for n, i in enumerate(imus) if i is not None)
    steps = b"".join(i or bytes(IMU_STEP_LEN) for i in imus)
    return seal(bytes([present, step & 0xFF]) + steps)


def parse_bratiska_step(b: bytes) -> tuple[int, list[bytes | None]]:
    """The step's number and the four IMUs' steps, None for one not answering; ValueError for a
    wrong length or CRC, which Staršaja takes as a step missing."""
    if len(b) != BRATISKA_STEP_LEN:
        raise ValueError("not 52 B")
    if struct.unpack_from("<H", b, BRATISKA_STEP_LEN - 2)[0] != crc16(b[:-2]):
        raise ValueError("bad CRC")
    present = b[0] & 0x0F
    imus = [b[2 + 12 * n:14 + 12 * n] if present >> n & 1 else None for n in range(BRATISKA_IMUS)]
    return b[1], imus


def end_steps(own: list[bytes], links: list[bytes | None],
              fitted: tuple[int, ...] = (4, 4, 4, 4)) -> list[bytes]:
    """Staršaja's IMU steps for her frames of data, in her table's order: her own IMUs' first,
    then each Bratiška's as his step brought them, as many of his four as her table lists; a step
    missing or failing its CRC, and an IMU that does not answer, give zeros."""
    if len(links) != len(fitted) or len(links) > BRATISKI:
        raise ValueError("a step a Bratiška, four at most")
    out = list(own)
    for b, n in zip(links, fitted):
        imus: list[bytes | None] = [None] * BRATISKA_IMUS
        if b is not None:
            try:
                _, imus = parse_bratiska_step(b)
            except ValueError:
                pass
        out += [i or bytes(IMU_STEP_LEN) for i in imus[:n]]
    return out


NATASA_MISA, NATASA_WARNING, NATASA_MOTOR, NATASA_TRIAL, NATASA_FAILED = 1, 2, 4, 8, 16


def natasa_data(cycle: int, buttons: int, state: int) -> bytes:
    """Hers, once every PERIOD cycles, in cycle 15: the buttons, a bit each, and her state."""
    return Frame(NATASA, K_DATA, cycle, struct.pack("<HB", buttons & 0xFFFF, state & 0xFF)).pack()


def parse_natasa_data(frame: bytes) -> tuple[int, int, int]:
    """The cycle's 16 bits, the buttons and the state."""
    f = Frame.unpack(frame)
    if f.unit != NATASA or f.kind != K_DATA:
        raise ValueError("not Nataša's data")
    buttons, state = struct.unpack_from("<HB", f.body)
    return f.number, buttons, state


# --- the diagnostics ------------------------------------------------------------------------------

DIAGNOSTICS_CYCLE = 31     # every unit's in the cycle whose number mod PERIOD is 31
LINE8_DATA_CYCLE = 15      # Nataša's frame of data, half a round from it
IMU_TEMPS = 6              # IMU temperatures a diagnostics frame
TEMPS_AT = 15              # byte 19 of the frame: the IMUs' temperatures, six at most
RESET_AT = 27              # byte 31 of the frame: the last reset's cause (porjadok, Watchdogs)
(RESET_SUPPLY, RESET_IWDG, RESET_FAULT, RESET_ECC, RESET_CLOCK, RESET_ASKED,
 RESET_PIN) = range(7)


def mv_byte(mv: int) -> int:
    """The lowest 3.3 V in 10 mV above 2.00 V; 4.55 V and more read 255."""
    return max(0, min(255, (mv - 2000) // 10))


def byte_mv(b: int) -> int:
    return 2000 + 10 * b


def temp_c(out_temp: int) -> float:
    """An IMU's OUT_TEMP in °C: the LSM6DSV16X's 256 LSB/°C, 0 at 25 °C (DS13510 Rev 4, table 6
    and its note 3)."""
    return out_temp / 256 + 25


def which_imus(cycle: int, imus: int) -> range:
    """The six IMUs whose temperatures this diagnostics carries, by turns by the frame's number:
    the glove's 22 in four diagnostics. Six from the first in turn is the code's choice."""
    turns = max(1, -(-imus // IMU_TEMPS))
    first = IMU_TEMPS * ((cycle // PERIOD) % turns)
    return range(first, min(first + IMU_TEMPS, imus))


def on_skin(loff_stat: list[int]) -> int:
    """One chip's LOFF_STATP or LOFF_STATN over 32 samples turned over: 1 on the skin in every
    one of them."""
    off = 0
    for s in loff_stat:
        off |= s
    return ~off & 0xFF


def skin_word(first: int, second: int = 0xFF) -> int:
    """The 16 electrodes' word of a module: the first chip's eight in the low byte, the second's
    in the high one, ones for a chip not fitted."""
    return first & 0xFF | (second & 0xFF) << 8


@dataclass
class Diagnostics:
    """Every unit's frame 0x21, once every 32 cycles: its bits are 1 while all is well."""
    unit: int
    cycle: int
    alive: int = 0xFFFFFFFF        # a bit a chip in the order of the unit's table, unused 1
    clean: int = 0xFFFFFFFF        # without an error over the 32 samples, the same bits
    p_on: int = 0xFFFF             # P1-P16 on the skin, the second chip's eight in the high byte
    n_on: int = 0xFFFF             # N1-N16
    flags: int = 0xFF              # bit 0 the bias electrode on the skin, 1 Mamka's frames clean
    temp_c: int = 0                # the processor's, signed
    low_mv: int = 3300             # the lowest 3.3 V since the last
    imu_temps: list[int] = field(default_factory=list)   # OUT_TEMP, six at most
    reset: int = RESET_SUPPLY      # the last reset's cause, 0-6

    def pack(self) -> bytes:
        if len(self.imu_temps) > IMU_TEMPS:
            raise ValueError("six IMU temperatures at most")
        body = struct.pack("<IIHHBbB", self.alive, self.clean, self.p_on, self.n_on, self.flags,
                           self.temp_c, mv_byte(self.low_mv))
        body += b"".join(struct.pack("<h", t) for t in self.imu_temps)
        body = body.ljust(RESET_AT, b"\0") + bytes([self.reset])
        return Frame(self.unit, K_DIAGNOSTICS, self.cycle, body).pack()

    @classmethod
    def unpack(cls, frame: bytes, imus: int = IMU_TEMPS) -> "Diagnostics":
        """`imus`: how many temperatures this one carries, which the unit's table tells."""
        f = Frame.unpack(frame)
        if f.kind != K_DIAGNOSTICS:
            raise ValueError("not diagnostics")
        alive, clean, p, n, flags, t, mv = struct.unpack_from("<IIHHBbB", f.body)
        temps = [struct.unpack_from("<h", f.body, TEMPS_AT + 2 * i)[0] for i in range(min(imus, 6))]
        return cls(f.unit, f.number, alive, clean, p, n, flags, t, byte_mv(mv), temps,
                   f.body[RESET_AT])

    @property
    def all_well(self) -> bool:
        """The scan for all ones: a zero is looked into only when found."""
        return ((self.alive & self.clean) == 0xFFFFFFFF and (self.p_on & self.n_on) == 0xFFFF
                and (self.flags & 0x03) == 0x03)


def chip_bits(chips: int, ok: list[bool]) -> int:
    """The alive or clean word: a bit a chip, 1 for well, the unused bits 1."""
    word = 0xFFFFFFFF
    for i in range(chips):
        if not ok[i]:
            word &= ~(1 << i)
    return word


# --- the registers of chip 0x00 ------------------------------------------------------------------

REG_BIAS, REG_IMU_MODE = 0x00, 0x01            # the settings, 0x00-0x3F
REG_LED = 0x02                                 # a module's status LED, 1 blinking; not kept
REG_SHIELD = 0x03                              # the strip's ground layer: 0 on ground, 1 driven
REG_TABLE = 0x40                               # the unit's table, read only, 0x40-0x7F
REG_FIRMWARE = 0x80                            # the firmware's update, 0x80-0xBF
REG_EVENTS = 0xC0                              # Mamka's, 0xC0-0xFF

KIND_EMG, KIND_END, KIND_NATASA, KIND_MISA = range(1, 5)   # 2 the glove and the sock


def blink(unit: int, on: bool, number: int = 0) -> bytes:
    """The map's application finding a module: its status LED blinking, or back to the
    firmware's own."""
    return write(unit, CHIP_UNIT, REG_LED, int(on), number)

FW_MODULE, FW_GLOVE, FW_BRATISKA, FW_NATASA, FW_MISA, FW_P1, FW_P2 = range(1, 8)
PART_ADS1298, PART_LSM6DSV16X, PART_SOUND, PART_MOTORS, PART_SPHERE, PART_BRATISKA = range(1, 7)


@dataclass
class UnitTable:
    """From register 0x40 of chip 0x00, read only: the length, the unit's kind, the firmware's
    kind and version, the UID, the chips, 2 B each, their number and their part."""
    kind: int
    firmware: int
    version: int
    uid: bytes
    chips: list[tuple[int, int]] = field(default_factory=list)

    def pack(self) -> bytes:
        if len(self.uid) != UID_LEN:
            raise ValueError("the UID is 12 B")
        body = struct.pack("<BBH", self.kind, self.firmware, self.version) + self.uid
        body += bytes([len(self.chips)]) + b"".join(bytes([n, p]) for n, p in self.chips)
        return bytes([1 + len(body)]) + body

    @classmethod
    def unpack(cls, b: bytes) -> "UnitTable":
        if len(b) < 18 or len(b) < b[0]:
            raise ValueError("a table too short")
        kind, fw, ver = struct.unpack_from("<BBH", b, 1)
        chips = [(b[18 + 2 * i], b[19 + 2 * i]) for i in range(b[17])]
        return cls(kind, fw, ver, bytes(b[5:17]), chips)

    def reads(self) -> list[tuple[int, int]]:
        """The reads that take it, (the first register, the count), 25 B at a time."""
        n = len(self.pack())
        return [(REG_TABLE + i, min(VALUES, n - i)) for i in range(0, n, VALUES)]


def module_table(uid: bytes, imus: int = 4, version: int = 0x0100, imu: int = PART_LSM6DSV16X,
                 ads: tuple[int, ...] = (PART_ADS1298, PART_ADS1298)) -> UnitTable:
    """A sensing module's: its first ADS1298 at 0x01, a second at 0x06, its IMUs from 0x10: two
    ADS1298 on the body and the head, one on the neck."""
    chips = [(CHIP_ADS, ads[0])] + ([(CHIP_ADS2, ads[1])] if len(ads) > 1 else [])
    chips += [(CHIP_IMU + i, imu) for i in range(imus)]
    return UnitTable(KIND_EMG, FW_MODULE, version, uid, chips)


HAND_IMUS, FOOT_IMUS = 20, 8       # the glove's places, Staršaja's four and the Bratiški's; a sock's to start
END_IMUS = 20                      # the board's places: two I3C buses of two on Staršaja and on each Bratiška


def end_table(uid: bytes, imus: int = HAND_IMUS, bratiski: int = BRATISKI, version: int = 0x0100,
              imu: int = PART_LSM6DSV16X) -> UnitTable:
    """The glove's, and the sock's, the same board: its ADS1298 at 0x01, its Bratiški from 0x07,
    its IMUs from 0x10 in the frame's order, Staršaja's own first; 0x10-0x23 for the glove's 20."""
    if not 0 <= bratiski <= BRATISKI or not 1 <= imus <= END_IMUS:
        raise ValueError("up to four Bratiški and 20 IMUs")
    chips = [(CHIP_ADS, PART_ADS1298)]
    chips += [(CHIP_BRATISKA + i, PART_BRATISKA) for i in range(bratiski)]
    chips += [(CHIP_IMU + i, imu) for i in range(imus)]
    return UnitTable(KIND_END, FW_GLOVE, version, uid, chips)


# --- into Baťa: the places on the SPIs ------------------------------------------------------------

PLACE = FRAME_LEN      # a place of 34 B: the four places more, and every place in the service mode
EXTRA = 4              # places a cycle for the diagnostics, the answers and Mamka's own


def has_place(kind: int) -> bool:
    """Whether a unit of this kind has a place of data: all but Míša, who sends no frame of data,
    his sphere going in the four places."""
    return kind != KIND_MISA


def place_len(kind: int, ads: int = 0) -> int:
    """A unit's place of data a cycle, by its kind: 58 B for a module of two ADS1298, its frame
    0x24, and for the glove and the sock, 0x25; 34 B for every other unit with a place, none for
    Míša."""
    if not has_place(kind):
        return 0
    return DATA2_LEN if ads == 2 or kind == KIND_END else PLACE


def places_of(frame: bytes) -> int:
    """How many places of 34 B a frame takes: one for 34 B or 8 B, 16 for a firmware block."""
    return -(-len(frame) // PLACE)


def places(frames: list[bytes | None], sizes: list[int] = ()) -> bytes:
    """Frames as they came, each from its place's start, zeros after a short one; None an empty
    place. `sizes` gives the data places' lengths, 58 or 34 B by the unit's kind; a frame beyond
    them takes places of 34 B, a firmware block 16 of them."""
    out = bytearray()
    for i, f in enumerate(frames):
        f = f or b""
        n = sizes[i] if i < len(sizes) else PLACE * max(1, places_of(f))
        if len(f) > n:
            raise ValueError("a frame longer than its place")
        out += f + bytes(n - len(f))
    return bytes(out)


def parse_places(stream: bytes, sizes: list[int] = ()) -> list[bytes | None]:
    """A transfer's places, the data places by `sizes` and the rest of 34 B: a frame by its
    kind's length, None for an empty one (kind 0). A tail shorter than a place, a stripe's
    padding, is no place."""
    out, pos, i = [], 0, 0
    while True:
        n = sizes[i] if i < len(sizes) else PLACE
        if pos + n > len(stream):
            break
        kind = stream[pos + 1]
        if kind == 0:
            out.append(None)
        else:
            if kind not in LENGTH:
                raise ValueError(f"no kind 0x{kind:02X}")
            m = LENGTH[kind]
            if i >= len(sizes):
                n = PLACE * -(-m // PLACE)
            elif m > n:
                raise ValueError("a frame longer than its place")
            if pos + m > len(stream):
                raise ValueError("a frame cut short")
            out.append(bytes(stream[pos:pos + m]))
        pos += n
        i += 1
    return out


def cycle_transfer(data: list[bytes | None], sizes: list[int], extra: list[bytes] = ()) -> bytes:
    """A processor's cycle while measuring: the frames of data in her table's order, by line
    and on each line by slot, each in a place of its unit's size, then the four places of 34 B
    more."""
    if len(data) != len(sizes):
        raise ValueError("a size for every place of data")
    if len(extra) > EXTRA:
        raise ValueError("four places more")
    return places(list(data) + list(extra) + [None] * (EXTRA - len(extra)), list(sizes))


def parse_cycle(stream: bytes, sizes: list[int]) -> tuple[list[bytes | None], list[bytes]]:
    """The data places of a processor, their sizes from her table, and the frames of the four."""
    p = parse_places(stream, list(sizes))
    units = len(sizes)
    if len(p) < units + EXTRA:
        raise ValueError("too few places")
    return p[:units], [f for f in p[units:units + EXTRA] if f is not None]


def stripe(stream: bytes) -> tuple[bytes, bytes]:
    """Processor 2's transfer in words of 4 B over her two SPIs, bytes 0-3 on SPI0_M2, 4-7 on
    SPI3_M0 and so on; padded with zeros to 8 B so that both carry the same share (378 B to 384)."""
    stream = stream + bytes(-len(stream) % 8)
    words = [stream[i:i + 4] for i in range(0, len(stream), 4)]
    return b"".join(words[0::2]), b"".join(words[1::2])


def join(a: bytes, b: bytes) -> bytes:
    if len(a) != len(b) or len(a) % 4:
        raise ValueError("both SPIs carry the same share")
    return b"".join(a[i:i + 4] + b[i:i + 4] for i in range(0, len(a), 4))


# --- the firmware ---------------------------------------------------------------------------------

FW_BLOCK = 512
FW_MAP_REG, FW_MAP_LEN = 0x90, 32      # a bit a block, 256 blocks a window: 128 KB
FW_MAP_WINDOW = 0x89                   # which 256 blocks the map shows
FW_MAX_BLOCKS = 1024                   # the largest bank, Mamka's 512 KB, in four windows
FW_BEGIN, FW_CHECK, FW_CONFIRM, FW_ABORT = 1, 2, 3, 4
FW_IDLE, FW_ERASING, FW_RECEIVING, FW_CRC_WRONG, FW_ON_TRIAL, FW_FAILED = range(6)
FW_PROGRAMMING = 6     # the glove's Staršaja writing her Bratiški through ST's bootloader


@dataclass
class FirmwareFrame:
    """519 B: the unit's number (0 every unit), 0x30, the firmware's kind it is for, the block's
    number, 512 B of the image, CRC-16."""
    unit: int
    firmware: int
    block: int
    data: bytes

    def pack(self) -> bytes:
        if len(self.data) > FW_BLOCK:
            raise ValueError("512 B a block")
        head = struct.pack("<BBBH", self.unit & 0xFF, K_FIRMWARE, self.firmware, self.block)
        return seal(head + self.data.ljust(FW_BLOCK, b"\0"))

    @classmethod
    def unpack(cls, frame: bytes) -> "FirmwareFrame":
        b = check(frame)
        if b[1] != K_FIRMWARE:
            raise ValueError("not a firmware block")
        unit, _, kind, block = struct.unpack_from("<BBBH", b)
        return cls(unit, kind, block, b[5:5 + FW_BLOCK])


def image_with_crc(image: bytes) -> bytes:
    """The image as it goes out: its CRC-32 at its end, little-endian."""
    return image + struct.pack("<I", crc32(image))


def fw_frames(firmware: int, image: bytes) -> list[bytes]:
    """The image in blocks of 512 B to every unit; the last padded with 0xFF to a multiple of
    16 B for the flash, zeros after it filling the frame (0xFF is the code's choice)."""
    blocks = []
    for n, off in enumerate(range(0, len(image), FW_BLOCK)):
        chunk = image[off:off + FW_BLOCK]
        chunk += b"\xFF" * (-len(chunk) % 16)
        blocks.append(FirmwareFrame(EVERY, firmware, n, chunk).pack())
    if len(blocks) > FW_MAX_BLOCKS:
        raise ValueError("an image is at most a bank, 512 KB on Mamka's")
    return blocks


def fw_windows(blocks: int) -> int:
    """How many windows of the map an image of `blocks` takes, 256 blocks each."""
    return -(-blocks // (8 * FW_MAP_LEN))


def fw_window(unit: int, window: int, number: int = 0) -> bytes:
    """Which 256 blocks the unit's map at 0x90 shows next: one byte written at 0x89."""
    return write(unit, CHIP_UNIT, FW_MAP_WINDOW, window, number)


def fw_begin(firmware: int, image: bytes, version: int, number: int = 0) -> bytes:
    """*Begin* to every unit, chip 0x00 from 0x80: the command, the kind, the length, the
    version."""
    values = struct.pack("<BBIH", FW_BEGIN, firmware, len(image), version)
    return write_many(EVERY, CHIP_UNIT, REG_FIRMWARE, values, number)


def fw_command(unit: int, what: int, number: int = 0) -> bytes:
    return write(unit, CHIP_UNIT, REG_FIRMWARE, what, number)


def missing(block_map: bytes, blocks: int, window: int = 0) -> list[int]:
    """The blocks a unit lacks in one window, from its map of 32 B, a bit a block."""
    first = window * 8 * FW_MAP_LEN
    return [n for n in range(first, min(blocks, first + 8 * FW_MAP_LEN))
            if not block_map[(n - first) // 8] >> ((n - first) % 8) & 1]


# --- line 8: the sound, Míša's sphere, the motors ------------------------------------------------

SOUND_SAMPLES = 48     # stereo samples a packet: 1 ms at 48 kHz


def sound(kind: int, number: int, samples: list[tuple[int, int]]) -> bytes:
    """A packet of 198 B, 0x22 down for the headphones or 0x23 up from the microphones: 48 stereo
    samples of 16 bits, left then right."""
    if kind not in (K_SOUND_DOWN, K_SOUND_UP) or len(samples) != SOUND_SAMPLES:
        raise ValueError("0x22 or 0x23, 48 stereo samples")
    pcm = b"".join(struct.pack("<hh", lft, rgt) for lft, rgt in samples)
    return Frame(NATASA, kind, number, pcm).pack()


def parse_sound(frame: bytes) -> tuple[int, int, list[tuple[int, int]]]:
    f = Frame.unpack(frame)
    if f.kind not in (K_SOUND_DOWN, K_SOUND_UP):
        raise ValueError("not sound")
    return f.kind, f.number, [struct.unpack_from("<hh", f.body, 4 * i) for i in range(48)]


SPHERE_LEN, SPHERE_FIELDS, SPHERE_PIECE = 112, 36, 25
SRC_NONE, SRC_ULTRASOUND, SRC_RADAR, SRC_BOTH = range(4)    # the source's code, header and fields


def sphere(frame_no: int, status: int, turn: int, pitch: int,
           fields: list[tuple[int, int, int]]) -> bytes:
    """Míša's sphere: 4 B of header (the status's bits 0-1 the source's code), then the 36 fields
    of (distance u8, speed i8, the byte of the confidence, the source's code and the kind)."""
    if len(fields) != SPHERE_FIELDS:
        raise ValueError("36 fields")
    out = struct.pack("<BBbb", frame_no & 0xFF, status & 0xFF, turn, pitch)
    return out + b"".join(struct.pack("<BbB", d & 0xFF, s, c & 0xFF) for d, s, c in fields)


def sphere_answers(sph: bytes, cycle: int) -> list[bytes]:
    """The sphere as his chip 0x05, registers 0x00-0x6F, in five answers sent unasked, 25 B in
    each, all with the cycle's number at which it was done."""
    if len(sph) != SPHERE_LEN:
        raise ValueError("a sphere is 112 B")
    return [unasked(MISA, CHIP_SPHERE, off, sph[off:off + SPHERE_PIECE], cycle)
            for off in range(0, SPHERE_LEN, SPHERE_PIECE)]


class SphereAssembler:
    """Puts Míša's five answers together by their cycle's number."""

    def __init__(self) -> None:
        self.parts: dict[int, dict[int, bytes]] = {}
        self.spheres: list[tuple[int, bytes]] = []

    def feed(self, frame: bytes) -> None:
        r = Registers.unpack(frame)
        if r.unit != MISA or r.chip != CHIP_SPHERE:
            return
        got = self.parts.setdefault(r.number, {})
        got[r.reg] = r.values
        offsets = range(0, SPHERE_LEN, SPHERE_PIECE)
        if all(o in got for o in offsets):
            self.spheres.append((r.number, b"".join(got[o] for o in offsets)))
            del self.parts[r.number]


MOTOR_LEFT, MOTOR_RIGHT, MOTOR_FOREHEAD, MOTOR_NAPE = 0x00, 0x04, 0x08, 0x0C
MOTOR_SETTINGS, MOTOR_PATTERNS = 0x10, 0x20
REG_MICROPHONES = 0x00     # Nataša's sound chip: 0 off, as after a reset, 1 on


def microphones(on: bool, number: int = 0) -> bytes:
    """Baťa's `microphones.service` turning Nataša's microphones on or off: one byte written."""
    return write(NATASA, CHIP_SOUND, REG_MICROPHONES, int(on), number)


def motors(sets: dict[int, tuple[int, int, int, int]], number: int = 0) -> bytes:
    """One frame for several motors: register 0x00 + 4 × motor, (pattern, strength, repeats,
    pulse)."""
    first, last = min(sets), max(sets)
    regs = bytearray(last + 4 - first)
    for base, vals in sets.items():
        regs[base - first:base - first + 4] = bytes(vals)
    return write_many(NATASA, CHIP_MOTORS, first, bytes(regs), number)


def pulse(motor: int, length_10ms: int, number: int = 0) -> bytes:
    """One pulse now, for Nikita's beat: one byte written, in 8 B."""
    return write(NATASA, CHIP_MOTORS, motor + 3, length_10ms, number)


def pattern_define(n: int, steps: list[int], number: int = 0) -> bytes:
    """Patterns 8-15 at 0x20 + 8 × (n - 8), 8 B each: up to 8 steps, a step's length in 10 ms,
    on and off in turn from on, a 0 after the last."""
    if not 8 <= n <= 15 or not 1 <= len(steps) <= 8 or not all(1 <= s <= 255 for s in steps):
        raise ValueError("patterns 8-15, 1-8 steps of 1-255")
    vals = bytes(steps) + (b"\0" if len(steps) < 8 else b"")
    return write_many(NATASA, CHIP_MOTORS, MOTOR_PATTERNS + 8 * (n - 8), vals, number)


# --- Mamka's own registers ------------------------------------------------------------------------

EV_PRESSED, EV_RELEASED, EV_BUDILNIK, EV_BMS_ALARM, EV_WARNING_ON, EV_WARNING_OFF, \
    EV_SILENT = range(1, 8)
REG_POWER, REG_REASON, REG_FAN = 0x10, 0x11, 0x12      # processor 2's writes
REG_GPS, REG_UTC = 0xD0, 0xE0


def event(what: int, which: int, cycle: int, unit: int = P2) -> bytes:
    """An event, unasked from 0xC0: what, which, the cycle's number (u32)."""
    values = struct.pack("<BBI", what, which, cycle & 0xFFFFFFFF)
    return unasked(unit, CHIP_UNIT, REG_EVENTS, values, cycle)


def gps(lat: int, lon: int, height_m: int, fix: int, sats: int, cycle: int) -> bytes:
    """At a fix, unasked from 0xD0: the latitude and longitude (10⁻⁷ °), the height, the fix, the
    satellites."""
    return unasked(P2, CHIP_UNIT, REG_GPS, struct.pack("<iihBB", lat, lon, height_m, fix, sats),
                   cycle)


def utc(cycle: int, second: int) -> bytes:
    """At every PPS, unasked from 0xE0: the suit's cycle at which a UTC second began, and that
    second."""
    return unasked(P2, CHIP_UNIT, REG_UTC, struct.pack("<II", cycle & 0xFFFFFFFF, second), cycle)


def power(command: int, number: int = 0) -> bytes:
    """Processor 2's power command, register 0x10: 1 off in order, 2 the computers off, 3 the
    lines off and on, 4 Baťa halted, 5 running again."""
    return write(P2, CHIP_UNIT, REG_POWER, command, number)


@dataclass
class Battery:
    """Chip 0x04 of processor 2 from 0x00: the BMS's live block as she last read it, 23 B."""
    cells: tuple[int, int, int, int]
    pack_mv: int
    current_ma: int
    temps: tuple[int, int, int]
    alarms: int = 0
    soc: int = 0
    remaining_mah: int = 0

    def pack(self) -> bytes:
        return struct.pack("<4HHh3hHBH", *self.cells, self.pack_mv, self.current_ma, *self.temps,
                           self.alarms, self.soc, self.remaining_mah)

    @classmethod
    def unpack(cls, b: bytes) -> "Battery":
        v = struct.unpack_from("<4HHh3hHBH", b)
        return cls(tuple(v[0:4]), v[4], v[5], tuple(v[6:9]), v[9], v[10], v[11])


BATTERY_LEN = struct.calcsize("<4HHh3hHBH")
