"""The map's logic (bata/SOFTWARE.md, *The map*): what a bring-up found, set against the map kept
by UID; what is known without asking, what is asked, the numbers given, the settings.

- **Known without asking:** the line tells the piece; the kind tells the glove and the sock,
  the fourth place of an arm's or a leg's line; lines 5 and 6 carry one module each; line 8
  Nataša and Míša by their kinds.
- **A module replaced,** a new UID on a line where exactly one unit of the map of that kind is
  missing, takes the missing one's place, waiting for the person's confirmation.
- **Asked:** the order on a line, the module's LED blinking while the question stands; the
  answer gives the unit its place and its number, its type's next free one.
- **Missing** units stay in the map until the person forgets them.
- **The settings,** which module drives the bias (one), each strip's ground layer and the IMU
  mode, the glove's and the sock's too, are set only in the service mode and go to the units at
  the next start.
- **A unit moved** to another line is placed again.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field

from ci import stp

from .lists import HAND_FOOT, LINE_PLACES, PLACES

KIND_NAMES = {stp.KIND_EMG: "module", stp.KIND_END: "glove or sock", stp.KIND_NATASA: "Nataša",
              stp.KIND_MISA: "Míša"}


@dataclass
class Seen:
    """A unit as a bring-up found it: Mamka's report of a line."""
    uid: str                      # hex
    line: int
    kind: int
    ads: int = 0
    firmware: int = 0
    diagnostics: dict = field(default_factory=dict)   # off electrodes, temperature, 3.3 V, reset


@dataclass
class Entry:
    """A unit in the map."""
    uid: str
    line: int
    kind: int
    ads: int = 0
    place: int = 0                # 0 not yet known
    number: int = 0               # 0 not yet given
    confirmed: bool = False
    bias: bool = False            # this module drives the bias
    shield: int = 0               # the strip's ground layer: 0 on ground, 1 driven
    imu_mode: int = 0
    replaces: str = ""            # the missing unit's UID whose place it takes, to be confirmed


