"""BDF+: BioSemi's 24-bit EDF with EDF+'s annotations, which EDFbrowser, MNE and EEGLAB read.

The header is EDF's (256 B, then 256 B a signal, every field ASCII, left-aligned, padded with
spaces), with BDF's two marks: the first byte 0xFF and "BIOSEMI" in the version, and "BDF+C" in
the reserved field, a continuous recording. A data record holds every signal's samples for its
duration, each sample three bytes, little-endian, two's complement. The annotations ride in a
signal of their own, "BDF Annotations", as EDF+'s time-stamped annotation lists (TALs): every
record's first TAL its onset in seconds from the start, `+<onset>\\x14\\x14\\x00`, then the events,
`+<onset>\\x15<duration>\\x14<text>\\x14\\x00`, the rest zeros. The number of records is written
as -1 while recording and set when the file is closed.
"""
from __future__ import annotations

import datetime as dt
import sys
from array import array
from dataclasses import dataclass

DIG_MIN, DIG_MAX = -(1 << 23), (1 << 23) - 1
MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()


@dataclass(frozen=True)
class Signal:
    label: str                 # 16 characters at most, "EMG 61-01"
    rate: int                  # samples a data record
    dimension: str = ""        # 8 at most, "uV"
    phys_min: float = DIG_MIN
    phys_max: float = DIG_MAX
    dig_min: int = DIG_MIN
    dig_max: int = DIG_MAX
    transducer: str = ""
    prefilter: str = ""


def _field(value, width: int) -> bytes:
    if isinstance(value, float):
        text = f"{value:.6f}".rstrip("0").rstrip(".")
        if len(text) > width:
            text = f"{value:.{max(0, width - len(str(int(value))) - 1)}f}"[:width]
    else:
        text = str(value)
    raw = text.encode("ascii")
    if len(raw) > width:
        raise ValueError(f"{text!r} longer than {width}")
    return raw.ljust(width, b" ")


def _onset(seconds: float) -> str:
    text = f"{seconds:+.6f}".rstrip("0").rstrip(".")
    return text if text not in ("+", "-") else "+0"


