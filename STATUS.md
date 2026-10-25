<div align="center">

# Status

**Beta 0.4, 25 Oct 2026:** the purpose and the requirements written down, the protocol built
around frames of fixed length, eight lines by the suit's pieces, the layout on the body for both
ways of measuring, drawn, the battery on LiFePO4; still all on paper, nothing built.

↑ [NIC-Crazy_Ivan](README.md)

</div>

---

This is a concept at the design stage. Every part has its pages, every frame, message and register
is written down, and the protocols run as Python code with tests; no board has been drawn and no
part has been bought. What is here is of four kinds, and each page says which:

| kind | what it means | where it shows |
|---|---|---|
| **from a datasheet** | a figure read in the part's own document, cited by document, table or section | most numbers; the citation stands beside them |
| **computed on paper** | a figure derived from datasheet values: budgets, rates, dividers, corners, timing | the tables of currents, clocks and filters; the Python codecs check the byte layouts |
| **an estimate** | a figure with no source yet, marked as such | board stacks, cable capacitances, the ROCK 5T's consumption, the Hailo's heat |
| **awaiting measurement** | what only a sample or a board can tell | the open questions at the end of every page |

## In 0.4

- the purpose and the requirements written down: first a controller, second rehabilitation,
  the assistants beside them, how we know it works, and what it must do in ranges
  ([README](README.md#what-it-is-for)),
- **two frames inside the suit, 34 B and 8 B,** each kind of one length, the unit's number, the
  kind and the cycle's number in every one: a unit's data, its diagnostics every 32 cycles, the
  commands and their answers; a frame of 519 B for firmware and one of 198 B for the sound; no
  repeat for data ([Porjadok](porjadok/SOFTWARE.md#the-frames)),
- **eight lines, one a piece of the suit,** all at 19.66 Mbaud, four slots of 128 B on lines 1–7
  and two of 256 B on line 8: the limbs on
  lines 1–4 and Mamka's processor 1, the shoulders with the arms, the head and the trunk on lines
  5–7 and processor 2, Nataša and Míša on line 8, which runs by its slots always
  ([Porjadok](porjadok/HARDWARE.md#links-between-boards)),
- two modes: the service mode from power-on, *discover* and *assign* by the whole UID, then the
  bus test, *get ready* and *start*; the suit clock on every line from the start; the ADS1299s on
  idle through the whole active mode; Mamka's heartbeat
  ([Porjadok](porjadok/SOFTWARE.md#the-modes)),
- nothing kept in a unit's flash but its firmware: the map and every setting on Baťa, keyed by
  the unit's UID ([Baťa](bata/SOFTWARE.md#the-map)); firmware in the service mode, broadcast in
  blocks of 512 B, the missing ones asked again
  ([updating](porjadok/SOFTWARE.md#updating-firmware)),
- three SPIs to Baťa: processor 1's at 37.5 MHz, processor 2's two at 11.1 MHz behind the ROCK's
  translators, the frames as they came in places of 34 B; four wires between the processors, her
  own registers, the BMS a chip of processor 2 ([Mamka](mamka/SOFTWARE.md)),
- **Bogatyr,** the layout on the body: 16 modules of 16 electrodes, a bias and a reference electrode
  each, 288 in all, for the differential way and against the reference, every muscle with its pair;
  48 IMUs on the body, more where the skin slides; a proposal from several studies, to be gone
  through with a physiotherapist, drawn on an average body as a first draft
  ([Bogatyr](bogatyr/README.md)),
- **the glove, Vešč:** its Staršaja on the sleeve, five Bratiški, one a finger, 20 IMUs, eight
  wires across the wrist, a unit on its arm's line and part of every suit with arms
  ([Rubaška](rubaska/HARDWARE.md#the-glove)),
- line 8 by its slots always, each unit on a timer of its own, Mamka's heartbeat the correction:
  the sound in packets of 198 B with a buffer at each end, Nataša's frames, the motors as a chip,
  Nataša optional ([Nataša](natasa/SOFTWARE.md)); Míša a unit of his own on his own tap, on the
  suit's clock with no oscillator of his own, his sphere a chip of its own
  ([Míša](misa/SOFTWARE.md)),
- CI-BTP in three classes and four rates, its meta packets by the map, the live output alone;
  recordings only when asked, in BDF
  ([output](porjadok/SOFTWARE.md#ci-btp)),
- the units' cores at 49.152 MHz, the lines on a PLL of their own
  ([Porjadok](porjadok/SOFTWARE.md#the-clock-tree)),
- the EMG at 3,840 SPS, 1,920 SPS a setting to try
  ([Rubaška](rubaska/SOFTWARE.md#the-ads1299s-settings)),
- a connector a branch in the backpack, the Weipu SP21, and a cable of 14 wires
  ([Porjadok](porjadok/HARDWARE.md#cable-and-connectors-in-the-suit)),
- the battery on LiFePO4, the EVE C40 in 4S1P the first candidate ([Babuška](babuska/HARDWARE.md)),
- Terem for 2280 cards, the Hailo-10H with 8 GB, its board an L under the ROCK, read from Radxa's
  3D model, with windows over the ROCK's tallest parts ([Terem](terem/CONSTRUCTION.md#the-board)),
- the names by family ties: Borovičok, the Bratiški, Staršaja every sensing unit's main
  processor, Kormilica Mamka's power section ([NAMES](NAMES.md)),
- the codecs and the simulator for all of it ([software](software/protocol/README.md)).

## What is closed

- the family of parts and what each does ([README](README.md), [NAMES](NAMES.md)),
- the suit's clock and every rate derived from it ([Mamka](mamka/HARDWARE.md#clock)),
- the lines, the frames, the frames down and the registers, the errors and the firmware updates
  ([Porjadok](porjadok/SOFTWARE.md)),
- the output stream, CI-BTP, packet by packet ([Porjadok](porjadok/SOFTWARE.md#output)),
- the sensing module and the IMU, pin by pin ([Rubaška](rubaska/HARDWARE.md)), and their analog
  side: the gain, the input filter, the noise, the right-leg drive,
- how the units start, their clocks, their DMA and their interrupts
  ([Porjadok](porjadok/SOFTWARE.md#bring-up)),
- Mamka, Nataša and Míša, pin by pin, the pins checked against the datasheets' tables, a
  new plain GPIO chosen when a board is drawn,
- the power chain from the battery to every branch ([Babuška](babuska/README.md),
  [Mamka](mamka/HARDWARE.md#the-computers-supply), [Terem](terem/README.md)),
- what Baťa does with the data ([signals](bata/SIGNALS.md)) and how he halts
  ([Storož](bata/SOFTWARE.md#storož)).

## What is open

Each page ends with its open questions. The largest:

- every figure marked *to be measured*: the pack's voltage at 20 and 80%, the ROCK 5T's
  consumption, the cable at 20 Mbaud, the electrodes' contact, the radar beside the EMG, the
  SPIs behind the ROCK's translators at 11.1 MHz,
- the top at 80% on LiFePO4's flat curve: the BMS's count or a full charge,
- the glove's wires, what they carry and their rate, set on the first board; Staršaja's pins and
  the Bratiški's AFs; what Baťa's application for the map shows and asks,
- datasheets not read: the BMS's manuals,
- the clock trees and the DMA tables of the six processor designs, written on paper, checked on
  the first board,
- the layout on the body, gone through with a physiotherapist and tried on a body, the two ways
  of measuring compared on one arm ([Bogatyr](bogatyr/CONSTRUCTION.md#open-questions)); the steel
  studs against Ag/AgCl and titanium; the flexible and stretchable strips, washed and worn,
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
