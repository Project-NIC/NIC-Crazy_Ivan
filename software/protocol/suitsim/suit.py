"""The suit side: blocks, Nataša and Mamka's processor 1 and 2, one cycle at a time."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from ci import stp

ADS_SPS = 3840
STEP = 32                       # ADS samples per IMU step (120 Hz)
LSB_PER_UV = 1 / 0.02235        # gain 24, ±187.5 mV over 24 bits: 22.35 nV a step


@dataclass
class Block:
    """One sensing module: its address on its line, its signals and its last frames."""
    line: int                  # 1–4
    slot: int                  # 1–4
    firmware: int = 0x0100
    glove: bool = False
    foot: bool = False
    trunk: bool = False        # the ECG shows strongly on the trunk's modules
    bias: bool = False
    rng: random.Random = field(default_factory=lambda: random.Random(1))
    history: dict = field(default_factory=dict)   # sample -> frame bytes, the last 16

    @property
    def addr(self) -> int:
        return self.slot

    def channels(self, sample: int, pose: float) -> list[int]:
        """Eight EMG-like channels: noise, a little muscle tone that follows the pose, the ECG."""
        t = sample / ADS_SPS
        out = []
        for ch in range(8):
            v = self.rng.gauss(0, 1.0) * LSB_PER_UV                       # ~1 µVrms of noise
            v += 60 * LSB_PER_UV * abs(math.sin(pose)) * self.rng.gauss(0, 1)  # EMG, bursty with effort
            if self.trunk:
                beat = (t * 1.2) % 1.0                                    # 72 beats a minute
                if beat < 0.03:
                    v += 1000 * LSB_PER_UV * math.sin(beat / 0.03 * math.pi)   # the R wave, ~1 mV
            out.append(int(max(-8388608, min(8388607, v))))
        return out

    def rotation(self, sample: int, temp_01c: int = 320) -> bytes:
        """The 4 B at position sample % 32: the state, counters, temperatures, the ADS registers."""
        p = sample % stp.ROTATION
        state = 0x01 | (0x02 if self.glove or self.foot else 0) | 0x0C
        content = {
            0: bytes([state]) + self.firmware.to_bytes(2, "little") + b"\0",
            1: bytes(4),
            2: temp_01c.to_bytes(2, "little") + (3300).to_bytes(2, "little"),
            9: b"\x01\x19\x01\x19", 10: b"\x01\x19\x01\x19",
        }
        regs = [0x3E, 0xD2, 0xC0, 0xEE if self.bias else 0xE8, 0x00] + [0x60] * 7 + [0x67 if self.bias else 0x60]
        regs += [0x7F if self.bias else 0, 0x7F if self.bias else 0, 0x7F if self.bias else 0xFF,
                 0x7F if self.bias else 0xFF, 0, 0, 0, 0x0F, 0, 0, 0x02]
        for i in range(6):
            content[3 + i] = bytes(regs[4 * i:4 * i + 4])
        return content.get(p, bytes(4))

    def imu_bytes(self, sample: int, steps: list[bytes]) -> bytes:
        """One byte per IMU of the current step; with a foot, its IMUs ride at positions 12–23."""
        p = sample % stp.ROTATION
        n = 8 if self.foot else 4
        out = bytearray(4)
        for i in range(4):
            if p < 12:
                out[i] = steps[i][p]
            elif self.foot and p < 24:
                out[i] = steps[4 + i][p - 12]
        return bytes(out)

    def frame(self, sample: int, pose: float, steps: list[bytes]) -> bytes:
        f = stp.BlockFrame(block=self.slot, sample=sample & 0xFFFF, channels=self.channels(sample, pose),
                           rotation=self.rotation(sample), imu=self.imu_bytes(sample, steps))
        b = f.pack()
        self.history[sample] = b
        for old in [s for s in self.history if s < sample - 16]:
            del self.history[old]
        return b


def imu_steps(sample: int, pose: float, swing: float, n: int = 8) -> list[bytes]:
    """The IMUs' steps for the step that begins at `sample`: a slow swing about one axis.

    The turn per step in the gyro's raw scale (±2000 °/s over 16 bits, divided by the step), the
    mean force with gravity on z (±16 g over 16 bits: 1 g = 2048).
    """
    rate_dps = swing * math.cos(pose) * 60.0           # the arm swinging, ±60 °/s at most
    g = int(rate_dps * 32768 / 2000)
    out = []
    for i in range(n):
        tilt = pose * (0.2 + 0.1 * i)
        ax, az = int(2048 * math.sin(tilt)), int(2048 * math.cos(tilt))
        out.append(stp.imu_step((g, 0, g // 2), (ax, 0, az)))
    return out


@dataclass
class Natasa:
    buttons: int = 0
    misa: bool = True
    sphere_no: int = 0
    rng: random.Random = field(default_factory=lambda: random.Random(2))

    def sphere(self) -> bytes:
        fields = []
        for col in range(12):
            for row in range(3):
                d = 255 if row == 0 else (40 + 10 * col if row == 1 else 120)
                fields.append((d, 0, 0x0F | (1 << 4) | (0 << 6) if row != 2 else 0x0F | (1 << 4) | (1 << 6)))
        # the fields are ordered row by row: up, middle, down
        up = [f for i, f in enumerate(fields) if i % 3 == 0]
        mid = [f for i, f in enumerate(fields) if i % 3 == 1]
        down = [f for i, f in enumerate(fields) if i % 3 == 2]
        return stp.sphere(self.sphere_no & 0xFF, 0x0F, 0, 0, up + mid + down)

    def frame(self, sample: int, mics: list[tuple[int, int]], sphere: bytes | None) -> bytes:
        p = sample % stp.NATASA_ROTATION
        if p < 14:
            rot = sphere[8 * p:8 * p + 8] if sphere else bytes(8)
        elif p == 14:
            rot = (0x0100).to_bytes(2, "little") + b"\0" + (330).to_bytes(2, "little") + (0 if sphere else 0xFFFF).to_bytes(2, "little") + b"\0"
        else:
            rot = bytes(8)
        state = 0x02 if sphere else 0
        return stp.NatasaFrame(sample=sample & 0xFFFF, state=state, buttons=self.buttons, rotation=rot, mics=mics).pack()


@dataclass
class Suit:
    """8 to 16 blocks on four lines, Nataša on the fifth, Mamka in between."""
    blocks: list[Block]
    natasa: Natasa | None = None
    bad_frame_rate: float = 0.0        # how often a frame reaches Mamka with a bad CRC
    repeat_fail_rate: float = 0.0      # how often the repeat is bad too
    rng: random.Random = field(default_factory=lambda: random.Random(3))
    sample: int = 0
    phase: float = 0.0
    steps: list[bytes] = field(default_factory=lambda: imu_steps(0, 0.0, 1.0))
    pending_repeat: dict = field(default_factory=dict)   # (line, slot) -> sample to repeat
    records: list[bytes] = field(default_factory=list)
    stats: dict = field(default_factory=lambda: {"frames": 0, "bad": 0, "repeated": 0, "missing": 0, "natasa": 0})
    mic_phase: float = 0.0

    @classmethod
    def standard(cls, n_blocks: int = 16, natasa: bool = True, **kw) -> "Suit":
        blocks = []
        for i in range(n_blocks):
            line, slot = i % 4 + 1, i // 4 + 1
            blocks.append(Block(line, slot, trunk=(i in (0, 1, 2, 3)), bias=(i == 0),
                                glove=(line in (1, 2) and slot == 2 and n_blocks >= 8),
                                foot=(line in (3, 4) and slot == 2 and n_blocks >= 8),
                                rng=random.Random(100 + i)))
        return cls(blocks, Natasa() if natasa else None, **kw)

    @property
    def pose(self) -> float:
        return self.phase

    def cycle(self) -> bytes:
        """One cycle: every block's frame, the repeats, Mamka's record of 768 B; Nataša's frame."""
        s = self.sample
        if s % STEP == 0:
            self.phase = 2 * math.pi * 0.5 * s / ADS_SPS     # a swing twice a second
            self.steps = imu_steps(s, self.phase, 1.0)
        halves = []
        for half in (0, 1):
            frames: list[bytes | None] = []
            glove = None
            flags = 0
            for line in (1 + 2 * half, 2 + 2 * half):
                for slot in (1, 2, 3, 4):
                    blk = next((b for b in self.blocks if b.line == line and b.slot == slot), None)
                    if blk is None:
                        frames.append(None)
                        continue
                    f = blk.frame(s, self.pose, self.steps)
                    self.stats["frames"] += 1
                    key = (line, slot)
                    if key in self.pending_repeat:
                        # the repeat of the last cycle's bad frame rides behind the fresh one
                        old = blk.history.get(self.pending_repeat.pop(key))
                        if old is None or self.rng.random() < self.repeat_fail_rate:
                            self.stats["missing"] += 1
                            flags |= stp.FLAG_MISSING
                            self.records[-1] = self._patch(self.records[-1], half, len(frames), None)
                        else:
                            self.stats["repeated"] += 1
                            self.records[-1] = self._patch(self.records[-1], half, len(frames), old)
                    if self.rng.random() < self.bad_frame_rate:
                        self.stats["bad"] += 1
                        self.pending_repeat[key] = s
                        frames.append(None)         # arrives bad: the record waits for the repeat
                        flags |= stp.FLAG_WAITED
                    else:
                        frames.append(f)
                    if blk.glove:
                        gf = stp.BlockFrame(block=slot | stp.BEHIND, sample=s & 0xFFFF, channels=[0] * 8,
                                            imu=blk.imu_bytes(s, self.steps[4:8] + self.steps[:4])).pack()
                        glove = gf
            halves.append(stp.RecordHalf(s & 0xFFFF, half, frames, glove, 0, flags).pack())
        record = halves[0] + halves[1]
        self.records.append(record)
        self.sample += 1
        return record

    def _patch(self, record: bytes, half: int, index: int, frame: bytes | None) -> bytes:
        """Puts a repeated frame into the record that waited for it, and clears its wait flag."""
        h = stp.RecordHalf.unpack(record[384 * half:384 * half + 384])
        h.frames[index] = frame
        h.flags &= ~stp.FLAG_WAITED
        if frame is None:
            h.flags |= stp.FLAG_MISSING
        out = bytearray(record)
        out[384 * half:384 * half + 384] = h.pack()
        return bytes(out)

    def natasa_frame(self) -> bytes | None:
        if self.natasa is None:
            return None
        s = self.sample - 1
        n = 13 if s % 2 == 0 else 12
        mics = []
        for _ in range(n):
            self.mic_phase += 2 * math.pi * 440 / 48000
            v = int(8000 * math.sin(self.mic_phase))
            mics.append((v, v // 2))
        sphere = None
        if self.natasa.misa:
            if s % 240 == 0:
                self.natasa.sphere_no += 1
            sphere = self.natasa.sphere()
        self.stats["natasa"] += 1
        return self.natasa.frame(s, mics, sphere)
