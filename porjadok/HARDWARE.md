<div align="center">

# Porjadok: hardware

**What every module shares in copper:** the power rails and their budget, the lines, the cable and
its connectors, the drivers on a unit, and the boards.

↑ [Porjadok](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## Power

The suit's power is *Pitanije*, a Russian word that means both food and a power supply: from
[Babuška](../babuska/README.md) through [Ključnica](../babuska/HARDWARE.md#the-bms) and Mamka's
converters down to the LDOs on every module.

The suit runs from a LiFePO4 battery of 12.8 V nominal, charged between 20 and 80%.
[Mamka](../mamka/HARDWARE.md#converters) makes two supply rails from it with LMR43610 buck
converters at 2.2 MHz: **4 V** for the digital parts, a converter for each line, and **6 V** for
the analog parts, one converter for the whole suit. Each module brings them down with its own
LDOs: 3.3 V for everything digital, 5 V for the analog side. The RS-485 drivers run from 3.3 V as
well, which lowers the current on the lines. How a sensing
module does it is described under [Rubaška](../rubaska/HARDWARE.md#power).

**Budget** of the sensing modules: the average from typical datasheet figures, the peak with the
processor at its datasheet maximum and the line driver sending:

| rail | one module, average | one module, peak | 16 modules |
|---|---|---|---|
| 4 V | ~69 mA | ~135 mA | ~1.10 A, ~4.4 W |
| 6 V | ~8 mA | ~8 mA | ~0.13 A, ~0.77 W |

- **The processor is counted as at 200 MHz in VOS0,** for margin (see
  [Rubaška](../rubaska/HARDWARE.md#power)); its core at 49.152 MHz saves an estimated ~14 mA
  more (see [software](SOFTWARE.md#the-clock-tree)), not taken off here.
- **On a line only one driver sends at a time,** so a leg's line of three modules takes ~0.21 A
  on the 4 V rail, ~0.33 A at worst; an arm's line, three modules and the glove at ~0.11 A on
  average and ~0.22 A at worst (see [Rubaška](../rubaska/HARDWARE.md#the-glove)), ~0.31 A on
  average and ~0.51 A at worst, the most any line of the body draws.
- The digital rail at 4 V costs ~0.3 W across the suit against 3.7 V and buys the margin the
  LDOs and the head's motors need (see [WHY](WHY.md)). The analog rail stays at 6 V: 5.5 V would
  save only ~0.06 W, and the headroom helps the TPS7A47 reject ripple from Mamka's converters.

## Links between boards

The eight lines are the *Pupovina*, Russian for the umbilical cord: they bring power, the clock
and data to Mamka's children, the [Rebjata](../rubaska/HARDWARE.md#sensing-module), the gloves,
Nataša and Míša.

Eight lines leave Mamka, **a line a piece of the suit,** at most four units a line, so that the
suit comes apart in its pieces with no connector along it: each piece's cable goes straight to
the backpack, an arm's over its shoulder and down the arm, the units chained along it. Fully
populated, that is 16 ADS1299 and 64 IMU places in the modules and two gloves of 20 IMUs.

| line | processor | the piece | slots 1–4 |
|---|---|---|---|
| 1, 2 | 1 | the left arm, the right: the sleeve with its shoulder, and the glove | the shoulder, the upper arm, the forearm, the glove |
| 3, 4 | 1 | the left leg, the right | the hip, the thigh, the calf; one free |
| 5 | 2 | the headband: the head's EMG | the head's module |
| 6 | 2 | the trunk in front | the chest and abdomen |
| 7 | 2 | the trunk behind | the neck and upper back, the lower back |
| 8 | 2 | the headband: [Nataša](../natasa/README.md) and [Míša](../misa/README.md), with the sound | Nataša, Míša, in two slots of their own |

Which unit is on which line and in which slot the map says, not the wiring. Lines 1–4 end at
processor 1 on [Mamka](../mamka/README.md), the limbs, which hands their frames to Baťa over one
fast SPI; lines 5–8 at her processor 2, the head and the trunk, over two slower ones. A suit for
the head and the trunk alone needs only processor 2's half of Mamka; the shoulders ride with the
arms.

A line has three pairs: two for data and one for the clock. The cable has 14 wires (see
[the cable](#cable-and-connectors-in-the-suit)).

**Data: full-duplex (four-wire) RS-485 with time-division multiple access (TDMA)**

- The master's TX (the STM32H562 on Mamka) is wired to the RX of every unit on the
  line. The master talks to all of them at once.
- The TX of every unit on the line is wired to the master's RX. The units take turns on this
  pair, each in its own time slot.
- A unit transmits on its second UART and reads its own transmission back through that UART's
  RX (echo).

**Line speed**

The units have STM32H523s, Mamka two STM32H562s. Per their datasheets (DS14540, DS14258) the
USART of both reaches 20 Mbaud with DMA. Both ends take their clock from the suit, 20 × 9.8304
MHz = 196,608,000 Hz, Mamka's as her bus clock and a unit's on a PLL of its own for the USART
alone (see [software](SOFTWARE.md#the-clock-tree)), which VOS1 allows (200 MHz, tables 20 and 21),
so the rates match exactly, with 8× oversampling:

- **every line:** 196,608,000 / 10 = **19,660,800 Bd,** 1.7% under the stated 20 Mbaud: 512 B
  a cycle, four slots of 128 B (see [software](SOFTWARE.md#timing-of-one-cycle)). A unit's driver
  draws ~37 mA into the terminations only while it sends, and the cable's own charge is a few mA
  (an estimate), so a frame sent in half the time costs half.
- **24,576,000 Bd,** 196.608 MHz with USARTDIV 16 (RM0481 56.5.8), is above the datasheets' 20
  Mbaud: a trial on the first board, where only BRR differs.

Every line runs at the one rate, set in every firmware; nothing on a line switches it.

What travels on the lines, the frames, the slots, the commands and the way into Baťa, is under
[software](SOFTWARE.md#the-frames).

## Cable and connectors in the suit

Inside the suit a line runs as one cable of **14 wires,** its part chosen later. The first
candidate is the **3M 1785**, a shielded and jacketed twisted-pair flat cable (3M TS-0308), with
IDC sockets pressed onto it along the way, one where each unit taps in.

- **The wires:** 6 for the three pairs (from the master, to the master, the clock); 2 × +4 V and
  2 × +6 V, each twisted with one of **four grounds**. At each end the doubled wires go two into
  one contact, so a branch takes **10 pins:** six for the pairs and four for the supply, 4 V,
  6 V and two grounds.
- The 1785 is 28 AWG of 7 × 0.127 mm tinned stranded copper, which takes repeated bending; PVC
  insulation and jacket; a shield of expanded copper all round, 20 dB on average. PVC does here:
  the lines carry low-impedance digital signals, on which charge from friction does not show.
- A pair has 118 Ω and 45.3 pF/m, so the lines are terminated with 120 Ω.
- The pairs are twisted in stretches with short flat stretches between them: by default 508 mm
  in all with 51 mm flat, as option TB 190 mm with 25 mm flat, to order from 165 mm to 1.22 m.
  IDC sockets go only onto a flat stretch, so with TB a unit can tap in every 19 cm.
- A 1.27 mm flat cable fits an ordinary IDC socket with two rows at 2.54 mm. A socket can be
  pressed anywhere on a flat stretch, so the taps sit along one cable.
- **The four grounds** hold the modules' grounds close together, which the bias drive wants when
  more than one module drives (see [Rubaška](../rubaska/HARDWARE.md#right-leg-drive)).
- A broken cable is repaired with a new socket on the next flat stretch past the damage, or a
  piece of new cable between two sockets.
- **Sewn in, in meanders:** the cables are sewn into the suit along wavy paths, which take the
  stretch, and a pull has to tear the seams before it reaches the wires.
- **Where the suit parts:** at the backpack, each piece's line through a connector of its own
  (see [Babuška](../babuska/CONSTRUCTION.md#the-backpack)); at the wrist, where the hand's eight
  wires plug into the glove's Staršaja on the sleeve; and at each module, which unplugs for
  washing. Nowhere else.
- At these rates the stub from a tap to the unit's driver stays a few centimetres long, so each
  unit sits right at its tap.

**The backpack's connectors,** one a branch, eight in the backpack's shell: the **Weipu SP21 of
12 pins** (IP68, 5 A, a screwed coupling; two pins spare), the plug SP2110/P12II-1N $7.83 at TME
($5.22 by 20) and the socket 24.45 PLN at Piekarz, ~2,500 CZK for eight pairs, an estimate. For
the first trials the **GX16 of 10 pins** (29 CZK a half at dratek.cz; no sealing given, the shop's
figures unreliable), with the same pinout. Amphenol's PT 12-10 was weighed, a bayonet and IP67,
over 10,000 CZK for eight pairs ($33.64 the plug at PEI-Genesis, 2024); see [WHY](WHY.md).

**A variant to try: the lines untwisted, on the 3M 3517.** Over 1–2 m the twist matters less
for the data than for what the line sends out towards the bands' strips and picks up. In a
flat cable the two wires of a pair lie 1.27 mm apart, so their loop is small even untwisted,
and the 3517's shield all round holds the rest (20 dB on average).

- **Taps anywhere:** an untwisted flat cable has no flat stretches to wait for, so a socket can
  be pressed on at any point.
- **Ground wires between the pairs,** so that the 9.8 MHz clock does not talk into the data: ground,
  data down, ground, data up, ground, clock, ground, then the supply. That takes the 3517/14 or /16:
  ten wires for the signals, the rest for the supply. Adjacent wires have 119 Ω, so the termination
  stays 120 Ω.
- **It holds if two tests pass:** 2 m of 3517 carries the line at 20 Mbaud with an open eye, and
  a band's strip laid alongside it, read by an ADS1299, shows nothing of it in the data.
  Then the twist goes.

Drop on 1 m of cable at ~0.38 A on the 4 V rail, a line's current as first counted:

| wire | +4 V | ground | total |
|---|---|---|---|
| as first drawn, 28 AWG, 7 × 0.127 mm, ~0.2 Ω/m, one wire each | 76 mV | 38 mV, two wires | 114 mV |
| the 1785/16: +4 V on two wires, ground on six | 38 mV | 13 mV | 51 mV |
| the cable of 14 wires: +4 V on two wires, ground on four | 38 mV | 19 mV | 57 mV |

UL 1571's 28 AWG of 7 × 0.127 mm has at most 239 Ω/km (LTK's sheet), so the four grounds come to
~0.06 Ω/m: a unit a metre out sits ≤ ~30 mV off Mamka's ground at an arm's worst 0.51 A, two units
on different lines twice that at most. Against the volts of the ADS1299's common-mode range it is
nothing; for drives on several modules it means currents of tenths of a microamp between them
(see [Rubaška](../rubaska/HARDWARE.md#right-leg-drive)).

The 6 V rail carries little, ~8 mA per module, so one wire would be plenty; the cable gives it
two.

### End to end

The TPS7A2033 holds its ±1.5% from an input of 3.6 V up and falls out of regulation below
~3.44 V: its dropout is at most 140 mV at 300 mA, over −40 to 125 °C (SBVS338H, 5.5). From
Mamka's converter to a module's LDO, at ~0.54 A, all of it at the end of a metre, every part at
its worst; the table keeps the 0.54 A first counted, more than any line now draws (~0.51 A, an
arm's three modules and the glove), so the margin is a little larger than it shows:

| from Mamka to the LDO | resistance | drop |
|---|---|---|
| the converter: 1.00 V ± 1% at FB (SNVSBY5B, 7.5) and 1% resistors | | 3.92 V instead of 4.02 V |
| Mamka's π filter, two chokes and two beads side by side | ≤ 0.185 Ω | 100 mV |
| Mamka's IDC, +4 V and ground on one contact each | ~2 × 20 mΩ, an estimate (3M's sheet not read) | 22 mV |
| the harness in the backpack, 20 cm of 28 AWG, one wire each way | 2 × 48 mΩ | 52 mV |
| the backpack's Weipu SP21, +4 V on one contact, ground on two | ~10 mΩ, taken as 7 mΩ a contact, Weipu's figure not read | 6 mV |
| a metre of the cable at UL 1571's 239 Ω/km, +4 V on two wires, ground on four | 0.18 Ω | 97 mV |
| the module's IDC, two contacts for +4 V, four for ground | ~15 mΩ | 8 mV |
| **at the LDO** | | **≥ 3.63 V**, ~3.80 V from typical figures |

- **The suit's lines hold** the 3.6 V at the worst corner. The glove's LDO sits at the end of
  its arm's line, as a unit does.
- **Line 8, Nataša's and Míša's,** at its worst millisecond, ~1.0 A while the radar chirps with
  two motors running, falls to ~3.39 V at the worst corner, ~3.61 V from typical figures.
  Nataša's LDO still holds 3.3 V: at her ~160 mA its dropout is about half the 140 mV, inferred
  from the sheet's figure at 300 mA. A motor's overdrive is weaker for that millisecond only.
  Míša's supply is under [Míša](../misa/HARDWARE.md).
- **The harness is the weak link:** a single 28 AWG wire each way. It stays short, ~10–20 cm,
  from Mamka's headers to the connectors in the shell; 10 cm gives back ~26 mV.

## Cable length

The cable runs at most about a metre each way from Mamka. TI's cautious RS-485 rule
(length in metres × rate in bit/s below 10⁷) gives only 0.5 m at the lines' 19.66 Mbaud; TI
itself says today's cables do better. A metre at 20 Mbit/s therefore needs to be confirmed by
measurement.

## Clock: a one-way RS-485 channel

[Mamka](../mamka/README.md) sends the clock straight from her oscillator through three buffers
and eight drivers, one per line. **Each processor switches the clock drivers of her own lines on
one pin:** their DE up from her start, so the clock runs on her lines from then on (see
[Bring-up](SOFTWARE.md#bring-up)), and down only while her lines are off or asleep. The
eight drivers draw ~37 mA each into their terminations, ~0.3 A, which the two pins take off then.
The units on a line receive the clock from one pair.

## Drivers on a unit

| driver | count | pair |
|---|---|---|
| TI THVD1452 (full duplex, DE/RE) | 2 | data: the pair from the master and the return pair |
| TI THVD1450 (half duplex) | 1 | clock, receive only |

Expected wiring: the first THVD1452 receives from the master on A/B and drives the return pair
on Y/Z, its driver switched by DE from the UART. The second THVD1452 receives the return pair on
A/B and so gives the echo. The THVD1450 receives the clock. **The glove's Staršaja and Míša** take
two packages instead: one THVD1452 for the return pair and a quad receiver, the AM26LV32E, for
the pair from the master, the echo and the clock (3.3 V, 32 Mbps, VQFN-16 3.5 × 4 mm; 8 mA
typical, 17 mA at most, SLLS849E).

Every pair is terminated at both ends with 120 Ω, for the cable's 118 Ω: at Mamka, and at
the last unit by a solder jumper that every unit has, closed on the last one. A driver then
sees the two in parallel, ~60 Ω, close to the 54 Ω the datasheets test with (see
[Mamka](../mamka/HARDWARE.md#lines)).

All the drivers run from 3 to 5.5 V at up to 50 Mbit/s, the AM26LV32E at 3.3 V; on a unit they
run from 3.3 V (see [power](#power)). We considered M-LVDS too, but stayed with classic
RS-422/485 because of what the drivers and the parts around them consume.

RS-485 also carries the sound from Baťa across the suit to
[Nataša](../natasa/README.md).

## Boards

Seven boards are drawn, every one of them with the same four layers: signal, ground, power with
ground, signal, so that every trace has a plane under it and the ground is never cut by a trace.
Even the small ones take it: a four-layer board costs little more than a two-layer one at the
sizes here (an estimate; the house's price list decides), and one stack means one set of rules,
one impedance table and one order.

| board | where | what asks for the planes |
|---|---|---|
| [Mamka](../mamka/README.md) | the backpack | two processors, eight line drivers at 19.66 Mbaud and eight clock drivers at 9.83 MHz, the converters, the clock |
| [Terem](../terem/README.md) | under the ROCK 5T | ten PCIe Gen 3 pairs at 85 Ω in 0.5 mm pitch; 0.8 mm thick for the M.2 sockets |
| the sensing module | [Rubaška](../rubaska/HARDWARE.md#sensing-module) | the ADS1299 beside a processor and line drivers on one narrow board: analog and digital returns apart on a plane |
| the IMU board | [Rubaška](../rubaska/HARDWARE.md#the-imu) | small; the same stack for the same order, I3C over a plane |
| the glove's, Vešč | [Rubaška](../rubaska/HARDWARE.md#the-glove) | Staršaja on the sleeve with the line's drivers and five wires to the hand; the Bratiški on the hand, where they sit seen when it is drawn; the same stack |
| [Míša](../misa/README.md) | the headband | the radar module, the ultrasound, a processor, the line's drivers |
| [Nataša](../natasa/README.md) | the headband | I2S, the DAC and the amplifier beside the processor |

Beside them two kinds of flexible circuit, no boards but drawn the same way: the torso's strips,
polyimide of two layers, signals and a ground, from JLCPCB, and the stretchable circuits of the
limbs' bands and the glove, copper on TPU, from a maker of such (see
[Rubaška](../rubaska/CONSTRUCTION.md#electrodes)).

The ADS1299's own example layout is drawn for a minimum of two layers, with inner layers for
power where there are more (its datasheet, 12.2); it is the processor and the drivers on the same
board, and the module's narrow shape, that make the plane worth having there. Thickness follows
the board: 0.8 mm where an M.2 socket demands it, otherwise the house's standard 1.6 mm, and
thinner for the IMU board and the glove's boards if the suit asks, decided at construction. The
rest of the family is software or bought: Baťa and Borovičok, the BMS, the cables and connectors.

## Open questions

- cable length: confirm by measurement that a metre of the cable carries ~20 Mbit/s on every
  line, and whether 24.576 Mbaud holds,
- the cable's part: 14 wires, the 3M 1785 or another; its IDC sockets on the flat stretches,
  tried on a sample, and where its shield connects: at Mamka only, or at both ends,
- the Weipu SP21's contact resistance, from its sheet or measured,
- the lines untwisted on the 3M 3517: the eye at 20 Mbaud over 2 m, and a band's strip
  alongside, read by an ADS1299.
