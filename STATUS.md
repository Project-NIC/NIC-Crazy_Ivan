<div align="center">

# Status

**Beta 0.1, 9 October 2026:** the whole design on paper, nothing built.

↑ [NIC-Crazy_Ivan](README.md)

</div>

---

This is a concept at the design stage. Every part has its pages, every frame, message and register
is written down, and the protocols run as Python code with tests; no board has been drawn and no
part has been bought. What is here comes from three kinds of source, and each page says which:

| kind | what it means | where it shows |
|---|---|---|
| **from a datasheet** | a figure read in the part's own document, cited by document, table or section | most numbers; the citation stands beside them |
| **computed on paper** | a figure derived from datasheet values: budgets, rates, dividers, corners, timing | the tables of currents, clocks and filters; the Python codecs check the byte layouts |
| **an estimate** | a figure with no source yet, marked as such | board stacks, cable capacitances, the ROCK 5T's consumption, the Hailo's heat |
| **awaiting measurement** | what only a sample or a board can tell | the open questions at the end of every page |

## What is closed

- the family of parts and what each does ([README](README.md), [NAMES](NAMES.md)),
- the suit's clock and every rate derived from it ([Mamka](mamka/HARDWARE.md#clock)),
- the lines, their frames, the channel from the master, the errors and the firmware updates
  ([Porjadok](porjadok/SOFTWARE.md)),
- the output stream, CI-BTP, packet by packet ([Porjadok](porjadok/SOFTWARE.md#output)),
- the sensing module, the IMU and the glove, pin by pin ([Rubaška](rubaska/HARDWARE.md)),
- Mamka, Nataša and Míša, pin by pin, the pins checked against the datasheets' tables,
- the power chain from the battery to every branch ([Babuška](babuska/README.md),
  [Terem](terem/README.md), [Kormilica](kormilica/README.md)),
- what Baťa does with the data ([signals](bata/SIGNALS.md)) and how he halts
  ([Storož](bata/SOFTWARE.md#storož)).

## What is open

Each page ends with its open questions. The largest:

- every figure marked *to be measured*: the cells' voltage at 20 and 80%, the ROCK 5T's
  consumption, the cable at 20 Mbaud, the electrodes' contact, the radar beside the EMG,
- datasheets not read: the Hailo-10H module's, the ICS-43434's, the BMS's manuals, the ROCK 5T's
  2D drawing,
- the clock trees and the DMA layouts of the five processors in STM32CubeMX,
- the model itself: its window and features are a first guess.

## What anyone can check

The pages cite their sources, so a reader with the datasheets can check any number; the Python
codecs under [software](software/README.md) run with no dependencies and show the frames byte by
byte. A wrong number, a misread datasheet or a broken link goes into
[Issues](https://github.com/Project-NIC/NIC-Crazy_Ivan/issues); a question, an alternative or
"we tried that and it failed" goes into
[Discussions](https://github.com/Project-NIC/NIC-Crazy_Ivan/discussions), where the graveyards,
the `WHY.md` pages, grow from. The design is published as it is, under the MIT licence, for
whoever finds it useful; it takes no side in anything but the engineering.
