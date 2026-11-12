"""python3 -m recorder --table sim/table.json --spi1 sim/spi1.bin --spi2 sim/spi2.bin --out r.bdf

Mamka's transfers from files, as the simulator writes them, into a BDF+ recording. The live
source, Baťa's two SPIs, comes with the first Mamka."""
import argparse
import sys

from recorder import Recorder, load_table, read_transfers


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="record Mamka's transfers into BDF+")
    ap.add_argument("--table", required=True, help="the units, table.json")
    ap.add_argument("--spi1", required=True, help="processor 1's transfers")
    ap.add_argument("--spi2", required=True, help="processor 2's transfers, both SPIs' shares")
    ap.add_argument("--out", required=True, help="the BDF+ file")
    ap.add_argument("--units", default="", help="the units' numbers, e.g. 0x61,0x62; all if none")
    ap.add_argument("--no-imu", action="store_true", help="the EMG alone")
    a = ap.parse_args(argv)
    table = load_table(a.table)
    units = [int(x, 0) for x in a.units.split(",") if x]
    rec = Recorder(table, a.out, units=units, imus=not a.no_imu)
    for proc, transfer in read_transfers(table, a.spi1, a.spi2):
        rec.feed(proc, transfer)
    print(rec.close())
    return 0


if __name__ == "__main__":
    sys.exit(main())
