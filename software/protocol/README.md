# The protocols in Python

**CI-STP and CI-BTP as code:** codecs for every frame, container, record and packet the pages of
[Porjadok](../../porjadok/SOFTWARE.md), [Mamka](../../mamka/SOFTWARE.md) and
[Nataša](../../natasa/SOFTWARE.md) describe, with tests. Python 3, the standard library only.

| file | what is in it |
|---|---|
| `ci/crc.py` | CRC-16/CCITT-FALSE and the CRC-32 of a firmware image |
| `ci/stp.py` | the control frame, the containers and the master's message, the block's 40 B frame and the step assembler, Nataša's 68 B frame, the 384 B record halves, the UART packets and the I2C transfers, the firmware pieces, Interconnect, the sphere, the head's commands |
| `ci/btp.py` | the 512 B output frame and its packets: snapshot, meta (the eight, with builders), ECG, event, idle; *subscribe* |
| `suitsim/` | the simulator: blocks with made-up EMG, ECG and IMU steps on their lines, bad frames and their repeats, Mamka's records, Nataša's frame with the sphere, Baťa's output frames and the raw recording; a reader that summarizes a file |
| `tests/` | round trips, sizes, limits, the CRC vectors, and the simulator end to end |

Run the tests from this folder, or a second of the suit into files:

```
python3 -m unittest discover -s tests -t .
python3 -m suitsim --seconds 1 --blocks 16 --bad 0.001 --out sim
python3 -m suitsim --summarize sim/output.cibtp
```

The second line writes `records.bin` (Mamka's records as Baťa reads them over SPI),
`output.cibtp` (the live stream at 128 frames a second) and `raw.cibtp` (the recording with the
raw packets 16 and 17), and prints how many frames went bad, were repeated or went missing.

The code is the second reading of the pages: where a page left a byte order or a size open, the
code chose and the page was changed to say so. Firmware in C comes later and follows the same
layouts.