class Map:
    """The map in one JSON file keyed by the UID, which can be edited over SSH too."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.units: dict[str, Entry] = {}
        self.present: dict[str, Seen] = {}
        self.service = True                       # the settings only in the service mode
        self.blinking: str | None = None          # the UID whose LED blinks, asked about
        if os.path.exists(path):
            with open(path) as f:
                self.units = {u: Entry(**e) for u, e in json.load(f)["units"].items()}

    def save(self) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump({"units": {u: asdict(e) for u, e in sorted(self.units.items())}}, f,
                      indent=1, ensure_ascii=False)
        os.replace(tmp, self.path)

    # --- a bring-up --------------------------------------------------------------------------

    def bring_up(self, seen: list[Seen]) -> None:
        """What Mamka found, put against the map."""
        self.present = {s.uid: s for s in seen}
        for s in seen:
            e = self.units.get(s.uid)
            if e is None:
                e = self.units[s.uid] = Entry(s.uid, s.line, s.kind, s.ads)
            if e.line != s.line:                       # moved to another piece: placed again
                e.place, e.confirmed, e.replaces = 0, False, ""
            e.line, e.kind, e.ads = s.line, s.kind, s.ads
            if not e.place:
                self._known(e)
        for line in LINE_PLACES:
            self._replacements(line)
        self.save()

    def _known(self, e: Entry) -> None:
        """The places no one needs to be asked about."""
        place = 0
        if e.kind == stp.KIND_END and e.line in HAND_FOOT:
            place = HAND_FOOT[e.line]
        elif e.kind == stp.KIND_NATASA:
            place = 21
        elif e.kind == stp.KIND_MISA:
            place = 22
        elif e.line in (5, 6) and e.kind == stp.KIND_EMG:
            place = LINE_PLACES[e.line][0]
        if place and not self._taken(place, e.uid):
            self._give(e, place, confirmed=True)

    def _replacements(self, line: int) -> None:
        """A new UID where exactly one unit of the map of its kind is missing takes its place,
        to be confirmed."""
        new = [e for e in self.units.values() if e.line == line and not e.place
               and e.uid in self.present]
        for e in new:
            gone = [m for m in self.units.values() if m.line == line and m.place
                    and m.uid not in self.present and m.kind == e.kind and m.ads == e.ads]
            if len(gone) == 1 and len(new) == 1:
                old = gone[0]
                e.place, e.number, e.confirmed = old.place, old.number, False
                e.bias, e.shield, e.imu_mode = old.bias, old.shield, old.imu_mode
                e.replaces = old.uid

    def _taken(self, place: int, but: str = "") -> bool:
        return any(e.place == place and e.uid != but and e.confirmed for e in self.units.values())

    def _give(self, e: Entry, place: int, confirmed: bool) -> None:
        e.place, e.confirmed = place, confirmed
        if not e.number and e.kind in (stp.KIND_EMG, stp.KIND_END):
            e.number = self._next_number(e)
        elif e.kind == stp.KIND_NATASA:
            e.number = stp.NATASA
        elif e.kind == stp.KIND_MISA:
            e.number = stp.MISA

    def _next_number(self, e: Entry) -> int:
        t = stp.T_GLOVE if e.kind == stp.KIND_END else stp.T_TWO if e.ads == 2 else stp.T_ONE
        used = {u.number for u in self.units.values()}
        for n in range(1, 32):
            if stp.address(t, n) not in used:
                return stp.address(t, n)
        raise ValueError("no number left of this type")

    # --- the person's answers ----------------------------------------------------------------

    def questions(self) -> list[Entry]:
        """The present units whose place is not known, line by line."""
        return sorted((e for e in self.units.values() if e.uid in self.present and not e.place),
                      key=lambda e: e.line)

    def free_places(self, line: int) -> list[int]:
        return [p for p in LINE_PLACES[line] if not self._taken(p)]

    def ask(self, uid: str | None) -> None:
        """The LED of the unit asked about blinks (chip 0x00 register 0x02), the others not."""
        self.blinking = uid

    def answer(self, uid: str, place: int) -> None:
        e = self.units[uid]
        if place not in self.free_places(e.line):
            raise ValueError(f"place {place} is not free on line {e.line}")
        self._give(e, place, confirmed=True)
        self.blinking = None
        self.save()

    def confirm(self, uid: str) -> None:
        """A replacement confirmed: the missing one leaves the map, its place and number the new
        one's."""
        e = self.units[uid]
        if e.replaces in self.units:
            del self.units[e.replaces]
        e.confirmed, e.replaces = True, ""
        self.save()

    def forget(self, uid: str) -> None:
        if uid in self.present:
            raise ValueError("only a missing unit is forgotten")
        del self.units[uid]
        self.save()

    # --- the settings -------------------------------------------------------------------------

    def set(self, uid: str, bias: bool | None = None, shield: int | None = None,
            imu_mode: int | None = None) -> None:
        if not self.service:
            raise PermissionError("settings only in the service mode")
        e = self.units[uid]
        if bias and e.kind != stp.KIND_EMG:
            raise ValueError("only a module drives the bias")
        if bias:
            for other in self.units.values():          # one module drives the body, never two
                other.bias = False
        if bias is not None:
            e.bias = bias
        if shield is not None:
            e.shield = int(shield)
        if imu_mode is not None:
            e.imu_mode = int(imu_mode)
        self.save()

    # --- what is shown -------------------------------------------------------------------------

    def table(self) -> list[dict]:
        """One row a unit, by line and place: the place, the UID's last four hex digits, the
        kind, the firmware, present or missing, the settings, the diagnostics."""
        rows = []
        for e in sorted(self.units.values(), key=lambda e: (e.line, e.place or 99, e.uid)):
            s = self.present.get(e.uid)
            rows.append({
                "uid": e.uid, "line": e.line, "place": e.place,
                "place_name": PLACES.get(e.place, "unknown"), "uid4": e.uid[-4:].upper(),
                "kind": KIND_NAMES.get(e.kind, str(e.kind)), "number": e.number,
                "firmware": s.firmware if s else None, "present": s is not None,
                "confirmed": e.confirmed, "bias": e.bias, "shield": e.shield,
                "imu_mode": e.imu_mode, "diagnostics": s.diagnostics if s else {},
                "blinking": e.uid == self.blinking, "replaces": e.replaces[-4:].upper(),
                "sensing": e.kind in (stp.KIND_EMG, stp.KIND_END)})
        return rows
