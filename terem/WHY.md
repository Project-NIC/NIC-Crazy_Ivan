<div align="center">

# Terem: why not

**The graveyard:** what was considered for the Hailos' chamber and why it is not used.

↑ [Terem](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Each entry says what it was and why it went, so that nobody digs it up without knowing.

- **A bought adapter with a supply of its own.** None was found: 2230/2242-to-2280 adapters are
  brackets or passive boards fed from the slot (Delock, Sintech and the like), and ADT-Link's
  powered risers go from an M.2 slot to a PCIe x4 or x16 card with a SATA or Molex plug. The
  nearest hack, a passive adapter with its 3.3 V trace cut and a regulator glued on, is a one-off
  for a trial, not a part.
- **The Hailos straight in the ROCK 5T's slots.** Both slots hang on one SY8113B buck of 3 A on the
  board (Silergy, AN_SY8113B Rev 0.1), and two modules at 5 W are 3 A and at the datasheet's 8.25 W
  ~5 A: the *brutal* profile ran past that converter's limit. Terem gives each its own converter.
- **The LMR43620,** the 2 A member of Mamka's LMR436x0 family, first chosen here. 2 A of 3.3 V,
  ~6.6 W, is short of the Hailo-10H's 8.25 W at its most (Hailo's datasheet Rev. 1.0, 3.1); the
  LMR60440 gives 4 A in a package of 2.5 × 2 mm at the same ~2 MHz, sleeps at 0.65 µA and needs no
  divider in its fixed-3.3 V variant (SNAS877).
- **The LMR33640,** also 4 A: 400 kHz or 1 MHz only, an HSOIC-8 of 5 × 4 mm and 5 µA asleep
  (SNVSB99C), all worse for Terem than the LMR60440.
- **Feeding the slots' 3.3 V from outside.** A second regulator on the same 3.3 V would fight the
  board's: a synchronous buck held above its setpoint sinks current (the LMR60440's negative
  limit is −1.0 to −2.2 A in FPWM, SNAS877 6.5). The edges' 3.3 V pins are left open instead.
- **Two sources OR-ed through ideal diodes,** the slot's 3.3 V and Terem's, so that a module would
  run from the slot without Terem. An LM66100 is made for 1.5 A at most (SLVSEZ8A), short of the
  module's ~2.5 A; a controller with an external FET would do it, two of them, for a fallback that
  only matters when the battery is unplugged, when the backpack is off anyway.
- **An M.2 extender cable to Kormilica's socket** for the second Hailo (the old Kormilica, the
  Raspberry Pi's board, is retired, see [Baťa](../bata/WHY.md#the-computers)). Cables and jumpers,
  and PCIe Gen 3 over 10 cm of FPC; Terem's traces are millimetres.
- **Sockets for 2242** (to 25 Oct 2026): Terem as long as the ROCK's slots, but a 2242 module on
  it, the short card in the long board. Terem was meant for 2280 from the start, the 8 GB Hailo
  comes in 2280 only so far, and a 2280 card fits by reaching ~7.5 mm past the ROCK's standoffs
  (see [construction](CONSTRUCTION.md#the-board)).
- **One hole for two screws,** the card's and Terem's into the same standoff of the ROCK, which
  would have needed a split hole. The card's screw falls ~7.5 mm past the ROCK's, so each has its
  own hole (the owner).
- **One adapter a slot,** two boards each with a socket and a 3.3 V input of its own. One
  board in both slots takes the battery once, and the slots are coplanar (Radxa's 2D drawing,
  see [HARDWARE](HARDWARE.md#the-two-slots)), so the fallback is not needed.
- **The ROCK's eFuse on Terem.** It made Terem the ROCK's supply too, so a ROCK without Hailos,
  running its model on the RK3588's own NPU, or Borovičok with an SSD in his slot, would have
  needed a Terem only to be switched. The eFuse sits on Mamka, who switches the computers
  anyway (see [Mamka](../mamka/HARDWARE.md#the-computers-supply)); Terem is the Umnicas' alone.
- **Cutting the slot rail to stop a faulty module.** The ROCK can drop its PCIe 3.3 V by
  GPIO1_A4, but one rail feeds both slots, so both Umnicas would go. A faulty module is already
  held by its own converter's limit; its own EN from the ROCK does one module at a time.
- **EN from the slot's 3.3 V, with a one-way KILL transistor.** The first design: 10 kΩ from
  the edge's 3.3 V to EN, 100 kΩ to ground, and a 2N7002 on EN that a ROCK pin could pull down,
  so that a module could never run without a live slot. The device tree does the same with no
  parts: Terem's converter is a GPIO regulator whose supply is the slot rail, and the PCIe
  driver enables it and times PERST# itself. The transistor went.
- **EN of both converters from Mamka.** She would have to know when the ROCK's PCIe is up and
  when its driver wants the module, which only the ROCK knows; and the ROCK has the pins.
- **PGOOD through the slot itself.** The M.2 edge has no spare pin the ROCK reads: pins 10
  (DAS/DSS#) and 68 (SUSCLK) are unconnected on the ROCK 5T (schematic V1.2), and PEWAKE# is the
  module's own line. PGOOD goes to the header through Mamka's traces instead.
- **A two-layer board.** The board is small and the parts are few, but on 0.8 mm of FR4 an
  85 Ω pair needs traces over a millimetre wide, which do not fit the 0.5 mm pitch of the
  fingers, so the ten pairs would run at an impedance nobody chose and the links might train at
  Gen 3, at Gen 2, or not at all. Four layers at 0.8 mm cost a few euros more and take the
  gamble out (see [CONSTRUCTION](CONSTRUCTION.md#the-board)).
- **A heatsink held to the ROCK's corner holes,** the first plan for the Hailos: a plate over
  both modules on spacers to the stack's four screws. The holes lie at the ROCK's corners, 49 and
  57 mm apart, three of them far from Terem, so the plate would be a bracket made to measure.
  The ICK S 45 × 45 × 20 screws to Terem itself (see [construction](CONSTRUCTION.md)).
- **A heatsink glued across both modules,** on Fischer's adhesive foil: no holes, but neither
  module would then come out alone. Two screws with springs hold it instead.
