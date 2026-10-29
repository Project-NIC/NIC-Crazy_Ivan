"""Baťa's side: both processors' transfers in, put together by the frames' number, the output
frames out."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from ci import btp, stp

ECG_DECIMATION = 4      # 1,920 SPS to 480, the ECG's default


@dataclass
class Bata:
    maps: dict                         # {processor: her units in her table's order}
    rate: int = btp.RATE_128
    cls: int = btp.CLASS_512
    frames_out: list[bytes] = field(default_factory=list)
    events: int = 0
    pending: list[btp.Packet] = field(default_factory=list)
    waiting: dict = field(default_factory=dict)     # cycle -> {processor: her data places}
    expect: dict = field(default_factory=lambda: {1: 0, 2: 0})
    diagnostics: dict = field(default_factory=dict)  # a unit's number -> its last Diagnostics
    meta_cycle: int = 0
    cycles: int = 0
    lost: int = 0                      # cycles that never came: a jump in the frames' numbers
    empty: int = 0                     # places that should have held a frame of data
    out_of_step: int = 0               # a frame whose number is not its cycle's
    steps: int = 0                     # IMU steps put together
    spheres: stp.SphereAssembler = field(default_factory=stp.SphereAssembler)

    def __post_init__(self) -> None:
        # the units with a place of data, in the table's order, a place's size by the unit's kind
        self.place_units = {p: [u for u in self.maps[p] if u.place] for p in self.maps}
        self.ecg_units = [(2, i) for i, u in enumerate(self.place_units.get(2, []))
                          if getattr(u, "trunk", False)]
        self.ecg = [bytearray() for _ in self.ecg_units]
        self.ecg_first = 0
        self.assemblers = {}
        for u in (u for m in self.maps.values() for u in m if u.line < 8):
            per = stp.END_IMU if u.kind == stp.KIND_END else stp.MODULE_IMU
            self.assemblers[u.number] = stp.StepAssembler(u.imus, per)

    def placed(self, proc: int) -> list:
        """Her units with a place of data, in her table's order: all but Míša."""
        return [u for u in self.maps[proc] if u.place]

    # --- in --------------------------------------------------------------------------------------

    def transfer1(self, stream: bytes) -> None:
        """One cycle from processor 1 on SPI1."""
        self.take(1, stream)

    def transfer2(self, spi_a: bytes, spi_b: bytes) -> None:
        """One cycle from processor 2, striped over her two SPIs."""
        self.take(2, stp.join(spi_a, spi_b))

    def take(self, proc: int, stream: bytes) -> None:
        """The places by the table, the cycle's number from the frames in them, the four places'
        frames by their kind; a cycle goes on once both processors' places of it are in."""
        data, extra = stp.parse_cycle(stream, [u.place for u in self.place_units[proc]])
        cycle = self.expect[proc]
        numbers = {stp.widen(cycle, f[2] | f[3] << 8) for f in data if f is not None}
        if numbers:
            first = min(numbers)
            self.out_of_step += len(numbers) - 1
            if first > cycle:
                self.lost += first - cycle
            cycle = first
        self.expect[proc] = cycle + 1
        if self.maps[proc]:
            self.waiting.setdefault(cycle, {})[proc] = data
        for f in extra:
            self.frame(f)
        self.release()

    def frame(self, frame: bytes) -> None:
        """A frame of the four places: diagnostics, Míša's sphere, Mamka's events."""
        f = stp.Frame.unpack(frame)
        if f.kind == stp.K_DIAGNOSTICS:
            u = self.unit(f.unit)
            d = stp.Diagnostics.unpack(frame, len(stp.which_imus(f.number, u.imus)) if u else 6)
            self.diagnostics[f.unit] = d
        elif f.kind == stp.K_READ | stp.ANSWER:
            r = stp.Registers.unpack(frame)
            if r.unit == stp.MISA and r.chip == stp.CHIP_SPHERE:
                self.spheres.feed(frame)
                while self.spheres.spheres:
                    _, sph = self.spheres.spheres.pop(0)
                    self.pending.append(btp.sphere(sph))
            elif r.unit == stp.P2 and r.chip == stp.CHIP_UNIT and r.reg == stp.REG_EVENTS:
                self.events += 1
                self.pending.append(btp.event(self.events, r.values[0], r.values[1]))

    def unit(self, number: int):
        return next((u for m in self.maps.values() for u in m if u.number == number), None)

    def release(self) -> None:
        """In order: a cycle with both processors' places goes on."""
        for c in sorted(self.waiting):
            got = self.waiting[c]
            if not all(p in got or not self.maps[p] for p in (1, 2)):
                break
            del self.waiting[c]
            self.cycle(c, got)

    # --- a whole cycle ---------------------------------------------------------------------------

    def cycle(self, c: int, got: dict) -> None:
        """Both processors' frames of one cycle: the IMU steps from the frames, the ECG of the
        trunk's modules, a snapshot every step."""
        self.cycles += 1
        for proc, data in got.items():
            for u, f in zip(self.place_units[proc], data):
                if u.line == 8:
                    continue
                if f is None:
                    self.empty += 1
                    continue
                a = self.assemblers[u.number]
                before = len(a.steps)
                body = stp.Frame.unpack(f).body
                a.feed(c, body[-a.per:])                 # the steps' bytes last, 4 B or 28 B
                self.steps += len(a.steps) - before
        if c % ECG_DECIMATION == 0:
            for k, (proc, i) in enumerate(self.ecg_units):
                f = got.get(proc, [None] * (i + 1))[i]
                self.ecg[k].append(f[4] if f is not None else 0x80)   # channel 1's top byte
            if self.ecg and len(self.ecg[0]) == 1:
                self.ecg_first = c
        if c % stp.STEP == 0:
            self.snapshot(c)

    # --- out -------------------------------------------------------------------------------------

    def snapshot(self, cycle: int) -> None:
        every = {btp.RATE_256: 1, btp.RATE_128: 1, btp.RATE_64: 2, btp.RATE_32: 4}[self.rate]
        step = cycle // stp.STEP
        if step % every:
            return
        joints = bytes(int(128 + 100 * math.sin(cycle / stp.ADS_SPS * math.pi + i / 10)) & 0xFF
                       for i in range(127))
        contacts = 0b11 << 28 | 0b11 << 30   # the heels and the balls of the feet: standing
        pk = [btp.snapshot(step % 16, joints, contacts)]
        if self.ecg and self.ecg[0]:
            pk.append(btp.ecg(self.ecg_first, [bytes(e) for e in self.ecg], ECG_DECIMATION))
            for e in self.ecg:
                e.clear()
        pk += self.pending
        self.pending = []
        self.frames_out.append(btp.Frame(cycle, pk, self.cls).pack())
        # beyond the snapshots, a meta packet after every fifteenth: eight a second at 128 frames
        self.meta_cycle += 1
        if self.meta_cycle % 15 == 0:
            which = (self.meta_cycle // 15 - 1) % 8 + 1
            self.frames_out.append(btp.Frame(cycle, [self.meta_packet(which)], self.cls).pack())

    def units(self) -> list:
        return [u for p in (1, 2) for u in self.maps[p]]

    def map_units(self) -> list[btp.MapUnit]:
        return [btp.MapUnit(u.number, u.kind, i, u.imus, 0x0100)
                for i, u in enumerate(self.units())]

    def meta_packet(self, which: int) -> btp.Packet:
        units = self.units()
        if which == 1:
            return btp.meta_suit(b"SIM-0001", 1, 0, 0x0001, 0x0100, 0x0100, self.rate, 127, 32,
                                 len(self.ecg_units), self.map_units(), (1 << len(units)) - 1)
        if which == 2:
            return btp.meta_bones(1800, 800,
                                  [120, 500, 420, 300] + [320, 260, 190, 450, 420, 260] * 2)
        if which == 3:
            return btp.meta_joints(3, [(i // 3, i % 3 + 1, -60, 60) for i in range(64)])
        if which == 4:
            entries = [((64 + i) // 3, (64 + i) % 3 + 1, -60, 60) for i in range(63)]
            return btp.meta_joints(4, entries, list(range(32)))
        if which == 5:
            channels = bytearray()
            for u in units:
                if u.kind == stp.KIND_EMG:
                    d = self.diagnostics.get(u.number)
                    p, n = (d.p_on, d.n_on) if d else (0xFFFF, 0xFFFF)
                    channels += bytes(0x04 | (~p >> i & 1) | (~n >> i & 1) << 1
                                      for i in range(8 * u.ads))
            return btp.meta_electrodes(bytes(channels), 0, 0xFFFF, 0)
        if which == 6:
            temps = [10 * d.temp_c if d else 0x7FFF
                     for d in (self.diagnostics.get(u.number) for u in units)]
            imus = sum(u.imus for u in units)
            battery = stp.Battery((3300,) * 4, 13200, -1500, (250, 260, 270), 0, 55, 6600).pack()
            return btp.meta_temperatures((temps + [0x7FFF] * btp.UNITS)[:btp.UNITS], [26] * min(imus, btp.IMUS),
                                         (300, 310, 450), battery, 0x3FF, 2100)
        if which == 7:
            return btp.meta_fatigue(bytes(btp.CHANNELS), bytes(64))
        return btp.meta_time(0, 0, 0, 0, 0, 0, 0)

    def close(self) -> None:
        for c in sorted(self.waiting):
            self.cycle(c, self.waiting.pop(c))
        if self.pending:
            self.frames_out.append(btp.Frame(self.expect[1], self.pending, self.cls).pack())
            self.pending = []
