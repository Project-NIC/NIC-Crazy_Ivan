"""python3 -m suitmap --map map.json [--sim 16] [--host 127.0.0.1] [--port 8080]

The map's page. Until the Mamka link exists, `--sim` brings a simulated suit up once, its units
with their UIDs as the simulator makes them."""
import argparse
import sys

from suitmap import Map, Seen
from suitmap.web import serve


def simulated(n: int) -> list[Seen]:
    from suitsim import Suit
    return [Seen(u.uid.hex(), u.line, u.kind, u.ads, 0x0100) for u in Suit.standard(n).units]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="the suit's map")
    ap.add_argument("--map", required=True, help="the map's JSON file")
    ap.add_argument("--sim", type=int, default=0, help="bring up a simulated suit of n modules")
    ap.add_argument("--host", default="127.0.0.1", help="Baťa's address on the local network")
    ap.add_argument("--port", type=int, default=8080)
    a = ap.parse_args(argv)
    m = Map(a.map)
    if a.sim:
        m.bring_up(simulated(a.sim))
    server = serve(m, a.host, a.port)
    print(f"the map on http://{a.host}:{a.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
