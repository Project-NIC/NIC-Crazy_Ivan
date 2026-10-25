"""The suit side: the limbs on lines 1-4 and processor 1, the head and the trunk on lines 5-7 and
Nataša and Míša on line 8, all on processor 2; Mamka passing the frames to Baťa as they came."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from ci import stp

ADS_SPS = 3840
LSB_PER_UV = 1 / 0.04470        # gain 12, ±375 mV over 24 bits: 44.70 nV a step
MISA_EVERY = 384                # cycles between Míša's spheres, 10 a second
P1_LINES = range(1, 5)          # the arms and the legs, on processor 1

# where each module sits, by line and slot, with its IMUs (Bogatyr), in the order a smaller suit
# takes them; an arm's line is its shoulder, upper arm, forearm and glove, a leg's its hip, thigh
# and calf
PLACES = [(1, 2, "upper arm L", 4), (1, 3, "forearm L", 4), (2, 2, "upper arm R", 4),
          (2, 3, "forearm R", 4), (3, 2, "thigh L", 4), (3, 3, "calf L", 4), (4, 2, "thigh R", 4),
          (4, 3, "calf R", 4), (6, 1, "chest and abdomen", 1), (7, 2, "lower back", 3),
          (7, 1, "neck and upper back", 2), (1, 1, "shoulder L", 3), (2, 1, "shoulder R", 3),
          (3, 1, "hip L", 1), (4, 1, "hip R", 1), (5, 1, "head", 2)]
TRUNK = ("chest and abdomen", "lower back", "neck and upper back")   # where the ECG shows


def imu_steps(pose: float, n: int) -> list[bytes]:
    """The IMUs' steps: a slow swing about one axis, in the raw scales (±2000 °/s and ±16 g over
    16 bits, 1 g = 2048), the turn divided by the step."""
    g = int(math.cos(pose) * 60.0 * 32768 / 2000)       # the arm swinging, ±60 °/s at most
    out = []
    for i in range(n):
        tilt = pose * (0.2 + 0.05 * i)
        out.append(stp.imu_step((g, 0, g // 2),
                                (int(2048 * math.sin(tilt)), 0, int(2048 * math.cos(tilt)))))
    return out


@dataclass
class Unit:
    """A unit on a line: its place, its number, its UID."""
    line: int
    slot: int
    name: str = ""
    number: int = 0
    imus: int = 0
    rng: random.Random = field(default_factory=lambda: random.Random(1))
    uid: bytes = b""
    kind: int = 0

    def __post_init__(self) -> None:
        if not self.uid:
            self.uid = bytes(self.rng.getrandbits(8) for _ in range(stp.UID_LEN))

    @property
    def processor(self) -> int:
        return 1 if self.line in P1_LINES else 2

    @property
    def chips(self) -> int:
        return self.imus

    def diagnostics(self, cycle: int, temp_c: int = 32) -> bytes:
        temps = [int((26.0 - 25) * 132.48)] * len(stp.which_imus(cycle, self.imus))
        alive = stp.chip_bits(self.chips, [True] * self.chips)
        return stp.Diagnostics(self.number, cycle, alive, alive, temp_c=temp_c, low_mv=3270,
                               imu_temps=temps).pack()


@dataclass
class Module(Unit):
    """A sensing module: an ADS1299 and its IMUs."""
    trunk: bool = False         # the ECG shows strongly on the trunk's modules
    kind: int = stp.KIND_EMG

    @property
    def chips(self) -> int:
        return 1 + self.imus

    def channels(self, cycle: int, pose: float) -> list[int]:
        """Eight EMG-like channels: noise, a little muscle tone that follows the pose, the ECG."""
        t = cycle / ADS_SPS
        out = []
        for _ in range(8):
            v = self.rng.gauss(0, 1.0) * LSB_PER_UV                                  # ~1 µVrms
            v += 60 * LSB_PER_UV * abs(math.sin(pose)) * self.rng.gauss(0, 1)        # EMG, effort
            if self.trunk and (t * 1.2) % 1.0 < 0.03:                                # 72 a minute
                v += 1000 * LSB_PER_UV * math.sin((t * 1.2) % 1.0 / 0.03 * math.pi)  # R, ~1 mV
            out.append(int(max(-8388608, min(8388607, v))))
        return out

    def frame(self, cycle: int, pose: float, steps: list[bytes]) -> bytes:
        imu = stp.imu_bytes(cycle, steps[:self.imus], stp.MODULE_IMU)
        return stp.module_data(self.number, cycle, self.channels(cycle, pose), imu)


@dataclass
class Glove(Unit):
    """The glove, Vešč, a unit of its own in its arm's fourth slot: 20 IMUs on five Bratiški."""
    imus: int = 20
    kind: int = stp.KIND_IMU

    def frame(self, cycle: int, pose: float, steps: list[bytes]) -> bytes:
        return stp.glove_data(self.number, cycle, stp.imu_bytes(cycle, steps[:self.imus],
                                                                stp.GLOVE_IMU))


