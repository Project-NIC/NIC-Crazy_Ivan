# The map

**Baťa's map:** the suit's table of what is fitted and every unit's settings, keyed by the UID,
in one JSON file, shown and set through a page of plain HTML forms
([Baťa](../../bata/SOFTWARE.md#the-map)). Python 3, the standard library only; the protocol's
codecs and simulator beside it.

| file | what is in it |
|---|---|
| `suitmap/core.py` | a bring-up put against the map: the places known without asking, a replaced module's place to confirm, the questions and the answers, the numbers by type, the missing kept until forgotten, the settings in the service mode |
| `suitmap/web.py` | the page: the questions with the line's free places and the LED to blink, the table by line, the settings as buttons; reloading every 2 s, no JavaScript |
| `suitmap/lists.py` | the place list; the IMUs' places on the bones and the joint list, a first draft |
| `tests/` | the known places, the answers and the numbers, a replacement, forgetting, one bias, the service mode, the page over HTTP, the lists against the simulator |

```
python3 -m suitmap --map /tmp/map.json --sim 16 --port 8080      # a simulated suit brought up
python3 -m unittest discover -s tests -t .
```

- **Known without asking:** the glove and the sock by their kind in the fourth place of an arm's
  or a leg's line; the head and the chest, lines 5 and 6; Nataša and Míša by their kinds. A new
  UID where exactly one unit of its kind is missing takes its place, and the person confirms it;
  a unit moved to another line is asked about again.
- **Asked:** the three modules of each limb and line 7's two, at the first fitting: the page asks
  which of the line's free places, the unit's LED blinking at a button; the answer gives the
  place and the number, the type's next free one (0x61… two chips, 0x81… one, 0xE1… gloves and
  socks).
- **The settings:** one module drives the bias, a second one chosen takes it over; each strip's
  ground layer on ground or driven; the IMU mode, the glove's and the sock's too; only in the
  service mode, sent at the next start.
- **Listening** on 127.0.0.1 unless given Baťa's address on the local network; never a public one.
- **Not yet:** the Mamka link, which brings the bring-up's units, blinks the LED and sends the
  settings; until it exists, `--sim` brings the simulator's suit up once. Storož's state is
  shown as "unknown" until he has a file to read it from.
- **The joint list, a first draft,** also as a table in [Baťa](../../bata/SOFTWARE.md#the-map):
  96 values of the 127, from the IMUs' places in Bogatyr's
  CONSTRUCTION: the spine in four joints, each side's scapula, clavicle, shoulder (swing and
  twist), elbow, forearm, wrist, the thumb's three and each finger's three, hip (swing and twist),
  knee, ankle, midfoot and big toe; the ranges first guesses with room to spare. The glove's zones
  taken in the order index, middle, ring, little, thumb, carpus and the sock's four trial places
  are guesses until their tables are fixed.
