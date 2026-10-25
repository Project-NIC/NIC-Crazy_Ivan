"""CI-BTP's stream captured to a file, each frame its class's length, read and summarized."""
from __future__ import annotations

from collections import Counter

from ci import btp


def write_frames(path: str, frames: list[bytes]) -> None:
    with open(path, "wb") as f:
        for fr in frames:
            f.write(fr)


def read_frames(path: str):
    """Walks a file frame by frame, each frame's length from its class in byte 4."""
    with open(path, "rb") as f:
        while True:
            head = f.read(btp.HEADER_LEN)
            if len(head) < btp.HEADER_LEN:
                return
            rest = f.read(btp.frame_len(head) - btp.HEADER_LEN)
            yield btp.Frame.unpack(head + rest)


def summarize(frames) -> dict:
    """What a file or a stream holds: frames, packets by type, gaps in the sample numbers."""
    types = Counter()
    n, last, back, first = 0, None, 0, None
    for fr in frames:
        n += 1
        if first is None:
            first = fr.sample
        for p in fr.packets:
            types[p.type] += 1
        if last is not None and fr.sample < last:
            back += 1
        last = fr.sample
    return {"frames": n, "packets": dict(types), "first": first, "last": last, "backwards": back}
