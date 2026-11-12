"""The units a recording knows: Baťa's map as it stands for one run, one JSON file.

    {"units": [{"number": 97, "name": "shoulder L", "line": 1, "slot": 1,
                "kind": 1, "ads": 2, "imus": 4}, ...]}

`kind` is the protocol's (`stp.KIND_EMG` 1, `KIND_END` 2 the glove and the sock, `KIND_NATASA`
3, `KIND_MISA` 4); the units by line and on each line by slot, as each processor's table orders
them. The simulator writes the same file (`python3 -m suitsim --out sim`, `table.json`).
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from ci import stp

P1_LINES = range(1, 5)        # the arms and the legs on processor 1, the rest on processor 2


def processor(line: int) -> int:
    return 1 if line in P1_LINES else 2


@dataclass(frozen=True)
class Unit:
    number: int
    name: str
    line: int
    slot: int
    kind: int
    ads: int = 0
    imus: int = 0

    @property
    def processor(self) -> int:
        return processor(self.line)

    @property
    def place(self) -> int:
        """Its place of data a cycle: 58 B, 34 B or none (Míša)."""
        return stp.place_len(self.kind, self.ads)

    @property
    def channels(self) -> int:
        """EMG channels in its frame of data: 16 for a module of two chips, 8 for one chip and
        for the glove and the sock, none for Nataša and Míša."""
        if self.kind not in (stp.KIND_EMG, stp.KIND_END):
            return 0
        return 16 if self.ads == 2 and self.kind == stp.KIND_EMG else 8

    @property
    def step_bytes(self) -> int:
        """IMU bytes a frame: 4 a module's, 28 the glove's and the sock's."""
        return stp.END_IMU if self.kind == stp.KIND_END else stp.MODULE_IMU


def load_table(path: str) -> list[Unit]:
    with open(path) as f:
        units = [Unit(**u) for u in json.load(f)["units"]]
    return sorted(units, key=lambda u: (u.line, u.slot))
