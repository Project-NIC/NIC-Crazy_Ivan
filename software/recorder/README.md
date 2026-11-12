# The recorder

**Baťa's recorder:** Mamka's two processors' transfers in, the samples as the chips gave them out
into BDF+, made only when asked ([Baťa](../../bata/SOFTWARE.md),
[Porjadok](../../porjadok/SOFTWARE.md#ci-btp)). Python 3, the standard library only; the codecs
are the protocol's ([protocol](../protocol/README.md)).

| file | what is in it |
|---|---|
| `recorder/table.py` | the units of a run, one JSON file, `table.json`, as the simulator writes it |
| `recorder/bdf.py` | BDF+ written record by record and read back: the header, 24-bit samples, the annotations as EDF+'s TALs |
| `recorder/record.py` | the transfers put together cycle by cycle by the frames' number; every EMG channel at 1,920 SPS in µV, every IMU's step at 120 Hz in °/s and g; a lost frame held and marked as a gap; Mamka's events marked |
| `tests/` | BDF+ round trips and limits, the samples as the frames carried them, the gaps, the whole suit, a reading by EDFlib where pyedflib is installed |

A second of the simulated suit, then its recording:

```
cd ../protocol && python3 -m suitsim --seconds 3 --bad 0.001 --out /tmp/sim && cd ../recorder
python3 -m recorder --table /tmp/sim/table.json --spi1 /tmp/sim/spi1.bin \
    --spi2 /tmp/sim/spi2.bin --out /tmp/rec.bdf
python3 -m unittest discover -s tests -t .
```

- **What is written:** the units asked for (`--units 0x61,0x62`; all the sensing ones if none),
  their EMG and their IMUs (`--no-imu` for the EMG alone). A file holds at most 639 signals and
  the annotations', EDFlib's limit, which pyedflib keeps; the whole suit, 280 channels and 108
  IMUs' six values, goes into two files, `rec.bdf` and `rec-2.bdf`, whole units in each.
- **The scales:** the EMG ±333,333 µV over the chip's 24 bits, ±VREF / gain at 4 V and 12; the
  IMU's turn a step's mean rate at 70 mdps/LSB, its force the mean at 0.488 mg/LSB (DS13510 Rev
  4, table 3), each a 16-bit value in a 24-bit sample.
- **A gap,** a frame that did not come, holds the unit's last samples and is written as an
  annotation, `gap 61` with its onset and length, so nobody takes the held samples for the
  body's; a gap open at a second's end is written to it and opened again, so every annotation
  lies in its own record. Mamka's events are written into every file.
- **The start** is a step's first cycle, so the IMUs' steps line up with the records. A unit
  sends a step's turn in the step after it, so each step is written where it was measured and a
  second is written a step after its end; the last second's last step is held, the part of a
  second after it not written.
- **Live:** Baťa's two SPIs in place of the files come with the first Mamka. A second of the
  whole suit takes ~0.45 s here; on the ROCK it is to be measured.
