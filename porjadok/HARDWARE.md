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
| 6 V | ~7 mA, the head's ~15, the neck's ~8 | the same | ~0.12 A, ~0.73 W |

- **Two ADS1298 draw what one ADS1299 did:** 2 × 3.1 mA against 7.14 on the analog rail and 2 ×
  0.5 against 1 on the digital (SBAS459K and SBAS499C, Electrical Characteristics), so a module's
  budget stands with its second chip (see [Rubaška](../rubaska/HARDWARE.md#power)).
- **The processor is counted as at 200 MHz in VOS0,** for margin (see
  [Rubaška](../rubaska/HARDWARE.md#power)); its core at 49.152 MHz saves an estimated ~14 mA
  more (see [software](SOFTWARE.md#the-clock-tree)), not taken off here.
- **On a line only one driver sends at a time,** so an arm's line, three modules and the glove at
  ~0.11 A on average and ~0.21 A at worst (see [Rubaška](../rubaska/HARDWARE.md#the-glove)), takes
  ~0.31 A on the 4 V rail on average and ~0.50 A at worst, the most any line of the body draws; a
  leg's, three modules and the sock at ~0.09 A and ~0.17 A, ~0.29 A and ~0.47 A.
- The digital rail at 4 V costs ~0.3 W across the suit against 3.7 V and buys the margin the
  LDOs and the head's motors need (see [WHY](WHY.md)). The analog rail stays at 6 V: 5.5 V would
  save only ~0.06 W, and the headroom helps the TPS7A47 reject ripple from Mamka's converters.

## Links between boards

The eight lines are the *Pupovina*, Russian for the umbilical cord: they bring power, the clock
and data to Mamka's children, the [Rebjata](../rubaska/HARDWARE.md#sensing-module), the gloves,
Nataša and Míša.

Eight lines leave Mamka, **a line a piece of the suit,** at most four units a line, so that the suit
comes apart in its pieces with no connector along it: each piece's cable goes straight to the
backpack, an arm's over its shoulder and down the arm, the units chained along it. Fully populated,
that is 35 ADS129x, two ADS1298 on a module of the body, two ADS1299 on the head's, one on the
neck's and one ADS1298 on each glove and sock, 280 channels; 64 IMU places in the modules, two
gloves of 20 IMUs and two socks of 8.

| line | processor | the piece | slots 1–4 |
|---|---|---|---|
| 1, 2 | 1 | the left arm, the right: the sleeve with its shoulder, and the glove | the shoulder, the upper arm, the forearm, the glove |
| 3, 4 | 1 | the left leg, the right: the trouser leg, and the sock | the hip, the thigh, the calf, the sock |
| 5 | 2 | the headband: the head's EMG | the head's module |
| 6 | 2 | the trunk in front | the chest and abdomen |
| 7 | 2 | the trunk behind | the neck and upper back, the lower back |
| 8 | 2 | the headband: [Nataša](../natasa/README.md) and [Míša](../misa/README.md), with the sound | Nataša, Míša, in two slots of their own |

Which unit is on which line and in which slot the map says, not the wiring. Lines 1–4 end at
processor 1 on [Mamka](../mamka/README.md), the limbs, which hands their frames to Baťa over one
fast SPI; lines 5–8 at her processor 2, the head and the trunk, over two slower ones. A suit for
the head and the trunk alone needs only processor 2's half of Mamka; the shoulders ride with the
arms.

A line has three pairs: two for data and one for the clock. The cable has 16 wires (see
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

- **every line:** 196,608,000 / 10 = **19,660,800 Bd,** 1.7% under the stated 20 Mbaud: 1,024 B
  a cycle at 1,920 SPS, four slots of 128 B in its first half (see
  [software](SOFTWARE.md#timing-of-one-cycle)). A unit's driver
  draws ~37 mA into the terminations only while it sends, and the cable's own charge is a few mA
  (an estimate), so a frame sent in half the time costs half.
- **24,576,000 Bd,** 196.608 MHz with USARTDIV 16 (RM0481 56.5.8), is above the datasheets' 20
  Mbaud: a trial on the first board, where only BRR differs.

Every line runs at the one rate, set in every firmware; nothing on a line switches it.

What travels on the lines, the frames, the slots, the commands and the way into Baťa, is under
[software](SOFTWARE.md#the-frames).

## Cable and connectors in the suit

Inside the suit a line runs as one flat cable of **16 wires,** the **3M 3811/16** (3M TS-0122),
with IDC sockets of 2 × 8 pressed onto it along the way, one where each unit taps in.

- **The wires,** a ground between the pairs so that the 9.8 MHz clock does not talk into the
  data: ground, data down, ground, data up, ground, clock, ground, ten for the signals; then
  2 × +4 V, 2 × ground and 2 × +6 V. At the backpack's connector the doubled wires share a
  contact, so a branch takes **10 pins:** six for the pairs and four for the supply, 4 V, 6 V and
  two grounds, three ground wires to each.
- **26 AWG of 7 × 0.160 mm tinned stranded copper** on 1.27 mm centres, PVC, unshielded and
  untwisted; 95 Ω between ground, signal and ground, 48.6 pF/m and 4.63 ns/m (TS-0122). The
  pairs' own impedance the sheet does not give: the lines are terminated with 120 Ω, checked on
  the cable. PVC does here: the lines carry low-impedance digital signals, on which charge from
  friction does not show.
- A 1.27 mm flat cable fits an ordinary IDC socket with two rows at 2.54 mm, one that takes
  26 AWG stranded wire. A socket can be pressed on anywhere, so the taps sit along one cable
  wherever a unit is.
- **The six grounds** hold the modules' grounds close together.
- A broken cable is repaired with a new socket past the damage, or a piece of new cable between
  two sockets.
- **Sewn in, in meanders:** the cables are sewn into the suit along wavy paths, which take the
  stretch, and a pull has to tear the seams before it reaches the wires.
- **Where the suit parts:** at the backpack, each piece's line through a connector of its own
  (see [Babuška](../babuska/CONSTRUCTION.md#the-backpack)); and at each unit, which unplugs for
  washing, the glove's board on the back of the hand as a module does, the line's cable sewn on
  over the wrist to it. Nowhere else.
- At these rates the stub from a tap to the unit's driver stays a few centimetres long, so each
  unit sits right at its tap.

**The backpack's connectors,** one a branch, eight in the backpack's shell: the **Weipu SP21 of
12 pins** (IP68, 5 A, a screwed coupling; two pins spare), the plug SP2110/P12II-1N $7.83 at TME
($5.22 by 20) and the socket 24.45 PLN at Piekarz, ~2,500 CZK for eight pairs, an estimate. For
the first trials the **GX16 of 10 pins** (29 CZK a half at dratek.cz; no sealing given, the shop's
figures unreliable), with the same pinout. Amphenol's PT 12-10 was weighed, a bayonet and IP67,
over 10,000 CZK for eight pairs ($33.64 the plug at PEI-Genesis, 2024); see [WHY](WHY.md).

**Untwisted and unshielded,** over 1–2 m: the twist matters less for the data than for what the
line sends out towards the bands' strips and picks up, and in a flat cable the two wires of a
pair lie 1.27 mm apart, so their loop is small. **It holds if two tests pass:** 2 m of the cable
carries the line at 20 Mbaud with an open eye, and a band's strip laid alongside it, read by a
module, shows nothing of it in the data. Should the second fail, a braided sleeve over the
cable, grounded at Mamka, is its shield.

**The drop** on a metre at ~0.38 A on the 4 V rail, a line's current as first counted, is ~25 mV
on the two +4 V wires and ~8 mV on the six grounds, ~33 mV, at ~0.13 Ω/m: 26 AWG's 0.141 mm² of
copper with a little for the tin and the lay, an estimate, 3M's sheet giving no resistance. At
most it is taken as ~151 Ω/km, UL 1571's 239 Ω/km for 28 AWG of 7 × 0.127 mm (LTK's sheet)
scaled by the cross-section, so the six grounds come to ~0.025 Ω/m: a unit a metre out sits
≤ ~13 mV off Mamka's ground at an arm's worst 0.50 A, two units on different lines twice that at
most. Against the volts of the ADS129x's common-mode range it is nothing.

The 6 V rail carries little, ~8 mA per module, so one wire would be plenty; the cable gives it
two.

### End to end

The TPS7A2033 holds its ±1.5% from an input of 3.6 V up and falls out of regulation below
~3.44 V: its dropout is at most 140 mV at 300 mA, over −40 to 125 °C (SBVS338H, 5.5). From
Mamka's converter to a module's LDO, at ~0.54 A, all of it at the end of a metre, every part at
its worst; the table keeps the 0.54 A first counted, more than any line now draws (~0.50 A, an
arm's three modules and the glove), so the margin is a little larger than it shows:

| from Mamka to the LDO | resistance | drop |
|---|---|---|
| the converter: 1.00 V ± 1% at FB (SNVSBY5B, 7.5) and 1% resistors | | 3.92 V instead of 4.02 V |
| Mamka's π filter, two chokes and two beads side by side | ≤ 0.185 Ω | 100 mV |
| Mamka's IDC, +4 V and ground on one contact each | ~2 × 20 mΩ, an estimate (3M's sheet not read) | 22 mV |
| the harness in the backpack, 20 cm of 28 AWG, one wire each way | 2 × 48 mΩ | 52 mV |
| the backpack's Weipu SP21, +4 V on one contact, ground on two | ~10 mΩ, taken as 7 mΩ a contact, Weipu's figure not read | 6 mV |
| a metre of the cable at ~151 Ω/km (above), +4 V on two wires, ground on six | 0.10 Ω | 54 mV |
| the module's IDC, two contacts for +4 V, six for ground | ~13 mΩ | 7 mV |
| **at the LDO** | | **≥ 3.67 V**, ~3.83 V from typical figures |

- **The suit's lines hold** the 3.6 V at the worst corner. The glove's LDOs sit at the end of its
  arm's line, on the hand, as a unit's do.
- **Line 8, Nataša's and Míša's,** at its worst millisecond, ~1.0 A while the radar chirps with
  two motors running, falls to ~3.48 V at the worst corner, ~3.67 V from typical figures.
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

Every pair is terminated at both ends with 120 Ω, checked on the cable: at Mamka, and at
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
| the sensing module | [Rubaška](../rubaska/HARDWARE.md#sensing-module) | two ADS129x, one on each side, or the neck's one ADS1299, beside a processor and line drivers on one narrow board: analog and digital returns apart on a plane |
| the IMU board | [Rubaška](../rubaska/HARDWARE.md#the-imu) | small; the same stack for the same order, I3C over a plane |
| the glove's, Vešč, and the sock's, Nosok | [Rubaška](../rubaska/HARDWARE.md#the-glove) | one board on the back of the hand, or on the calf above the ankle for the foot: an ADS1298 with its inputs on one side, Staršaja, the line's drivers and four Bratiški on the other; the same stack as a module's |
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
thinner for the IMU board and the glove's board if the suit asks, decided at construction. The
rest of the family is software or bought: Baťa and Borovičok, the BMS, the cables and connectors.

## Open questions

- cable length: confirm by measurement that a metre of the cable carries ~20 Mbit/s on every
  line, and whether 24.576 Mbaud holds,
- the 3M 3811/16 on a sample: its pairs' impedance against the 120 Ω terminations, the IDC
  sockets that take its 26 AWG, and its resistance against the ~151 Ω/km taken,
- the Weipu SP21's contact resistance, from its sheet or measured,
- the cable's two tests: the eye at 20 Mbaud over 2 m, and a band's strip alongside, read by a
  module; first on an old 40-wire IDE cable (1.27 mm, 28 AWG), the sleeve only if the strip
  asks for it.
