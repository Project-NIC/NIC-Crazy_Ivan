"""python3 -m suitsim --seconds 1 --modules 16 --out /tmp/sim: a suit for a second, into files."""
import argparse
import os
import sys

from suitsim import Suit, Bata, write_frames, read_frames, summarize
from ci import btp


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="simulate the suit and write what Baťa would")
    ap.add_argument("--seconds", type=float, default=1.0)
    ap.add_argument("--modules", type=int, default=16)
    ap.add_argument("--no-gloves", action="store_true")
    ap.add_argument("--no-line8", action="store_true", help="no Nataša and no Míša")
    ap.add_argument("--rate", type=int, choices=(256, 128, 64, 32), default=128)
    ap.add_argument("--bad", type=float, default=0.0,
                    help="share of frames that arrive bad, e.g. 0.001")
    ap.add_argument("--out", default="sim")
    ap.add_argument("--summarize", help="only read a .cibtp file and print what it holds")
    a = ap.parse_args(argv)
    if a.summarize:
        print(summarize(read_frames(a.summarize)))
        return 0
    suit = Suit.standard(a.modules, not a.no_line8, not a.no_gloves, bad_frame_rate=a.bad)
    rate = {256: btp.RATE_256, 128: btp.RATE_128, 64: btp.RATE_64, 32: btp.RATE_32}[a.rate]
    bata = Bata({1: suit.of(1), 2: suit.of(2)}, rate=rate)
    cycles = int(a.seconds * 3840)
    for _ in range(cycles):
        t1, share = suit.cycle()
        bata.transfer1(t1)
        bata.transfer2(*share)
    bata.close()
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "spi1.bin"), "wb") as f:
        for t in suit.p1:
            f.write(t)
    with open(os.path.join(a.out, "spi2.bin"), "wb") as f:
        for sa, sb in suit.p2:
            f.write(sa + sb)
    write_frames(os.path.join(a.out, "output.cibtp"), bata.frames_out)
    size = sum(len(t) for t in suit.p1) + sum(2 * len(sa) for sa, _ in suit.p2)
    print(f"cycles {cycles}, transfers {len(suit.p1)} + {len(suit.p2)} ({size / 1e6:.2f} MB), "
          f"suit {suit.stats}, Baťa: cycles {bata.cycles}, empty places {bata.empty}, "
          f"lost {bata.lost}, out of step {bata.out_of_step}, IMU steps {bata.steps}")
    print("output.cibtp:", summarize(read_frames(os.path.join(a.out, 'output.cibtp'))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
