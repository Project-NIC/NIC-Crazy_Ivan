# The protocols in Python

**CI-STP and CI-BTP as code:** codecs for every frame, place and packet the pages of
[Porjadok](../../porjadok/SOFTWARE.md), [Mamka](../../mamka/SOFTWARE.md),
[Nataša](../../natasa/SOFTWARE.md), [Míša](../../misa/SOFTWARE.md) and
[Rubaška](../../rubaska/SOFTWARE.md#the-bratiški) describe, with tests.
Python 3, the standard library only.

| file | what is in it |
|---|---|
| `ci/crc.py` | CRC-16/CCITT-FALSE and the CRC-32 of a firmware image |
| `ci/stp.py` | the five frames, 34 B, 58 B, 8 B, 519 B and 198 B, each kind with its one length; the commands and their answers, *discover* and *assign*, the reads and the writes, the LED's blink, *direct write*, *get ready*, *start*, *stop*, the heartbeat, *Mamka?*, the bus test with PRBS-9; a module's frame of data, 34 B with one chip and 58 B with two, the glove's and the sock's of 58 B with eight channels and 28 B of steps, Nataša's, the IMU steps 4 B or 28 B a frame and their assembler; a Bratiška's step of 52 B on his link and Staršaja's steps from the four; the diagnostics for 16 channels with the last reset's cause; the unit's table; the places on the SPIs, 58 or 34 B by the unit's kind, and processor 2's striping; the firmware's blocks, *begin* and the map; the sound's packets, Míša's sphere in five answers, the motors; Mamka's events, GPS, UTC and the battery's block |
| `ci/btp.py` | the place list; the output frames in three classes and their packets: snapshot, meta (the eight, with builders, the map in meta 1), ECG, sphere, event, vitals; *subscribe* and Baťa's answer |
| `suitsim/` | the simulator: modules, gloves and socks with made-up EMG, ECG and IMU steps, the limbs on lines 1–4 and processor 1, the head and the trunk on lines 5–7 and Nataša and Míša on line 8 on processor 2, frames damaged and dropped, the diagnostics, Nataša's buttons made events and Míša's sphere, processor 1's places on SPI1 and processor 2's striped over her two SPIs; Baťa putting both processors' cycles together by the frames' number, the IMU steps, the ECG and the output frames; a reader that summarizes a file |
| `tests/` | round trips, sizes, limits, the CRC vectors, and the simulator end to end |

Run the tests from this folder, or a second of the suit into files:

```
python3 -m unittest discover -s tests -t .
python3 -m suitsim --seconds 1 --modules 16 --bad 0.001 --out sim
python3 -m suitsim --summarize sim/output.cibtp
```

The second line writes `spi1.bin` (processor 1's transfers, 1,064 B a cycle), `spi2.bin`
(processor 2's, both SPIs' shares of 192 B one after the other) and `output.cibtp` (the live
stream at 128 frames a second in the class of 512 B), and prints how many frames went bad, how
many places Baťa found empty and how many IMU steps he put together.

The code is the second reading of the pages: where a page leaves a detail open, the code
chooses and its docstring says so. Firmware in C comes later and follows the same layouts.
