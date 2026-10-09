<div align="center">

# Terem: why not

**The graveyard:** what was considered for the Hailos' chamber and the ROCK's supply and why it
is not used.

↑ [Terem](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Each entry says what it was and why it went, so that nobody digs it up without knowing.

- **A bought adapter with a supply of its own.** None was found: 2230/2242-to-2280 adapters are
  brackets or passive boards fed from the slot (Delock, Sintech and the like), and ADT-Link's
  powered risers go from an M.2 slot to a PCIe x4 or x16 card with a SATA or Molex plug. The
  nearest hack, a passive adapter with its 3.3 V trace cut and a regulator glued on, is a one-off
  for a trial, not a part.
- **The Hailos straight in the ROCK 5T's slots.** Both slots hang on one SY8113B buck of 3 A on
  the board, and two modules at their 5 W are 3 A: the *brutal* profile ran at that converter's
  edge. Terem gives each its own 2 A converter.
- **Feeding the slots' 3.3 V from outside.** A second regulator on the same 3.3 V would fight the
  board's: a synchronous buck held above its setpoint sinks current (the LMR43610's negative
  valley limit is −0.6 to −1 A in FPWM, SNVSBY5B). The edges' 3.3 V pins are left open instead.
- **Two sources OR-ed through ideal diodes,** the slot's 3.3 V and Terem's, so that a module would
  run from the slot without Terem. An LM66100 drops ~0.14 V at the module's 1.5 A and sits at
  its maximum; a controller with an external FET would do it, two of them, for a fallback that
  only matters when the battery is unplugged, when the backpack is off anyway.
- **An M.2 extender cable to Kormilica's socket** for the second Hailo. Cables and jumpers, and
  PCIe Gen 3 over 10 cm of FPC; Terem's traces are millimetres.
- **One adapter a slot,** two boards each with a 2242 socket and a 3.3 V input from Kormilica.
  One board in both slots takes the battery once, carries the eFuse too, and leaves no
  Kormilica with a ROCK. It stays the fallback should the slots not be coplanar.
- **A converter for the ROCK 5T.** Its DC jack takes 9–20 V, and the pack gives ~11.5–16 V; it
  runs straight from the battery through the eFuse.
- **A bare P-MOSFET as the ROCK 5T's switch.** At 16 V its gate needs a level shifter and a
  slow turn-on anyway, three or four parts with no current limit; the TPS26630 eFuse brings the
  limit, the soft start, the under- and overvoltage cutoffs and a shutdown pin in one part, and
  the branch is protected like every other.
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
- **Blade or glass fuses** anywhere on the battery: see
  [Babuška](../babuska/HARDWARE.md#power-variants).
