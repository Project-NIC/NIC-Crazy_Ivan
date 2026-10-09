"""Recordings: files of 512 B CI-BTP frames, read and summarized by one parser."""
from __future__ import annotations

from collections import Counter

from ci import btp


def write_frames(path: str, frames: list[bytes]) -> None:
    with open(path, "wb") as f:
        for fr in frames:
            f.write(fr)


def read_frames(path: str):
    with open(path, "rb") as f:
        while True:
            b = f.read(btp.FRAME_LEN)
            if len(b) < btp.FRAME_LEN:
                return
            yield btp.Frame.unpack(b)


def summarize(frames) -> dict:
    """What a file or a stream holds: frames, packets by type, gaps in the sample numbers."""
    types = Counter()
    n = 0
    last = None
    gaps = 0
    first = None
    for fr in frames:
        n += 1
        if first is None:
            first = fr.sample
        for p in fr.packets:
            types[p.type] += 1
        if last is not None and fr.sample < last:
            gaps += 1
        last = fr.sample
    return {"frames": n, "packets": dict(types), "first": first, "last": last, "backwards": gaps}
