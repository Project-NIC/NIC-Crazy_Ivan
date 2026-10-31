<div align="center">

# Status

**Beta 0.6, 31 Oct 2026:** every module on the ADS1298, the IMU the LSM6DSV16X held to the suit's
clock by a reference, the strips polyimide shielded on both faces, the units potted on the harness
with connectors for assembly only, Mamka's converters at 1 MHz, Mrazík the cooling block; 280
channels at 1,920 SPS and 98 IMUs, still all on paper, nothing built.

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

## In 0.6

- **the suit's IMU, the LSM6DSV16X,** held to the suit's clock by a reference on INT2, 24 or 15 Hz
  from the suit clock, its 1.6 kHz setting at 1,920 Hz; two a bus by their addresses; the IMU board
  with what ST asks and 1 kΩ on INT2 ([Rubaška](rubaska/HARDWARE.md#the-imu)),
- **the ADS1298 on every module,** the head and the neck too: one chip, one board, one firmware; a
  reference electrode wired on its strip where a strip wants one
  ([Rubaška](rubaska/HARDWARE.md#sensing-module)),
- **the modules' analog supply on the LP2985,** and an RC at every input where a cable arrives
  ([Rubaška](rubaska/HARDWARE.md#power)),
- **the strips polyimide everywhere,** the limbs too: the strip does not stretch, an elastic gap in
  the fabric does; two or three short strips a module; four layers, the leads between two grounds,
  the layer driven at the body's common mode by a TLV9001S, a follower's place at every stud under a
  0 Ω part ([Rubaška](rubaska/HARDWARE.md#the-strips-ground-layer)),
- **connectors for assembly and repair only:** the units potted whole in a gel on Kaščej, which is
  rinsed while the clothes are washed, **Strejda Al** the compression overall over it; the line on
  Picoflex in tin, a tap anywhere on the cable; the strips and the IMU boards on connectors on the
  first arm, soldered in a series
  ([Porjadok](porjadok/HARDWARE.md#cable-and-connectors-in-the-suit),
  [Rubaška](rubaska/CONSTRUCTION.md#harness-and-washing)),
- **the finger strips** polyimide meanders soldered to the IMUs' boards
  ([Rubaška](rubaska/CONSTRUCTION.md#the-glove)),
- **Mamka's converters at 1 MHz,** forced PWM on the 6 V; her processors the STM32H562VG or H563VG;
  the eFuse in front of each ROCK the TPS259474 ([Mamka](mamka/HARDWARE.md#converters)),
- **Mrazík,** the cooling: a closed aluminium block, IP55, around the ROCK with Mamka over it and
  Terem or a plate under it, a boss to the SoC through a window in Mamka, the fans outside on its
  fins; its closure comes with the schematics ([Babuška](babuska/CONSTRUCTION.md#mrazík)),
- every board's parts gone through for price, JLCPCB's basic parts first,
- **two ADS1298 a module** in cascade on one SPI, 16 channels on 32 electrodes, the neck's one chip;
  with the gloves' and the socks' 280 channels, 582 electrodes; the bias electrode straight on the
  first chip's RLDOUT, no switch ([Rubaška](rubaska/HARDWARE.md#sensing-module)),
- **1,920 SPS the rate,** the professionals', 3,840 the setting to try; the step 16 samples,
  120 Hz; one frame of data a unit, 58 B for a module of two chips, 0x24, and for the glove and the
  sock, 0x25, 34 B for the rest; the diagnostics for 16 channels; 1,064 B a cycle to Baťa from
  processor 1, 384 B from processor 2
  ([Porjadok](porjadok/SOFTWARE.md#a-units-data)),
- **the inputs:** one 4.99 kΩ a lead, one 220 pF C0G a channel, empty places for 10 pF, no TVS, a
  discharge computed ([Rubaška](rubaska/HARDWARE.md#sensing-module)),
- **the glove, Vešč, one board on the back of the hand:** the hand's ADS1298, 16 electrodes on 8
  channels, Staršaja and four Bratiški, one a finger, 20 IMU places, the finger strips passive;
  **the sock, Nosok,** the same board for the foot on the calf above the ankle, up to eight IMUs:
  98 IMUs on a suit with two gloves and two socks, 42 of them on the modules
  ([Rubaška](rubaska/HARDWARE.md#the-glove)),
- the purpose and the requirements written down: first a controller, second rehabilitation,
  the assistants beside them, how we know it works, and what it must do in ranges
  ([README](README.md#what-it-is-for)),
- **frames of fixed lengths inside the suit, 34 B and 8 B,** each kind of one length, the unit's
  number, the kind and the cycle's number in every one: a unit's data, its diagnostics every 32
  cycles, the commands and their answers; a frame of 58 B for a module of two chips' data, one of
  519 B for firmware and one of 198 B for the sound; no repeat for data
  ([Porjadok](porjadok/SOFTWARE.md#the-frames)),
- **eight lines, one a piece of the suit,** all at 19.66 Mbaud, four slots of 128 B on lines 1–7
  and two of 256 B on line 8: the limbs on
  lines 1–4 and Mamka's processor 1, the shoulders with the arms, the head and the trunk on lines
  5–7 and processor 2, Nataša and Míša on line 8, which runs by its slots always
  ([Porjadok](porjadok/HARDWARE.md#links-between-boards)),
- two modes: the service mode from power-on, *discover* and *assign* by the whole UID, then the
  bus test, *get ready* and *start*; the suit clock on every line from the start; the ADS129x on
  idle through the whole active mode; Mamka's heartbeat
  ([Porjadok](porjadok/SOFTWARE.md#the-modes)),
- every processor watching itself alike, nothing added to the boards: the independent watchdog
  fed only when every task has run, the brownout reset and the voltage detector, ECC on the flash
  and the SRAM, the stack's limit, the clock's security, the last reset's cause in the
  diagnostics; Baťa on the RK3588's watchdog, starting halted after an unclean stop
  ([Porjadok](porjadok/SOFTWARE.md#watchdogs), [Storož](bata/SOFTWARE.md#storož)),
- nothing kept in a unit's flash but its firmware: the map and every setting on Baťa, keyed by
  the unit's UID ([Baťa](bata/SOFTWARE.md#the-map)); firmware in the service mode, broadcast in
  blocks of 512 B, the missing ones asked again
  ([updating](porjadok/SOFTWARE.md#updating-firmware)),
- three SPIs to Baťa: processor 1's at 37.5 MHz, processor 2's two at 11.1 MHz behind the ROCK's
  translators, the frames as they came in places by the unit's kind, 58 or 34 B; four wires between
  the processors, her own registers, the BMS a chip of processor 2 ([Mamka](mamka/SOFTWARE.md)),
- **Bogatyr,** the layout on the body: the first eight channels of every module, every muscle with
  its pair, the second eight of the body's modules still to lay out; 42 IMUs on the body, four in a
  square on the head, more where the skin slides; a proposal from several studies, to be gone
  through with a physiotherapist, drawn on an average body as a first draft
  ([Bogatyr](bogatyr/README.md)),
- **the Bratiški without SWD:** chips of their Staršaja, not units, each on a full-duplex link of
  4 MBd on the board, his step of 52 B once a step; an empty STM32H503 boots ST's bootloader on
  the same pins, so Staršaja programs them herself, a shared BOOT0 line for recovery; the glove
  a unit on its arm's line and part of every suit with arms, its Staršaja the module's own part
  in UFQFPN48 ([Rubaška](rubaska/SOFTWARE.md#the-bratiški)),
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
- a connector a branch in the backpack, the Weipu SP21, and a flat cable of 16 wires, the 3M 3811
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
  side: the gain, the input filter, the noise, the right-leg drive, the strip's ground layer,
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
- the glove's board on the back of the hand: Staršaja's pins in UFQFPN48 against the datasheet's
  tables, the Bratiški programmed through the bootloader, on the first board; Mamka's eight line
  headers, which do not fit one edge: two rows or a smaller IDC,
- datasheets not read: the BMS's manuals,
- the clock trees and the DMA tables of the six processor designs, written on paper, checked on
  the first board,
- the layout on the body, gone through with a physiotherapist and tried on a body: the body's
  modules' second eight channels, the two ways of measuring compared on the head and the neck
  ([Bogatyr](bogatyr/CONSTRUCTION.md#open-questions)); first the hand: its eight channels and its
  IMUs on one inner layer under the board, and how many channels the thumb wants, asked before any
  glove is made; the foot's eight channels and the sock's places on the foot; the steel discs
  against Ag/AgCl, titanium and conductive silicone; the polyimide strips, washed and worn,
- the four-layer strip's own artifact and its ground layer on ground and driven, on the first arm;
  the powered-down bias output's leakage, the LP2985's noise with the inputs shorted inside, the
  IMUs' reference on INT2 and its 1 kΩ, on the first module; the glove on two Bratiški of eight
  IMUs, two SCL branches a finger, to be tried there,
- the backpack's heat with the *brutal* fitting, up to ~40 W; Mrazík's closure, the Hailos' path to
  its wall and its fans, drawn with the schematics ([Babuška](babuska/CONSTRUCTION.md#mrazík));
  Mamka's converters free near 1 MHz against the ADS1298's 983.04 kHz, and the 6 V starting into
  ~0.8–1.0 mF ([Mamka](mamka/HARDWARE.md#converters)),
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
