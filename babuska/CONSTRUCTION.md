<div align="center">

# Babuška: construction

**The backpack:** the shell, the insert, a connector for each piece of the suit, Mrazík round
the computers, and the heat and the air through it.

↑ [Babuška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## The backpack

The backpack is *Kommunalka*, Russian for a communal flat: the whole family lives in it and
shares one kitchen, Babuška.

Babuška, [Mamka](../mamka/README.md), [Terem](../terem/README.md) and [Baťa](../bata/README.md) ride
in a bought backpack with a hard shell, its back panel held off the back on a mesh or over a channel
along the spine (see [Bogatyr](../bogatyr/CONSTRUCTION.md#the-electrodes-rules)), the kind made of
two halves that open apart when it is unzipped.

- **A 3D-printed insert** holds everything in its place: the battery at the bottom, above it
  [Mrazík](#mrazík), the closed block round the stack of Baťa with Mamka over him and Terem or a
  plate under him (see [Mamka](../mamka/CONSTRUCTION.md#the-stack)), with a fan blowing over its
  fins. A home printer prints an insert; a whole backpack would take a large one.
- **A connector for each piece of the suit,** eight in the shell, one a line: the arms with
  their shoulders, the legs, the head's module, the chest, the back, and the headband (see
  [Porjadok](../porjadok/HARDWARE.md#links-between-boards)), so a piece comes off by itself; the
  head takes two, line 5's and line 8's, and the turtleneck sewn to the headband (see
  [Rubaška](../rubaska/CONSTRUCTION.md#harness-and-washing)) carries the neck's module on line 7
  with the back, so line 7's cable has a branch connector at the neck's foot, the Weipu SP21 of
  the branches, and the headband with the turtleneck comes off as one piece on three plugs. A
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


## Mrazík

*Mrazík*, Father Frost of the fairy tale, is the inner construction of the cooling (see
[the names](../NAMES.md)): a closed aluminium block, **IP55** (IEC 60529: protected against
dust, and against water jets), round the computer's stack, the ROCK 5T with Mamka over it and
under it either Terem or a plain aluminium plate in its place, so that one block serves every
fitting (see [Mamka](../mamka/CONSTRUCTION.md#the-stack)). Borovičok's is the same block with the
plate, or an SSD's card, and no Mamka: his power and its switching come from Mamka on his DC
cable, and his link to Baťa is Ethernet (see [Baťa](../bata/HARDWARE.md#borovičok)). Its
dimensions are set when it is drawn.

- **The walls** are finned aluminium blocks screwed together over thermal paste, the sides
  between the fins. Bosses reach the chips over pads, the boards sit on standoffs, and the lid
  is pressed by ~8 screws round its edge. The bottom is a plastic part with a soft seal round the
  cables: the block stands on its edge with the ports down.
- **The block is the stack's frame** (the owner, 5 Nov 2026): Mamka screwed into it, the ROCK, its
  own heatsink taken off, pressed onto the SoC's boss over a pad and screwed down hard, Terem
  clicked on and screwed into the block, the Hailos or an SSD in, then the back laid on over
  thermal pads and closed on a soft rubber seal. **Nothing inside cools in still air:** whatever
  warms, the SoC, the Hailos, an SSD, the converters, lies against the aluminium through a soft
  silicone pad of ~1 mm. Mamka either over pillars of the block under her warm parts, through
  insulating pads, the pillars milled, pressed or screwed in, or in channels the fan's air runs
  through, she then lacquered and sealed round her edge; which, when the block is drawn.
- **The SoC** is cooled by a boss through a window in Mamka over it, ~30 × 30 mm (the RK3588 is
  23 × 23 mm). The top wall clears Mamka's tallest parts, 10.2 mm, so the boss is ~36 mm long: at
  25 × 25 mm of aluminium (~200 W/m·K) ~0.3 K/W, ~5 K at 17 W, an estimate before the pads.
- **The antennas outside:** Wi-Fi and Bluetooth do not leave a closed aluminium block, so their
  antennas sit outside it, on SMA bulkheads in its wall.
- **The fans sit outside on the fins,** so they need no sealing. Mamka drives Baťa's as she
  drives the backpack's fan, by processor 2's PWM with the speed read back (see
  [Mamka](../mamka/HARDWARE.md#what-is-on-it)); Borovičok's, a two-wire 5 V fan, runs from his
  ROCK's own fan connector, switched by the ROCK's PWM with no speed read back (see
  [Baťa](../bata/HARDWARE.md#borovičok)).
- **Inside:** conformal coating with the connectors masked, a sachet of silica gel and an ePTFE
  vent for the pressure; no oil, which holds dust and creeps into the ports.
- **Condensation:** the inside is warm while it runs, so above the dew point; condensation
  threatens after switching off and at a cold start.
- **Its heat** is ~8–23 W in the small fitting and up to ~40 W in the brutal one, and Borovičok's
  block takes +4–17 W (see [Heat](#heat)).
- **Drawn at home** from Radxa's 3D model of the ROCK 5T V1.2 and from Mamka's and Terem's boards
  once they are drawn in EasyEDA.


## Heat

Worked out from the parts' own figures; with the ROCK 5T it is still open:

| source | power |
|---|---|
| the ROCK 5T | ~4–17 W |
| Hailo-10H, none, one or two | 0–16.5 W, 8.25 W each at most (Hailo's datasheet) |
| Mamka's own 3.3 V: the two processors and the line drivers, ~0.72–0.77 A | ~2.6–3.0 W from the battery, through her converter |
| the fan, the BMS, the eFuses | under 1 W |
| the converters (Mamka's LMR43610s, Terem's two LMR60440) | ~1–3 W, an estimate from their efficiency, to check in their datasheets |
| **total** | **~8–40 W** |

- **The way out:** every watt inside leaves through [Mrazík](#mrazík)'s walls to their fins, and
  no air of the backpack touches the boards. The SoC gives its heat to the top wall's boss
  through Mamka's window (see [Mamka](../mamka/CONSTRUCTION.md#the-stack)); the Hailos lie on
  pads against the block's wall on Terem's side (see
  [Terem](../terem/CONSTRUCTION.md#the-connectors-and-the-mounting)).
- **What the makers say:** for the AI HAT+ 2, the Hailo-10H on a Raspberry Pi, a heatsink is
  advised for a continuous load, and the suit's load is continuous: both modules get one: Mrazík's
  wall through the pads.
- **The air:** Mrazík stands upright on its edge, parallel to the back, in a channel that the
  insert forms around it. The backpack's fan draws in low at the side, above the wall between the
  battery and the electronics, and blows up the channel; the air leaves at the top under the
  overhang, away from the back and the neck. It passes the fins of both of Mrazík's faces, along
  the flow. Warm air rises the same way, so the battery at the bottom stays cool.
- **A small fan does for the small and the normal fitting:** 2.4 l/s (~5 CFM) is the fan's figure
  in free air, and 15 W in it warm the air by ~5 K. The mesh, the fins and the outlet take part of
  the flow (Noctua gives a static pressure of only ~1.95 mm H₂O, ~19 Pa), so the air warms more, an
  estimate of ~7–10 K. **The brutal fitting is another matter:** its ~40 W warm the same air by
  ~13 K free and ~20–27 K with the losses, Borovičok's block beside it ~57 W by ~19–38 K, before
  the fins' own resistance, which is set when Mrazík is drawn, so on a 35 °C day the fins would
  stand at 55–70 °C and the SoC's boss above them. So the fins and the fan are sized for 40 W
  when the block is drawn, a second fan or a larger one if the channel asks, and until measured
  the brutal fitting runs only under an air temperature the measurement sets. The channel is to
  be drawn for Mrazík's size once the block is drawn. The SoC and the Hailos give their heat
  to Mrazík's walls and the fins to the channel's air, with no fan of the Hailos' own; a
  measurement is to confirm it.
- **Fan control:** a 4-pin PWM fan, the Noctua NF-A4x10 5V PWM: 40 × 40 × 10 mm, 0.07 A, up to
  5,000 rpm and ~5 CFM in free air. It has its own driver, so Mamka needs no MOSFET or diode:
  Mamka's own 5 V converter feeds the fan (see [Mamka](../mamka/HARDWARE.md#mamkas-own-supply)), a
  timer gives PWM at 25 kHz and another reads the speed, two pulses a turn, so a stopped fan is
  noticed (see [Mamka](../mamka/HARDWARE.md#what-is-on-it)). At 0 %
  the fan stops, at 20 % it turns ~1,050 rpm. The computer sets the curve from the SoC's
  temperature, the Hailo's and the BMS's. If the fan stops, the computer lowers the Hailos'
  load.
- **Both sides:** the board takes ~4–17 W and its two Hailos up to 16.5 W (see
  [the battery](HARDWARE.md#the-battery)). The SoC lies on top and the two modules under the
  board, so the channel has to reach both of Mrazík's faces.
- **Sun:** a light-coloured shell. In the sun a dark one could come near the 40 °C and 50 °C the
  BMS allows for charging and discharging, our margins under the 55 °C and 60 °C of EVE's sheet
  (RD-C40-S01-LF rev. A, see [software](SOFTWARE.md#the-bmss-settings)).
- **Dust and rain:** the intake behind fine mesh, the outlet under an overhang; Mrazík itself is
  IP55.


## Open questions

- the backpack: which shell, the insert with its channel, the vents and the fan's real flow
  through them; the converters' losses from their datasheets,
- the backpack's heat with the ROCK 5T: the channel around both of Mrazík's faces,
- Mrazík: its dimensions, its walls and fins, the bosses and their pads, the lid's seal and the
  plastic bottom's round the cables, drawn from Radxa's 3D model V1.2 and Mamka's and Terem's
  boards; the SoC's temperature through its boss at full load, measured; the Hailos' temperature
  on their pads against the wall; whether the
  backpack's fan does for Baťa's block or the block takes a fan of its own on a second PWM of
  processor 2; condensation after switching off and at a cold start, tried,
- the pieces' connectors, the Weipu SP21: their contacts against our 28 AWG wire, which contact
  carries what, and where the eight sit on the shell.