@dataclass
class Natasa(Unit):
    """Line 8's first slot: her frame of data in cycle 15 of 32, her diagnostics in 31."""
    line: int = 8
    slot: int = 1
    name: str = "Nataša"
    number: int = stp.NATASA
    kind: int = stp.KIND_NATASA
    buttons: int = 0
    misa: bool = True

    def frame(self, cycle: int, pose: float, steps: list[bytes]) -> bytes | None:
        if cycle % stp.STEP != stp.LINE8_DATA_CYCLE:
            return None
        return stp.natasa_data(cycle, self.buttons, stp.NATASA_MISA if self.misa else 0)


@dataclass
class Misa(Unit):
    """Line 8's second slot, his own: the sphere after every radar frame. What his frame of data
    carries is not set; here it is zeros."""
    line: int = 8
    slot: int = 2
    name: str = "Míša"
    number: int = stp.MISA
    kind: int = stp.KIND_MISA
    imus: int = 1
    sphere_no: int = 0

    def frame(self, cycle: int, pose: float, steps: list[bytes]) -> bytes | None:
        if cycle % stp.STEP != stp.LINE8_DATA_CYCLE:
            return None
        return stp.Frame(stp.MISA, stp.K_DATA, cycle).pack()

    def sphere(self) -> bytes:
        self.sphere_no += 1
        rows = {0: (255, 0, 0x1F), 1: None, 2: (120, 0, 0x5F)}
        fields = [rows[row] or (40 + 10 * col, 0, 0x1F) for row in range(3) for col in range(12)]
        return stp.sphere(self.sphere_no, 0x0F, 0, 0, fields)


