<div align="center">

# Status

**Beta 0.3, 11 October 2026:** the whole design on paper, the analog side too, nothing built.

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

## New in 0.3

- the digital side closed on paper: how the units are found and numbered at start, the clock
  straight from the oscillator, the clock trees, the DMA and the interrupts of every processor
  ([Porjadok](porjadok/SOFTWARE.md#bring-up), [the clock tree](porjadok/SOFTWARE.md#the-clock-tree),
  [the GPDMA](porjadok/SOFTWARE.md#the-gpdma), [interrupts](porjadok/SOFTWARE.md#interrupts)),
- the digital rail at 4 V, at least 3.64 V at a module's regulator at the worst corner
  ([Porjadok](porjadok/HARDWARE.md#end-to-end)),
- the analog side: a gain of 12 for the electrodes' offset, the offset and the electrodes'
  prices, a noise budget, 8 and 6 mm studs in moist rings
  ([Rubaška](rubaska/HARDWARE.md#the-noise), [construction](rubaska/CONSTRUCTION.md#electrodes)),
- no cables to the electrodes: the torso's strips flexible circuits, the limbs' and the glove's
  stretchable ones, the stud pressed through a gold pad with a spring and a sealant,
- the electrodes laid out by muscles, a "tomography" in quotes: two rings on each limb, the
  torso in eight areas with the channels crossing them, the hand and the foot in pairs, drawn on
  an average body ([concept](rubaska/concept.png)); whether it works is not known,
- the reference electrode without a switch, not fitted on the suit; the unit stays universal,
- the hardware design under the CERN-OHL-P v2 ([LICENSE-HW](LICENSE-HW)), the software still
  under MIT,
- the assistants on the processor's cores ([Soňa](sona/README.md), [Taťána](tatana/README.md),
  [Nikita](nikita/README.md), [Pomoščnik](pomoscnik/README.md)), the Hailos under one heatsink
  ([Terem](terem/README.md)).

## What is closed

- the family of parts and what each does ([README](README.md), [NAMES](NAMES.md)),
- the suit's clock and every rate derived from it ([Mamka](mamka/HARDWARE.md#clock)),
- the lines, their frames, the channel from the master, the errors and the firmware updates
  ([Porjadok](porjadok/SOFTWARE.md)),
- the output stream, CI-BTP, packet by packet ([Porjadok](porjadok/SOFTWARE.md#output)),
- the sensing module, the IMU and the glove, pin by pin ([Rubaška](rubaska/HARDWARE.md)), and
  their analog side: the gain, the input filter, the noise, the right-leg drive,
- how the units start, their clocks, their DMA and their interrupts
  ([Porjadok](porjadok/SOFTWARE.md#bring-up)),
- Mamka, Nataša and Míša, pin by pin, the pins checked against the datasheets' tables,
- the power chain from the battery to every branch ([Babuška](babuska/README.md),
  [Mamka](mamka/HARDWARE.md#the-computers-supply), [Terem](terem/README.md)),
- what Baťa does with the data ([signals](bata/SIGNALS.md)) and how he halts
  ([Storož](bata/SOFTWARE.md#storož)).

## What is open

Each page ends with its open questions. The largest:

- every figure marked *to be measured*: the cells' voltage at 20 and 80%, the ROCK 5T's
  consumption, the cable at 20 Mbaud, the electrodes' contact, the radar beside the EMG,
- datasheets not read: the Hailo-10H 2242's (the 2280's is read), the BMS's manuals,
- the clock trees and the DMA tables of the six processor designs, written on paper, checked on
  the first board,
- the electrodes' layout, checked against SENIAM and an atlas, tried on a body, and its crossed
  pairs against neighbouring ones on one arm; the steel studs against Ag/AgCl and titanium; the
  flexible and stretchable strips, washed and worn,
- the backpack's heat with the *brutal* fitting, up to ~40 W against a fan drawn for 15 W
  ([Babuška](babuska/CONSTRUCTION.md#heat)),
- the model itself: its window and features are a first guess.

## What anyone can check

The pages cite their sources, so a reader with the datasheets can check any number; the Python
codecs under [software](software/README.md) run with no dependencies and show the frames byte by
byte. A wrong number, a misread datasheet or a broken link goes into
[Issues](https://github.com/Project-NIC/NIC-Crazy_Ivan/issues); a question, an alternative or "we
tried that and it failed" goes into
[Discussions](https://github.com/Project-NIC/NIC-Crazy_Ivan/discussions), where the graveyards, the
`WHY.md` pages, grow from. The design is published as it is, the software under the MIT licence and
the hardware under the CERN-OHL-P v2, for whoever finds it useful; it takes no side in anything but
the engineering.