class Writer:
    """A BDF+ file written record by record; `annotate` queues an event, which goes into the
    first record with room for it at or after its time."""

    def __init__(self, path: str, signals: list[Signal], start: dt.datetime,
                 record_seconds: float = 1.0, annotation_bytes: int = 240,
                 patient: str = "X X X X", equipment: str = "NIC-CrazyIvan") -> None:
        if annotation_bytes % 3:
            raise ValueError("the annotations' bytes come in threes, a 24-bit sample each")
        self.signals = list(signals) + [Signal("BDF Annotations", annotation_bytes // 3)]
        self.annotation_bytes = annotation_bytes
        self.record_seconds = record_seconds
        self.records = 0
        self.queue: list[tuple[float, bytes]] = []
        ns = len(self.signals)
        date = f"{start.day:02d}-{MONTHS[start.month - 1]}-{start.year}"
        start_text = f"Startdate {date} X X {equipment}"
        head = (b"\xffBIOSEMI" + _field(patient, 80) + _field(start_text, 80)
                + _field(start.strftime("%d.%m.%y"), 8) + _field(start.strftime("%H.%M.%S"), 8)
                + _field(256 * (ns + 1), 8) + _field("BDF+C", 44) + _field(-1, 8)
                + _field(_number(record_seconds), 8) + _field(ns, 4))
        for name, width in (("label", 16), ("transducer", 80), ("dimension", 8),
                            ("phys_min", 8), ("phys_max", 8), ("dig_min", 8), ("dig_max", 8),
                            ("prefilter", 80), ("rate", 8)):
            head += b"".join(_field(getattr(s, name), width) for s in self.signals)
        head += b" " * 32 * ns
        self.f = open(path, "wb")
        self.f.write(head)

    def annotate(self, onset: float, text: str, duration: float | None = None) -> None:
        tal = _onset(onset).encode("ascii")
        if duration is not None:
            tal += b"\x15" + _number(duration).encode("ascii")
        self.queue.append((onset, tal + b"\x14" + text.encode("utf-8") + b"\x14\x00"))

    def write_record(self, samples: list[list[int]]) -> None:
        """One data record: a list of samples for every signal but the annotations, each list
        of its signal's rate, values within its digital range."""
        if len(samples) != len(self.signals) - 1:
            raise ValueError("a list of samples for every signal")
        out = bytearray()
        for s, values in zip(self.signals, samples):
            if len(values) != s.rate:
                raise ValueError(f"{s.label}: {len(values)} samples, the rate is {s.rate}")
            if values and not (s.dig_min <= min(values) and max(values) <= s.dig_max):
                raise ValueError(f"{s.label}: a value outside the digital range")
            a = array("i", values)                     # 32 bits little-endian, then the top
            if sys.byteorder == "big":                 # byte of each dropped: 24 bits
                a.byteswap()
            words = bytearray(a.tobytes())
            del words[3::4]
            out += words
        onset = self.records * self.record_seconds
        tals = _onset(onset).encode("ascii") + b"\x14\x14\x00"
        later = []
        for at, tal in self.queue:
            if at < onset + self.record_seconds and len(tals) + len(tal) <= self.annotation_bytes:
                tals += tal
            else:
                later.append((at, tal))
        self.queue = later
        out += tals.ljust(self.annotation_bytes, b"\x00")
        self.f.write(out)
        self.records += 1

    def close(self) -> None:
        """The records counted into the header; events still queued are dropped, so the last
        record should be written after the last event."""
        self.f.seek(236)
        self.f.write(_field(self.records, 8))
        self.f.close()


def _number(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else _onset(v).lstrip("+")


# --- reading back, for the tests and a quick look -------------------------------------------------

@dataclass
class Recording:
    start: dt.datetime
    record_seconds: float
    signals: list[Signal]
    samples: list[list[int]]              # every signal's digital values, end to end
    annotations: list[tuple[float, float | None, str]]


def read(path: str) -> Recording:
    """A BDF or BDF+ file of ours: the header, the samples and the events (not the records'
    own time-keeping TALs)."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\xffBIOSEMI":
        raise ValueError("not a BDF file")
    text = lambda a, b: data[a:b].decode("ascii").strip()           # noqa: E731
    ns = int(text(252, 256))
    records = int(text(236, 244))
    seconds = float(text(244, 252))
    start = dt.datetime.strptime(text(168, 176) + text(176, 184), "%d.%m.%y%H.%M.%S")
    pos, cols = 256, {}
    for name, width in (("label", 16), ("transducer", 80), ("dimension", 8), ("phys_min", 8),
                        ("phys_max", 8), ("dig_min", 8), ("dig_max", 8), ("prefilter", 80),
                        ("rate", 8), ("reserved", 32)):
        cols[name] = [data[pos + i * width:pos + (i + 1) * width].decode("ascii").strip()
                      for i in range(ns)]
        pos += width * ns
    signals = [Signal(cols["label"][i], int(cols["rate"][i]), cols["dimension"][i],
                      float(cols["phys_min"][i]), float(cols["phys_max"][i]),
                      int(cols["dig_min"][i]), int(cols["dig_max"][i]),
                      cols["transducer"][i], cols["prefilter"][i]) for i in range(ns)]
    samples: list[list[int]] = [[] for _ in range(ns)]
    annotations = []
    record_len = 3 * sum(s.rate for s in signals)
    for r in range(records):
        p = pos + r * record_len
        for i, s in enumerate(signals):
            raw = data[p:p + 3 * s.rate]
            p += 3 * s.rate
            if s.label in ("BDF Annotations", "EDF Annotations"):
                annotations += _tals(raw)
            else:
                for k in range(0, len(raw), 3):
                    v = int.from_bytes(raw[k:k + 3], "little")
                    samples[i].append(v - (1 << 24) if v & 0x800000 else v)
    keep = [i for i, s in enumerate(signals) if not s.label.endswith("Annotations")]
    return Recording(start, seconds, [signals[i] for i in keep], [samples[i] for i in keep],
                     annotations)


def _tals(raw: bytes) -> list[tuple[float, float | None, str]]:
    out = []
    for tal in raw.split(b"\x00"):
        if not tal:
            continue
        parts = tal.split(b"\x14")
        head, texts = parts[0], [t for t in parts[1:] if t]
        onset, _, duration = head.partition(b"\x15")
        for t in texts:
            out.append((float(onset), float(duration) if duration else None, t.decode("utf-8")))
    return out
