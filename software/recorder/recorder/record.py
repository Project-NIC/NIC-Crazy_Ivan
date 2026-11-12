"""Mamka's transfers in, cycle by cycle, into BDF+: every EMG channel at the chips' rate as the
chips gave it, every IMU's step at 120 Hz, the gaps and Mamka's events as annotations.

A cycle goes on once both processors' places of it are in, put together by the frames' number,
as Baťa does it live (`suitsim.Bata`). A frame that did not come is a gap: its samples hold the
unit's last ones, as Baťa holds them before any filter (porjadok/SOFTWARE.md), and the gap is
written as an annotation, so nobody takes the held samples for the body's.
"""
from __future__ import annotations

import datetime as dt
import struct
from collections.abc import Iterable, Iterator

from ci import stp

from . import bdf
from .table import Unit

EMG_UV = 333333          # ±VREF / gain: 4 V / 12 (rubaska/SOFTWARE.md, CONFIG3 and CHnSET)
GYRO_DPS = 0.070         # 70 mdps/LSB at ±2000 dps (DS13510 Rev 4, table 3)
ACC_G = 0.000488         # 0.488 mg/LSB at ±16 g (DS13510 Rev 4, table 3)
I16_MIN, I16_MAX = -32768, 32767
MAX_SIGNALS = 639        # a file's signals and the annotations' one: EDFlib's limit of 640,
                         # which pyedflib keeps (0.1.42, tried on 11 Nov 2026)
ANNOTATION_BYTES = 3072  # a record's room for its annotations, ~100 gaps or events a second


def read_transfers(table: list[Unit], spi1: str, spi2: str) -> Iterator[tuple[int, bytes]]:
    """The simulator's files, one cycle after another: processor 1's transfer from `spi1`, then
    processor 2's from `spi2`, her two SPIs' shares one after the other and joined here."""
    sizes = {p: sum(u.place for u in table if u.processor == p) + stp.EXTRA * stp.PLACE
             for p in (1, 2)}
    share = len(stp.stripe(bytes(sizes[2]))[0])
    with open(spi1, "rb") as f1, open(spi2, "rb") as f2:
        while True:
            t1, t2 = f1.read(sizes[1]), f2.read(2 * share)
            if len(t1) < sizes[1] or len(t2) < 2 * share:
                return
            yield 1, t1
            yield 2, stp.join(t2[:share], t2[share:])


