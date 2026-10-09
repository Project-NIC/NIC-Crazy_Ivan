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

Babuška, [Mamka](../mamka/README.md), [Kormilica](../kormilica/README.md) or
[Terem](../terem/README.md), and [Baťa](../bata/README.md) ride in a bought backpack with a hard
shell, the kind made of two halves that open apart when it is unzipped.

- **A 3D-printed insert** holds everything in its place: the battery at the bottom, above it
  Baťa with Mamka and Kormilica, with a fan blowing through. The insert
  follows the computer, the Radxa ROCK 5T or the Raspberry Pi 5 (see
  [Baťa](../bata/HARDWARE.md#which-computer)). A home printer prints an insert; a whole
  backpack would take a large one.
- **One connector for the whole suit.** The suit comes off as a whole, so all five lines leave
  through one Amphenol **PT 24-61**, MIL-DTL-26482 Series 1: 61 contacts, a bayonet that locks
  in a quarter turn, IP67. Its receptacle sits on the right side of the shell and the plug
  (PT06A-24-61) on the suit's cable: one twist, and the backpack comes off. The five lines
  take 50 contacts and 11 are spare. The lines' 14-wire variant (see
  [Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit)) still takes 10 contacts a
  line: its doubled supply and ground wires go two into one contact, which the contacts carry
  easily at the line's fraction of an ampere. Plain PT plugs take solder-cup contacts, the PT-SE
  line crimped ones, and IP67 needs the environment-resisting version: the exact plug and
  receptacle are still to be chosen. Inside, a short harness joins it to Mamka's IDC headers.
- **One opening with a grommet** for other cables: the cable of the glasses passes through it
  and plugs in inside, its strain held there, so it stays an ordinary cable.
- The shell keeps the boards out of reach and the rain off. A plastic shell does not shield;
  the filtering rests on the boards (see [Mamka](../mamka/HARDWARE.md#filtering)).


## Heat

Worked out so far with the Raspberry Pi 5:

| source | power |
|---|---|
| Raspberry Pi 5 | 3–8.8 W |
| Hailo-10H | 2.5–5 W |
| Mamka's own 3.3 V: the two STM32H562s and the line drivers, ~0.5–0.6 A | ~1.5–2 W |
| the fan, the BMS | under 0.5 W |
| the converters (Mamka's LMR43610s, Kormilica's two LM61460 or Terem's two LMR43620) | ~1–3 W, an estimate from their efficiency, to check in their datasheets |
| **total** | **~8–19 W** |

- **Strips and wings:** the Raspberry Pi 5 with its Active Cooler, and Kormilica and Mamka on
  its header. Over the Raspberry Pi both are only strips with their headers; the rest reaches
  out past its edge on their wings, and on Kormilica's sits the Hailo-10H as an M.2 module (see
  [Kormilica](../kormilica/HARDWARE.md#the-hailo-10h)). Nothing lies over the Active Cooler or the
  Hailo.
- **What the makers say:** the Pi 5 slows its Arm cores down step by step from ~80 °C; at 85 °C both
  the Arm cores and the GPU are held back. Its firmware runs the Active Cooler in steps, each with
  5 °C of hysteresis: ~30% from 50 °C, ~50% from 60 °C, ~70% from 67.5 °C and full from 75 °C
  (`bcm2712-rpi-5-b.dts`, trip points and cooling levels 75/125/175/250). For the AI HAT+ 2, the
  same chip, a heatsink is advised for a continuous load, and the suit's load is continuous: the
  module gets one too.
- **The air:** the boards stand upright, parallel to the back, in a channel that the insert
  forms around them. The backpack's fan draws in low at the side, above the wall between the
  battery and the electronics, and blows up the channel; the air leaves at the top under the
  overhang, away from the back and the neck. It passes the Active Cooler, which draws from it
  and blows back into it, and the Hailo's heatsink, set with its fins along the flow. Warm air
  rises the same way, so the battery at the bottom stays cool.
- **A small fan does:** 2.4 l/s (~5 CFM) is the fan's figure in free air, and 15 W in it warm
  the air by ~5 K. The mesh, the fins and the outlet take part of the flow (Noctua gives a
  static pressure of only ~1.95 mm H₂O, ~19 Pa), so the air warms more, an estimate of ~7–10 K.
  The channel is as wide as the boards with Mamka's wing, ~90–100 mm, and at ~35 mm deep the
  air moves at ~0.7 m/s at most. The SoC is cooled by its Active Cooler, the Hailo by the
  channel, with no fan of its own; a measurement is to confirm it.
- **Fan control:** a 4-pin PWM fan, the Noctua NF-A4x10 5V PWM: 40 × 40 × 10 mm, 0.07 A, up to
  5,000 rpm and ~5 CFM in free air. It has its own driver, so Mamka needs no MOSFET or diode:
  Mamka's own 5 V converter feeds the fan (see [Mamka](../mamka/HARDWARE.md#mamkas-own-supply)), a
  timer gives PWM at 25 kHz and another reads the speed, two pulses a turn, so a stopped fan is
  noticed (see [Mamka](../mamka/HARDWARE.md#what-is-on-it)). At 0 %
  the fan stops, at 20 % it turns ~1,050 rpm. The computer sets the curve from the SoC's
  temperature, the Hailo's and the BMS's. If the fan stops, the computer lowers the Hailo's
  load; on the Raspberry Pi the Active Cooler, run by the Raspberry Pi itself, still cools the
  SoC.
- **With the ROCK 5T** the heat is still open. The board takes ~4–17 W and its two Hailos up to
  10 W (see [the battery](HARDWARE.md#the-battery)). Its SoC needs a cooler of its own (Radxa
  offers a passive heatsink, the 6240B, and one with a fan, the 4025A), and the two modules lie
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
