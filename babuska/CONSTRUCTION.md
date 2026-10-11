<div align="center">

# Babuška: construction

**The backpack:** the shell, the insert, the one connector of the whole suit, and the heat and the
air through it.

↑ [Babuška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## The backpack

The backpack is *Kommunalka*, Russian for a communal flat: the whole family lives in it and
shares one kitchen, Babuška.

Babuška, [Mamka](../mamka/README.md), [Terem](../terem/README.md) and [Baťa](../bata/README.md)
ride in a bought backpack with a hard shell, the kind made of two halves that open apart when it
is unzipped.

- **A 3D-printed insert** holds everything in its place: the battery at the bottom, above it the
  stack of Baťa with Mamka over him and Terem under him, ~110 × 82 × 68 mm, bare or in a perforated
  metal box of its size (see [Mamka](../mamka/CONSTRUCTION.md#the-stack)), with a fan blowing
  through. A home printer prints an insert; a whole backpack would take a large one.
- **One connector for the whole suit.** The suit comes off as a whole, so all five lines leave
  through one Amphenol **PT 24-61**, MIL-DTL-26482 Series 1: 61 contacts, a bayonet that locks in a
  quarter turn, IP67. Its receptacle sits on the right side of the shell and the plug (PT06A-24-61)
  on the suit's cable: one twist, and the backpack comes off. A line's sixteen wires (see
  [Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit)) take 11 contacts: the six of
  the three pairs, one for each doubled supply and three for the six grounds, two wires into one
  contact, which the contacts carry easily at the line's fraction of an ampere. The five lines take
  55 contacts and 6 are spare. Plain PT plugs take solder-cup contacts, the PT-SE line crimped ones,
  and IP67 needs the environment-resisting version: the exact plug and receptacle are still to be
  chosen. Inside, a short harness joins it to Mamka's IDC headers.
- **One opening with a grommet** for other cables: the cable of the glasses passes through it
  and plugs in inside, its strain held there, so it stays an ordinary cable.
- The shell keeps the boards out of reach and the rain off. A plastic shell does not shield;
  the filtering rests on the boards (see [Mamka](../mamka/HARDWARE.md#filtering)).


## Heat

Worked out from the parts' own figures; with the ROCK 5T it is still open:

| source | power |
|---|---|
| the ROCK 5T | ~4–17 W |
| Hailo-10H, none, one or two | 0–16.5 W, 8.25 W each at most (Hailo's datasheet) |
| Mamka's own 3.3 V: the two STM32H562s and the line drivers, ~0.5–0.6 A | ~1.5–2 W |
| the fan, the BMS, the eFuses | under 1 W |
| the converters (Mamka's LMR43610s, Terem's two LMR60440) | ~1–3 W, an estimate from their efficiency, to check in their datasheets |
| **total** | **~7–40 W** |

- **The stack:** the SoC under Radxa's 6240B with its own fan, ~13.5 mm of air between it and Mamka
  over it; the Hailos under one heatsink, a Fischer ICK S 45 × 45 × 20, on Terem's side (see
  [Mamka](../mamka/CONSTRUCTION.md#the-stack)).
- **What the makers say:** for the AI HAT+ 2, the Hailo-10H on a Raspberry Pi, a heatsink is
  advised for a continuous load, and the suit's load is continuous: both modules get one, the
  shared heatsink on Terem.
- **The air:** the boards stand upright, parallel to the back, in a channel that the insert forms
  around them. The backpack's fan draws in low at the side, above the wall between the battery and
  the electronics, and blows up the channel; the air leaves at the top under the overhang, away from
  the back and the neck. It passes the SoC's cooler, its fins along the flow, and the Hailos' pin
  heatsink, which takes it from any side. Warm air rises the same way, so the battery at the bottom
  stays cool.
- **A small fan does:** 2.4 l/s (~5 CFM) is the fan's figure in free air, and 15 W in it warm
  the air by ~5 K. The mesh, the fins and the outlet take part of the flow (Noctua gives a
  static pressure of only ~1.95 mm H₂O, ~19 Pa), so the air warms more, an estimate of ~7–10 K.
  The channel was drawn ~90–100 mm wide and ~35 mm deep for the Raspberry Pi of version 0.1,
  where the air moved at ~0.7 m/s at most; for the stack's 110 × 82 × 68 mm it is to be drawn
  again. The SoC is cooled by its own cooler, the Hailos by the
  channel, with no fan of their own; a measurement is to confirm it.
- **Fan control:** a 4-pin PWM fan, the Noctua NF-A4x10 5V PWM: 40 × 40 × 10 mm, 0.07 A, up to
  5,000 rpm and ~5 CFM in free air. It has its own driver, so Mamka needs no MOSFET or diode:
  Mamka's own 5 V converter feeds the fan (see [Mamka](../mamka/HARDWARE.md#mamkas-own-supply)), a
  timer gives PWM at 25 kHz and another reads the speed, two pulses a turn, so a stopped fan is
  noticed (see [Mamka](../mamka/HARDWARE.md#what-is-on-it)). At 0 %
  the fan stops, at 20 % it turns ~1,050 rpm. The computer sets the curve from the SoC's
  temperature, the Hailo's and the BMS's. If the fan stops, the computer lowers the Hailos'
  load.
- **Both sides:** the board takes ~4–17 W and its two Hailos up to 16.5 W (see
  [the battery](HARDWARE.md#the-battery)). The SoC's cooler is on top and the two modules lie
  on its underside, so the channel has to reach both of its sides.
- **Sun:** a light-coloured shell. In the sun a dark one could come near the 40 °C and 50 °C the
  BMS allows for charging and discharging.
- **Dust and rain:** the intake behind fine mesh, the outlet under an overhang.


## Open questions

- the backpack: which shell, the insert with its channel, the vents and the fan's real flow
  through them; the converters' losses from their datasheets,
- the backpack's heat with the ROCK 5T: its cooler, its underside with the two Hailos, the
  channel around both sides,
- the PT 24-61: the exact plug and receptacle (solder cups or the crimped PT-SE, the sealed
  version for IP67), its contacts against our 28 AWG wire, and which contact carries what.