class Recorder:
    """What is recorded: the units asked for (all the sensing ones if none), their EMG and, if
    asked, their IMUs' steps, in as many files as the signals need, whole units in each.
    `feed` takes a processor's transfer; `close` ends the files."""

    def __init__(self, table: list[Unit], path: str, start: dt.datetime | None = None,
                 units: Iterable[int] = (), imus: bool = True, rate: int = stp.ADS_SPS) -> None:
        self.placed = {p: [u for u in table if u.processor == p and u.place] for p in (1, 2)}
        wanted = set(units)
        self.units = [u for u in table if u.channels and (not wanted or u.number in wanted)]
        self.imus = imus
        self.rate = rate
        self.step_rate = rate // stp.STEP
        start = start or dt.datetime.now().replace(microsecond=0)
        self.files: list[tuple[bdf.Writer, list[Unit]]] = []
        group: list[Unit] = []
        count = 0
        for u in self.units:
            n = len(self._signals(u))
            if group and count + n > MAX_SIGNALS:
                self.files.append(self._writer(path, start, group))
                group, count = [], 0
            group.append(u)
            count += n
        if group:
            self.files.append(self._writer(path, start, group))
        self.writer_of = {u.number: w for w, us in self.files for u in us}
        self.expect = {1: 0, 2: 0}
        self.waiting: dict[int, dict[int, list]] = {}
        self.first: int | None = None              # the first cycle recorded, a step's start
        self.emg = {u.number: [] for u in self.units}           # a row of channels a cycle
        self.held = {u.number: [0] * u.channels for u in self.units}
        self.steps = {u.number: [[] for _ in range(u.imus)] for u in self.units}
        self.held_steps = {u.number: [bytes(stp.IMU_STEP_LEN)] * u.imus for u in self.units}
        self.assemblers = {u.number: stp.StepAssembler(u.imus, u.step_bytes) for u in self.units}
        self.gap_start: dict[int, int] = {}        # a unit's gap open since this cycle
        self.cycles = self.gaps = self.events = self.lost = 0
        self.written = 0                           # seconds written

    def _signals(self, u: Unit) -> list[bdf.Signal]:
        """A unit's signals: its EMG channels, then each IMU's turn and force."""
        out = [bdf.Signal(f"EMG {u.number:02X}-{c + 1:02d}", self.rate, "uV", -EMG_UV, EMG_UV,
                          transducer=f"ADS1298 gain 12, unit {u.name}",
                          prefilter="none, as the chip sent it") for c in range(u.channels)]
        for i in range(u.imus if self.imus else 0):
            out += [bdf.Signal(f"Gyr {u.number:02X}-{i + 1} {axis}", self.step_rate, "deg/s",
                               I16_MIN * GYRO_DPS, I16_MAX * GYRO_DPS, I16_MIN, I16_MAX,
                               "LSM6DSV16X, a step's mean rate", "8 samples, coning")
                    for axis in "XYZ"]
            out += [bdf.Signal(f"Acc {u.number:02X}-{i + 1} {axis}", self.step_rate, "g",
                               I16_MIN * ACC_G, I16_MAX * ACC_G, I16_MIN, I16_MAX,
                               "LSM6DSV16X, a step's mean force", "mean of 8 samples")
                    for axis in "XYZ"]
        return out

    def _writer(self, path: str, start: dt.datetime, units: list[Unit]) -> tuple:
        """The first file at `path`, the next ones at `path` with -2, -3 before its ending."""
        if self.files:
            stem, dot, end = path.rpartition(".")
            path = f"{stem}-{len(self.files) + 1}.{end}" if dot else f"{path}-{len(self.files) + 1}"
        signals = [s for u in units for s in self._signals(u)]
        return bdf.Writer(path, signals, start, annotation_bytes=ANNOTATION_BYTES), units

    # --- in ----------------------------------------------------------------------------------

    def feed(self, proc: int, stream: bytes) -> None:
        data, extra = stp.parse_cycle(stream, [u.place for u in self.placed[proc]])
        cycle = self.expect[proc]
        numbers = {stp.widen(cycle, f[2] | f[3] << 8) for f in data if f is not None}
        if numbers:
            cycle = min(numbers)
        self.expect[proc] = cycle + 1
        if self.placed[proc]:
            self.waiting.setdefault(cycle, {})[proc] = data
        for f in extra:
            self._extra(cycle, f)
        for c in sorted(self.waiting):
            got = self.waiting[c]
            if not all(p in got or not self.placed[p] for p in (1, 2)):
                break
            del self.waiting[c]
            self._cycle(c, got)

    def _extra(self, cycle: int, frame: bytes) -> None:
        """Mamka's events from the four places, as annotations; the rest is not recorded."""
        f = stp.Frame.unpack(frame)
        if f.kind != stp.K_READ | stp.ANSWER:
            return
        r = stp.Registers.unpack(frame)
        if r.unit == stp.P2 and r.chip == stp.CHIP_UNIT and r.reg == stp.REG_EVENTS:
            self.events += 1
            if self.first is not None:
                for w, _ in self.files:
                    w.annotate((cycle - self.first) / self.rate,
                               f"Mamka event {r.values[0]} {r.values[1]}")

    def _cycle(self, c: int, got: dict) -> None:
        if self.first is None:
            if c % stp.STEP:
                return                              # a recording starts at a step's start
            self.first = c
        elif c != self.first + self.cycles:
            for _ in range(c - (self.first + self.cycles)):       # cycles that never came
                self.lost += 1
                self._cycle(self.first + self.cycles, {})
        frames = {}
        for proc, data in got.items():
            for u, f in zip(self.placed[proc], data):
                frames[u.number] = f
        for u in self.units:
            f = frames.get(u.number)
            if f is None:
                self.gap_start.setdefault(u.number, c)
                values = self.held[u.number]
            else:
                self._close_gap(u.number, c)
                _, _, values, imu = stp.parse_data(f)
                self.held[u.number] = values
                a = self.assemblers[u.number]
                a.feed(c, imu)
                while a.steps:
                    period, i, step = a.steps.pop(0)
                    period -= 1                     # sent after its step: the step before's turn
                    if period * stp.STEP >= self.first:
                        self._step(u.number, i, period, step)
            self.emg[u.number].append(values)
        self.cycles += 1
        if self.cycles == (self.written + 1) * self.rate + stp.STEP:
            self._record()                          # a step late, the second's last steps in

    def _step(self, unit: int, i: int, period: int, step: bytes) -> None:
        """An IMU's step in its place of the record, the missing ones before it held."""
        series = self.steps[unit][i]
        index = period - self.first // stp.STEP - self.written * self.step_rate
        while len(series) < index:
            series.append(self.held_steps[unit][i])
        if len(series) == index:
            series.append(step)
            self.held_steps[unit][i] = step

    def _close_gap(self, unit: int, c: int) -> None:
        start = self.gap_start.pop(unit, None)
        if start is not None:
            self.gaps += 1
            self.writer_of[unit].annotate((start - self.first) / self.rate, f"gap {unit:02X}",
                                          (c - start) / self.rate)

    # --- out ---------------------------------------------------------------------------------

    def _record(self) -> None:
        """A second written to every file, a step after its end, when its IMUs' last steps have
        come (a unit sends a step's turn in the step after it). A gap still open at the second's
        end is written up to it and opened again from it, so every annotation lies in the record
        it belongs to."""
        end = self.first + (self.written + 1) * self.rate
        for unit, start in list(self.gap_start.items()):
            if start < end:
                self._close_gap(unit, end)
                self.gap_start[unit] = end
        for writer, units in self.files:
            samples = []
            for u in units:
                samples += list(zip(*self.emg[u.number][:self.rate]))   # rows to channels
                for i in range(u.imus if self.imus else 0):
                    series = self.steps[u.number][i]
                    series += [self.held_steps[u.number][i]] * (self.step_rate - len(series))
                    vals = [struct.unpack("<3h3h", s) for s in series[:self.step_rate]]
                    samples += [[v[k] for v in vals] for k in range(6)]
                    self.steps[u.number][i] = series[self.step_rate:]
            writer.write_record(samples)
        self.emg = {n: rows[self.rate:] for n, rows in self.emg.items()}
        self.written += 1

    def close(self) -> dict:
        """The files closed after their last whole second, its last IMU steps held, their
        frames never sent; what is left of a second, its samples and its annotations, is not
        written."""
        if self.first is not None and self.cycles >= (self.written + 1) * self.rate:
            self._record()
        unwritten = sum(len(w.queue) for w, _ in self.files)
        for w, _ in self.files:
            w.close()
        return {"files": len(self.files), "annotations unwritten": unwritten,
                "seconds": self.files[0][0].records if self.files else 0,
                "cycles": self.cycles, "gaps": self.gaps, "lost cycles": self.lost,
                "events": self.events}
