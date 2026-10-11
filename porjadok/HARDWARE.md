<div align="center">

# Porjadok: hardware

**What every module shares in copper:** the power rails and their budget, the lines, the cable and
its connectors, the drivers on a block, and the boards.

↑ [Porjadok](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## Power

The suit's power is *Pitanije*, a Russian word that means both food and a power supply: from
[Babuška](../babuska/README.md) through [Ključnica](../babuska/HARDWARE.md#the-bms) and Mamka's
converters down to the LDOs on every module.

The suit runs from a sodium-ion battery of 12 V nominal, charged between 20 and 80%.
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

- On a line only one driver sends at a time, so a line of four modules takes ~0.27 A on the
  4 V rail, ~0.42 A at worst. A glove on the forearm's module adds ~0.06–0.12 A to its line
  (see [Rubaška](../rubaska/HARDWARE.md#the-glove-and-the-foot)), ~0.54 A at worst; the drop
  below grows with it, ~72 mV on the 1785/16, which the TPS7A2033 still bears.
- The digital rail at 4 V costs ~0.3 W across the suit against 3.7 V and buys the margin the
  LDOs and the head's motors need (see [WHY](WHY.md)). The analog rail stays at 6 V: 5.5 V would
  save only ~0.06 W, and the headroom helps the TPS7A47 reject ripple from Mamka's converters.

## Links between boards

The lines are the *Pupovina*, Russian for the umbilical cord: they bring Mamka's children, the
[Rebjata](../rubaska/HARDWARE.md#sensing-module), power, the clock and data.

There are four lines, each carrying two to four basic blocks, 8 to 16 in all. Fully populated, that
is 16 ADS1299 and 64 ICM-42688-P. A fifth line, the same, goes to the head, for
[Nataša](../natasa/README.md) and Míša behind her, with no sensing module on it. The four body lines
end at the body's STM32H562 on [Mamka](../mamka/README.md), which acts as a bridge: it puts the data
together and hands it to Baťa over SPI. The head line ends at her second STM32H562.

A line has three pairs: two for data and one for the clock. The cable is the 3M 1785 shielded
twisted-pair flat cable (see [the cable](#cable-and-connectors-in-the-suit); category 5e or 6
Ethernet cable would do as well, with 100 Ω terminations instead of 120 Ω).

**Data: full-duplex (four-wire) RS-485 with time-division multiple access (TDMA)**

- The master's TX (the STM32H562 on Mamka) is wired to the RX of every block on the
  line. The master talks to all of them at once.
- The TX of every block on the line is wired to the master's RX. The blocks take turns on this
  pair, each in its own time slot.
- A block transmits on its second UART and reads its own transmission back through that UART's
  RX (echo).

**Line speed**

The lines should be as fast as possible: latency at the input should be as small as possible.
The blocks have STM32H523s, Mamka two STM32H562s. Per their datasheets (DS14540,
DS14258) the USART of both reaches 20 Mbaud with DMA. Both ends take their clock from the suit,
20 × 9.8304 MHz = 196,608,000 Hz, which VOS1 allows (200 MHz, tables 20 and 21), so the rates
match exactly: 196,608,000 / 10 = **19,660,800 Bd** with 8× oversampling, twice the suit clock
and 1.7% under the stated 20 Mbaud.

What travels on the lines, the frame, the slots, the channel from the master and the way into
Baťa, is under [software](SOFTWARE.md#the-frame).

## Cable and connectors in the suit

Inside the suit a line runs as one **3M 1785**, a shielded and jacketed twisted-pair flat
cable (3M TS-0308), with IDC sockets pressed onto it along the way, one where each block taps
in.

- 28 AWG of 7 × 0.127 mm tinned stranded copper, which takes repeated bending; PVC insulation
  and jacket; a shield of expanded copper all round, 20 dB on average. PVC does here: the lines
  carry low-impedance digital signals, on which charge from friction does not show.
- A pair has 118 Ω and 45.3 pF/m, so the lines are terminated with 120 Ω.
- The pairs are twisted in stretches with short flat stretches between them: by default 508 mm
  in all with 51 mm flat, as option TB 190 mm with 25 mm flat, to order from 165 mm to 1.22 m.
  IDC sockets go only onto a flat stretch, so with TB a block can tap in every 19 cm.
- A 1.27 mm flat cable fits an ordinary IDC socket with two rows at 2.54 mm, 2 × 8 for sixteen
  wires. The 1785/10 is 16.0 mm wide and 3.0–3.8 mm thick; the 1785/16 is six wires, ~7.6 mm,
  wider. A socket can be pressed anywhere on a flat stretch, so the taps sit along one cable.
- **The wires, the 1785/16:** 6 for the three pairs (from the master, to the master, the
  clock); 2 × +4 V and 2 × +6 V, each twisted with a ground wire as a pair of the cable; and
  one pair of two more grounds: **six grounds** in all, 16 positions, none spare. The six
  grounds hold the modules' grounds close together, which the bias drive wants when more than
  one module drives (see [Rubaška](../rubaska/HARDWARE.md#right-leg-drive)). At the backpack's
  connector the doubled wires go two into one contact.
- A broken cable is repaired with a new socket on the next flat stretch past the damage, or a
  piece of new cable between two sockets.
- **Sewn in, in meanders:** the cables are sewn into the suit along wavy paths, which take the
  stretch, and a pull has to tear the seams before it reaches the wires.
- **Where the suit parts:** at the backpack, through one bayonet connector for all five lines
  (see [Babuška](../babuska/CONSTRUCTION.md#the-backpack)), and at each module, which unplugs for
  washing. Nowhere else.
- At 20 Mbaud the stub from a tap to the block's driver stays a few centimetres long, so each
  block sits right at its tap.

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

Drop on 1 m of cable at the worst current of a line, ~0.42 A on the 4 V rail (see
[power](#power)):

| wire | +4 V on one wire | ground on two wires | total |
|---|---|---|---|
| as first drawn, 28 AWG, 7 × 0.127 mm, ~0.2 Ω/m | 84 mV | 42 mV | 126 mV |
| the 1785/16: +4 V on two wires, ground on six | 42 mV | 14 mV | 56 mV |

UL 1571's 28 AWG of 7 × 0.127 mm has at most 239 Ω/km (LTK's sheet), so the six grounds come to
~0.04 Ω/m: a block a metre out sits ≤ ~17 mV off Mamka's ground at 0.42 A, two blocks on
different lines twice that at most. Against the volts of the ADS1299's common-mode range it is
nothing; for drives on several modules it means currents of tenths of a microamp between them
(see [Rubaška](../rubaska/HARDWARE.md#right-leg-drive)).

The 6 V rail carries little, ~8 mA per module, so one wire would be plenty; the cable gives it
two.

### End to end

The TPS7A2033 holds its ±1.5% from an input of 3.6 V up and falls out of regulation below
~3.44 V: its dropout is at most 140 mV at 300 mA, over −40 to 125 °C (SBVS338H, 5.5). From
Mamka's converter to a module's LDO, at a line's worst ~0.54 A with a glove, all of it at the end
of a metre, every part at its worst:

| from Mamka to the LDO | resistance | drop |
|---|---|---|
| the converter: 1.00 V ± 1% at FB (SNVSBY5B, 7.5) and 1% resistors | | 3.92 V instead of 4.02 V |
| Mamka's π filter, two chokes and two beads side by side | ≤ 0.185 Ω | 100 mV |
| Mamka's IDC, +4 V and ground on one contact each | ~2 × 20 mΩ, an estimate (3M's sheet not read) | 22 mV |
| the harness in the backpack, 20 cm of 28 AWG, one wire each way | 2 × 48 mΩ | 52 mV |
| the PT 24-61, size 20 contacts (Amphenol: < 55 mV at 7.5 A) | 2 × 7 mΩ | 8 mV |
| a metre of 1785/16 at UL 1571's 239 Ω/km, +4 V on two wires, ground on six | 0.16 Ω | 86 mV |
| the module's IDC, two contacts for +4 V, six for ground | ~13 mΩ | 7 mV |
| **at the LDO** | | **≥ 3.64 V**, ~3.81 V from typical figures |

- **The suit's lines hold** the 3.6 V at the worst corner. The glove's own TPS7A2033, behind the
  wrist's two wires, loses ~17 mV more at its ~0.12 A.
- **The head line** at its worst millisecond, ~1.0 A while the radar chirps with two motors
  running, falls to ~3.41 V at the worst corner, ~3.63 V from typical figures. Nataša's LDO
  still holds 3.3 V: at her ~160 mA its dropout is about half the 140 mV, inferred from the
  sheet's figure at 300 mA. A motor's overdrive is weaker for that millisecond only.
- **The harness is the weak link:** a single 28 AWG wire each way. It stays short, ~10–20 cm,
  from Mamka's headers to the PT 24-61 in the shell; 10 cm gives back ~26 mV.

## Cable length

The cable runs at most about a metre each way from Mamka. TI's cautious RS-485 rule
(length in metres × rate in bit/s below 10⁷) gives only 0.5 m at 20 Mbit/s; TI itself says
today's cables do better. A metre therefore needs to be confirmed by measurement.

## Clock: a one-way RS-485 channel

[Mamka](../mamka/README.md) sends the clock straight from her oscillator through buffers and five
drivers, one per line, and a line's clock goes out when its driver's DE is raised (see
[Bring-up](SOFTWARE.md#bring-up)). The blocks on a line receive it from one pair.

## Drivers on a block

| driver | count | pair |
|---|---|---|
| TI THVD1452 (full duplex, DE/RE) | 2 | data: the pair from the master and the return pair |
| TI THVD1450 (half duplex) | 1 | clock, receive only |

Expected wiring: the first THVD1452 receives from the master on A/B and drives the return pair
on Y/Z, its driver switched by DE from the UART. The second THVD1452 receives the return pair on
A/B and so gives the echo. The THVD1450 receives the clock.

Every pair is terminated at both ends with 120 Ω, for the 3M 1785's 118 Ω: at Mamka, and at
the last block by a solder jumper that every block has, closed on the last one. A driver then
sees the two in parallel, ~60 Ω, close to the 54 Ω the datasheets test with (see
[Mamka](../mamka/HARDWARE.md#lines)).

All three drivers run from 3 to 5.5 V at up to 50 Mbit/s; on a block they run from 3.3 V (see
[power](#power)). We considered M-LVDS too, but stayed with classic RS-422/485 because of what
the drivers and the parts around them consume.

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
| [Mamka](../mamka/README.md) | the backpack | two processors, five line drivers at 19.66 Mbaud and five clock drivers at 9.83 MHz, the converters, the clock |
| [Terem](../terem/README.md) | under the ROCK 5T | ten PCIe Gen 3 pairs at 85 Ω in 0.5 mm pitch; 0.8 mm thick for the M.2 sockets |
| the sensing module | [Rubaška](../rubaska/HARDWARE.md#sensing-module) | the ADS1299 beside a processor and line drivers on one narrow board: analog and digital returns apart on a plane |
| the IMU board | [Rubaška](../rubaska/HARDWARE.md#the-imu) | small; the same stack for the same order, I3C over a plane |
| the glove's board | [Rubaška](../rubaska/HARDWARE.md#the-glove-and-the-foot) | five processors on the suit clock and Interconnect on the back of the hand; the same stack |
| [Míša](../misa/README.md) | the headband | the radar module, the ultrasound, a processor |
| [Nataša](../natasa/README.md) | the headband | I2S, the DAC and the amplifier beside the processor |

Beside them two flexible circuits, no boards but drawn the same way: the band's strip,
polyimide of two layers, signals and a ground, from JLCPCB, and the glove's stretchable circuit,
copper on TPU, from a maker of such (see
[Rubaška](../rubaska/CONSTRUCTION.md#electrodes)).

The ADS1299's own example layout is drawn for a minimum of two layers, with inner layers for
power where there are more (its datasheet, 12.2); it is the processor and the drivers on the same
board, and the module's narrow shape, that make the plane worth having there. Thickness follows
the board: 0.8 mm where an M.2 socket demands it, otherwise the house's standard 1.6 mm, and
thinner for the IMU board and the glove's board if the suit asks, decided at construction. The
rest of the family is software or bought: Baťa and Deduška, the BMS, the cables and connectors.

## Open questions

- cable length: confirm by measurement that a metre of 3M 1785 carries ~20 Mbit/s,
- the IDC sockets on the 3M 1785's flat stretches, tried on a sample, and where its shield
  connects: at Mamka only, or at both ends,
- the lines untwisted on the 3M 3517: the eye at 20 Mbaud over 2 m, and a band's strip
  alongside, read by an ADS1299.
