<div align="center">

# Babuška: construction

**The backpack:** the shell, the insert, a connector for each piece of the suit, and the heat
and the air through it.

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
- **A connector for each piece of the suit,** eight in the shell, one a line: the arms with
  their shoulders, the legs, the head's module, the chest, the back, and the headband (see
  [Porjadok](../porjadok/HARDWARE.md#links-between-boards)), so a piece comes off by itself. A
  line's 16 wires (see [Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit)) take
  10 contacts: the six of the three pairs and four for the supply, 4 V, 6 V and two grounds, the
  doubled wires sharing a contact, which a contact carries easily at the line's fraction of an
  ampere.
  The connector is the **Weipu SP21 of 12 pins,** IP68, 5 A, screwed on, two pins spare; the
  GX16 of 10 pins for the first trials. Inside, a short harness joins each to its IDC header on
  Mamka.
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
| Mamka's own 3.3 V: the two STM32H562s and the line drivers, ~0.72–0.77 A | ~2.4–2.5 W |
| the fan, the BMS, the eFuses | under 1 W |
| the converters (Mamka's LMR43610s, Terem's two LMR60440) | ~1–3 W, an estimate from their efficiency, to check in their datasheets |
| **total** | **~8–40 W** |

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
- **A small fan does:** 2.4 l/s (~5 CFM) is the fan's figure in free air, and 15 W in it warm the
  air by ~5 K. The mesh, the fins and the outlet take part of the flow (Noctua gives a static
  pressure of only ~1.95 mm H₂O, ~19 Pa), so the air warms more, an estimate of ~7–10 K. The channel
  is to be drawn for the stack's 110 × 82 × 68 mm. The SoC is cooled by its own cooler, the Hailos
  by the channel, with no fan of their own; a measurement is to confirm it.
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
- the pieces' connectors, the Weipu SP21: their contacts against our 28 AWG wire, which contact
  carries what, and where the eight sit on the shell.
