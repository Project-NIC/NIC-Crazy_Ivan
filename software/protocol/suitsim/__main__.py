"""python3 -m suitsim --seconds 1 --blocks 16 --out /tmp/sim: a suit for a second, into files."""
import argparse
import os
import sys

from suitsim import Suit, Bata, write_frames, read_frames, summarize
from ci import btp


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="simulate the suit and write what Baťa would")
    ap.add_argument("--seconds", type=float, default=1.0)
    ap.add_argument("--blocks", type=int, default=16)
    ap.add_argument("--no-natasa", action="store_true")
    ap.add_argument("--rate", type=int, choices=(128, 64, 32), default=128)
    ap.add_argument("--bad", type=float, default=0.0, help="share of frames that arrive bad, e.g. 0.001")
    ap.add_argument("--out", default="sim")
    ap.add_argument("--summarize", help="only read a .cibtp file and print what it holds")
    a = ap.parse_args(argv)
    if a.summarize:
        print(summarize(read_frames(a.summarize)))
        return 0
    suit = Suit.standard(a.blocks, not a.no_natasa, bad_frame_rate=a.bad)
    bata = Bata(rate={128: btp.RATE_128, 64: btp.RATE_64, 32: btp.RATE_32}[a.rate])
    cycles = int(a.seconds * 3840)
    for _ in range(cycles):
        rec = suit.cycle()
        bata.record(rec, suit.natasa_frame())
    bata.close()
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "records.bin"), "wb") as f:
        for r in suit.records:
            f.write(r)
    write_frames(os.path.join(a.out, "output.cibtp"), bata.frames_out)
    write_frames(os.path.join(a.out, "raw.cibtp"), bata.raw_out)
    print(f"cycles {cycles}, records {len(suit.records)} ({len(suit.records) * 768 / 1e6:.2f} MB), "
          f"suit {suit.stats}, gaps seen by Baťa {bata.gaps}")
    print("output.cibtp:", summarize(read_frames(os.path.join(a.out, 'output.cibtp'))))
    print("raw.cibtp:   ", summarize(read_frames(os.path.join(a.out, 'raw.cibtp'))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