@dataclass
class Suit:
    """Up to 16 modules and the gloves on lines 1-7 by the body's pieces, Nataša and Míša on line
    8, Mamka between them and Baťa: processor 1 the limbs over SPI1, processor 2 the rest over two
    slower SPIs, in places of 34 B."""
    units: list[Unit]                  # the map: by line and on each line by slot
    bad_frame_rate: float = 0.0        # how often a frame reaches Mamka with a bad CRC
    rng: random.Random = field(default_factory=lambda: random.Random(3))
    cycle_no: int = 0
    phase: float = 0.0
    steps: list[bytes] = field(default_factory=lambda: imu_steps(0.0, 24))
    queue: dict = field(default_factory=lambda: {1: [], 2: []})    # frames for the four places
    p1: list[bytes] = field(default_factory=list)                   # processor 1's, on SPI1
    p2: list[tuple[bytes, bytes]] = field(default_factory=list)     # processor 2's, on her two
    last_buttons: int = 0
    stats: dict = field(default_factory=lambda: {"frames": 0, "bad": 0, "queued": 0})

    @classmethod
    def standard(cls, n_modules: int = 16, line8: bool = True, gloves: bool = True,
                 **kw) -> "Suit":
        units: list[Unit] = []
        for i, (line, slot, name, imus) in enumerate(PLACES[:n_modules]):
            units.append(Module(line, slot, name, imus=imus, rng=random.Random(100 + i),
                                trunk=name in TRUNK))
        if gloves:
            for m in [u for u in units if u.name.startswith("forearm")]:
                m.imus = 2                          # the hand's two are the glove's
                units.append(Glove(m.line, 4, "glove " + m.name[-1], rng=random.Random(m.line)))
        if line8:
            units += [Natasa(rng=random.Random(81)), Misa(rng=random.Random(82))]
        units.sort(key=lambda u: (u.line, u.slot))
        for n, u in enumerate([u for u in units if u.line < 8], 1):
            u.number = n                            # *assign*'s, by the map's order here
        return cls(units, **kw)

    def of(self, processor: int) -> list[Unit]:
        return [u for u in self.units if u.processor == processor]

    def unit(self, name: str) -> Unit:
        return next(u for u in self.units if u.name == name)

    def arrive(self, frame: bytes | None) -> bytes | None:
        """A frame as it reaches Mamka: perhaps damaged, then dropped by its CRC."""
        if frame is None:
            return None
        self.stats["frames"] += 1
        if self.rng.random() < self.bad_frame_rate:
            self.stats["bad"] += 1
            bad = bytearray(frame)
            bad[self.rng.randrange(len(frame))] ^= 1 << self.rng.randrange(8)
            frame = bytes(bad)
        try:
            return stp.check(frame)
        except ValueError:
            return None

    def cycle(self) -> tuple[bytes, tuple[bytes, bytes]]:
        """One cycle: every unit's frame in its slot, the diagnostics in cycle 31 of 32, line 8's
        frames, each processor's transfer: processor 1's on SPI1, processor 2's striped."""
        s = self.cycle_no
        if s % stp.STEP == 0:
            self.phase = 2 * math.pi * 0.5 * s / ADS_SPS     # a swing twice a second
            self.steps = imu_steps(self.phase, 24)
        transfers = {}
        for proc in (1, 2):
            data = [self.arrive(u.frame(s, self.phase, self.steps)) for u in self.of(proc)]
            if s % stp.STEP == stp.DIAGNOSTICS_CYCLE:
                for u in self.of(proc):
                    self.put(proc, self.arrive(u.diagnostics(s)))
            if proc == 2:
                self.line8(s, data)
            extra, self.queue[proc] = self.queue[proc][:stp.EXTRA], self.queue[proc][stp.EXTRA:]
            transfers[proc] = stp.cycle_transfer(data, extra)
        self.p1.append(transfers[1])
        share = stp.stripe(transfers[2])
        self.p2.append(share)
        self.cycle_no += 1
        return transfers[1], share

    def put(self, proc: int, frame: bytes | None) -> None:
        if frame is not None:
            self.queue[proc].append(frame)
            self.stats["queued"] += 1

    def line8(self, s: int, data: list[bytes | None]) -> None:
        """Processor 2: an event for each change of Nataša's buttons, Míša's sphere as it came."""
        line8 = {u.number: (u, f) for u, f in zip(self.of(2), data) if u.line == 8}
        _, nf = line8.get(stp.NATASA, (None, None))
        if nf is not None:
            _, buttons, _ = stp.parse_natasa_data(nf)
            changed = buttons ^ self.last_buttons
            for bit in range(16):
                if changed >> bit & 1:
                    what = stp.EV_PRESSED if buttons >> bit & 1 else stp.EV_RELEASED
                    self.put(2, stp.event(what, bit, s))
            self.last_buttons = buttons
        misa, _ = line8.get(stp.MISA, (None, None))
        if misa is not None and s % MISA_EVERY == 0:
            for piece in stp.sphere_answers(misa.sphere(), s):
                self.put(2, self.arrive(piece))
