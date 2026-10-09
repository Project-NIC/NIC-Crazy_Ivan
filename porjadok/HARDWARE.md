<div align="center">

# Porjadok: hardware

**What every module shares in copper:** the power rails and their budget, the lines, the cable and
its connectors, and the drivers on a block.

↑ [Porjadok](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## Power

The suit's power is *Pitanije*, a Russian word that means both food and a power supply: from
[Babuška](../babuska/README.md) through [Ključnica](../babuska/HARDWARE.md#the-bms) and Mamka's
converters down to the LDOs on every module.

The suit runs from a sodium-ion battery of 12 V nominal, charged between 20 and 80%.
[Mamka](../mamka/HARDWARE.md#converters) makes two supply rails from it with LMR43610 buck
converters at 2.2 MHz: **3.7 V** for the digital parts, a converter for each line, and **6 V** for
the analog parts, one converter for the whole suit. Each module brings them down with its own
LDOs: 3.3 V for everything digital, 5 V for the analog side. The RS-485 drivers run from 3.3 V as
well, which lowers the current on the lines. How a sensing
module does it is described under [Rubaška](../rubaska/HARDWARE.md#power).

**Budget** of the sensing modules: the average from typical datasheet figures, the peak with the
processor at its datasheet maximum and the line driver sending:

| rail | one module, average | one module, peak | 16 modules |
|---|---|---|---|
| 3.7 V | ~69 mA | ~135 mA | ~1.10 A, ~4.1 W |
| 6 V | ~8 mA | ~8 mA | ~0.13 A, ~0.77 W |

- On a line only one driver sends at a time, so a line of four modules takes ~0.3 A on the
  3.7 V rail, ~0.42 A at worst.
- The digital rail at 3.7 V instead of 4 V saves ~0.3 W across the suit. The analog rail stays
  at 6 V: 5.5 V would save only ~0.06 W, and the headroom helps the TPS7A47 reject ripple from
  Mamka's converters.

## Links between boards

The lines are the *Pupovina*, Russian for the umbilical cord: they bring Mamka's children, the
[Rebjata](../rubaska/HARDWARE.md#sensing-module), power, the clock and data.

There are four lines, each carrying two to four basic blocks, 8 to 16 in all. Fully populated,
that is 16 ADS1299 and 64 ICM-42688-P. A fifth line, the same, goes to the head, for
[Nataša](../natasa/README.md) and other units there. The four body lines end at the body's STM32H562
on [Mamka](../mamka/README.md), which acts as a bridge: it puts the data together and hands it to
Baťa over SPI. The head line ends at her second STM32H562.

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

The RP1's UARTs (6.25 Mbit/s at most) are not used for the lines.

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
- A 1.27 mm flat cable fits an ordinary IDC socket with two rows at 2.54 mm, 2 × 5 for ten
  wires. The 1785/10 is 16.0 mm wide and 3.0–3.8 mm thick. A socket can be pressed anywhere on
  a flat stretch, so the taps sit along one cable.
- The wires: 6 for the three pairs (from the master, to the master, the clock) and, for power,
  2 × ground, 1 × +6 V and 1 × +3.7 V, 10 positions. Each supply wire is twisted with a ground
  wire as a pair of the cable. If the drop is too large, 4 × ground,
  2 × +6 V and 2 × +3.7 V, 14 wires, on the 16-wire 1785/16 with two spare; at the backpack's
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
for the data than for what the line sends out towards the electrode leads and picks up. In a
flat cable the two wires of a pair lie 1.27 mm apart, so their loop is small even untwisted,
and the 3517's shield all round holds the rest (20 dB on average).

- **One cable for everything:** the same 3517 as the electrode leads (see
  [Rubaška](../rubaska/CONSTRUCTION.md#electrodes)).
- **Taps anywhere:** an untwisted flat cable has no flat stretches to wait for, so a socket can
  be pressed on at any point.
- **Ground wires between the pairs,** so that the 9.8 MHz clock does not talk into the data:
  ground, data down, ground, data up, ground, clock, ground, then the supply. That takes the
  3517/14 or /16 instead of ten wires. Adjacent wires have 119 Ω, so the termination stays
  120 Ω.
- **It holds if two tests pass:** 2 m of 3517 carries the line at 20 Mbaud with an open eye, and
  an electrode lead laid alongside it, read by an ADS1299, shows nothing of it in the data.
  Then the twist goes.

Drop on 1 m of cable at the worst current of a line, ~0.42 A on the 3.7 V rail (see
[power](#power)):

| wire | +3.7 V on one wire | ground on two wires | total |
|---|---|---|---|
| 28 AWG, 7 × 0.127 mm, ~0.2 Ω/m | 84 mV | 42 mV | 126 mV |
| the same, wires doubled | 42 mV | 21 mV | 63 mV |

The TPS7A2033 needs ~3.44 V at its input (140 mV of dropout at 300 mA, a typical figure; the
sheet gives no maximum), so 3.7 V leaves
~0.26 V: one wire per rail does, two give a margin. The 6 V rail carries little, ~8 mA per
module, so one wire is plenty.

## Cable length

The cable runs at most about a metre each way from Mamka. TI's cautious RS-485 rule
(length in metres × rate in bit/s below 10⁷) gives only 0.5 m at 20 Mbit/s; TI itself says
today's cables do better. A metre therefore needs to be confirmed by measurement.

## Clock: a one-way RS-485 channel

[Mamka](../mamka/README.md) sends the clock through buffers and five drivers, one
per line. The blocks on a line receive it from one pair.

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

Eight boards are drawn, every one of them with the same four layers: signal, ground, power with
ground, signal, so that every trace has a plane under it and the ground is never cut by a trace.
Even the small ones take it: a four-layer board costs little more than a two-layer one at the
sizes here (an estimate; the house's price list decides), and one stack means one set of rules,
one impedance table and one order.

| board | where | what asks for the planes |
|---|---|---|
| [Mamka](../mamka/README.md) | the backpack | two processors, ten line drivers at 19.66 MBd, the converters, the clock |
| [Terem](../terem/README.md) | under the ROCK 5T | ten PCIe Gen 3 pairs at 85 Ω in 0.5 mm pitch; 0.8 mm thick for the M.2 sockets |
| [Kormilica](../kormilica/README.md) | on a Raspberry Pi's header | one PCIe lane, two converters; only with a Raspberry Pi |
| the sensing module | [Rubaška](../rubaska/HARDWARE.md#sensing-module) | the ADS1299 beside a processor and line drivers on one narrow board: analog and digital returns apart on a plane |
| the IMU board | [Rubaška](../rubaska/HARDWARE.md#the-imu) | small; the same stack for the same order, I3C over a plane |
| the Vnučka | [Rubaška](../rubaska/HARDWARE.md#the-glove-and-the-foot) | small; the same stack |
| [Míša](../misa/README.md) | the headband | the radar module, the ultrasound, a processor |
| [Nataša](../natasa/README.md) | the headband | I2S, the DAC and the amplifier beside the processor |

The ADS1299's own example layout is drawn for a minimum of two layers, with inner layers for
power where there are more (its datasheet, 12.2); it is the processor and the drivers on the same
board, and the module's narrow shape, that make the plane worth having there. Thickness follows
the board: 0.8 mm where an M.2 socket demands it, otherwise the house's standard 1.6 mm, and
thinner for the IMU board and the Vnučka if the suit asks, decided at construction. The rest of
the family is software or bought: Baťa and Deduška, the BMS, the cables and connectors.

## Open questions

- cable length: confirm by measurement that a metre of 3M 1785 carries ~20 Mbit/s,
- the IDC sockets on the 3M 1785's flat stretches, tried on a sample, and where its shield
  connects: at Mamka only, or at both ends,
- the lines untwisted on the 3M 3517: the eye at 20 Mbaud over 2 m, and an electrode lead
  alongside, read by an ADS1299.
