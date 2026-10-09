"""Baťa's side: the records in, the output frames and the recordings out."""
from __future__ import annotations

import math
import struct
from dataclasses import dataclass, field

from ci import btp, stp

P_RAW_HALF, P_RAW_NATASA = 16, 17   # the raw packets, to disk only (porjadok/SOFTWARE.md, Output)


@dataclass
class Bata:
    rate: int = btp.RATE_128
    sample: int = 0                       # the 32-bit sample number Baťa keeps
    last16: int | None = None
    frames_out: list[bytes] = field(default_factory=list)
    raw_out: list[bytes] = field(default_factory=list)
    events: int = 0
    buttons: int = 0
    pending: list[btp.Packet] = field(default_factory=list)
    raw_pending: list[btp.Packet] = field(default_factory=list)
    ecg: list[bytearray] = field(default_factory=lambda: [bytearray() for _ in range(4)])
    ecg_first: int = 0
    meta_cycle: int = 0
    gaps: int = 0
    out_frames: int = 0

    def __post_init__(self) -> None:
        self.raw_out.extend(f.pack() for f in self.meta_frames())
        self.pending = []

    # --- in --------------------------------------------------------------------------------------

    def record(self, record: bytes, natasa_frame: bytes | None = None) -> None:
        h0 = stp.RecordHalf.unpack(record[:384])
        h1 = stp.RecordHalf.unpack(record[384:])
        s16 = h0.sample
        if self.last16 is not None:
            d = (s16 - self.last16) & 0xFFFF
            if d != 1:
                self.gaps += 1
            self.sample += d
        self.last16 = s16
        self.raw_pending.append(btp.Packet(P_RAW_HALF, 0, record[:384]))
        self.raw_pending.append(btp.Packet(P_RAW_HALF, 1, record[384:]))
        if natasa_frame is not None:
            self.raw_pending.append(btp.Packet(P_RAW_NATASA, 0, natasa_frame))
            nf = stp.NatasaFrame.unpack(natasa_frame)
            if nf.buttons != self.buttons:
                changed = nf.buttons ^ self.buttons
                for bit in range(16):
                    if changed & (1 << bit):
                        self.events += 1
                        self.pending.append(btp.event(self.events, 1, bit, bytes([1 if nf.buttons & (1 << bit) else 0])))
                self.buttons = nf.buttons
        # the ECG: the trunk's four blocks, channel 1, one byte a sample (the top byte of 24)
        for i, f in enumerate(h0.frames[:4]):
            if f is not None:
                self.ecg[i].append((stp.BlockFrame.unpack(f).channels[0] >> 16) & 0xFF)
            else:
                self.ecg[i].append(0x80)
        if len(self.ecg[0]) == 1:
            self.ecg_first = self.sample
        self.flush_raw()
        if self.sample % 32 == 0:
            self.snapshot(h0, h1)

    # --- out -------------------------------------------------------------------------------------

    def snapshot(self, h0: stp.RecordHalf, h1: stp.RecordHalf) -> None:
        every = {btp.RATE_128: 1, btp.RATE_64: 2, btp.RATE_32: 4}[self.rate]
        step = self.sample // 32
        if step % every:
            return
        joints = bytes(int(128 + 100 * math.sin(self.sample / 3840 * math.pi + i / 10)) & 0xFF for i in range(127))
        contacts = 0b11 << 28 | 0b11 << 30   # heels and the balls of the feet: standing
        pk = [btp.snapshot(step % 16, joints, contacts)]
        if len(self.ecg[0]) >= 32:
            pk.append(btp.ecg(self.ecg_first & 0xFFFF, [bytes(e[:32]) for e in self.ecg]))
            for e in self.ecg:
                del e[:32]
            self.ecg_first += 32
        pk += self.pending
        self.pending = []
        self.frames_out.append(btp.Frame(self.sample, pk).pack())
        self.out_frames += 1
        # the meta frames in between: one of the eight after every fifteen snapshots at 128 fps
        self.meta_cycle += 1
        if self.meta_cycle % 15 == 0:
            which = (self.meta_cycle // 15 - 1) % 8 + 1
            self.frames_out.append(btp.Frame(self.sample, [self.meta_packet(which)]).pack())
            self.out_frames += 1

    def meta_packet(self, which: int) -> btp.Packet:
        if which == 1:
            return btp.meta_suit(b"SIM-0001", 1, 0, 0x0001, (0x100, 0x100, 0x100, 0x100), 0xFFFF, [0x100] * 16, self.rate, 127, 32, 4)
        if which == 2:
            return btp.meta_bones(1800, 800, [120, 500, 420, 300] + [320, 260, 190, 450, 420, 260] * 2)
        if which == 3:
            return btp.meta_joints(3, [(i // 3, i % 3 + 1, -60, 60) for i in range(64)])
        if which == 4:
            return btp.meta_joints(4, [((64 + i) // 3, (64 + i) % 3 + 1, -60, 60) for i in range(63)], list(range(32)))
        if which == 8:
            return btp.meta_time(0, 0, 0, 0, 0, 0, 0)
        return btp.meta(which, bytes(btp.META_LEN[which]))

    def meta_frames(self) -> list[btp.Frame]:
        return [btp.Frame(self.sample, [self.meta_packet(w)]) for w in range(1, 9)]

    def flush_raw(self) -> None:
        """Packs the raw packets into 512 B frames as they fill: a record is two of them."""
        area, packets = 0, []
        for p in self.raw_pending:
            n = len(p.pack())
            if area + n > btp.PACKET_AREA:
                self.raw_out.append(btp.Frame(self.sample, packets).pack())
                area, packets = 0, []
            packets.append(p)
            area += n
        self.raw_pending = packets

    def close(self) -> None:
        if self.raw_pending:
            self.raw_out.append(btp.Frame(self.sample, self.raw_pending).pack())
            self.raw_pending = []
        if self.pending:
            self.frames_out.append(btp.Frame(self.sample, self.pending).pack())
            self.pending = []
