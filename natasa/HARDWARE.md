<div align="center">

# Nataša: hardware

**The board in the headband:** the head line, the processor's pins, the microphones, the
headphones, the buttons, the motors, Míša's socket and the power.

↑ [Nataša](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## The head line

Nataša hangs on a line of its own, the fifth from [Mamka](../mamka/HARDWARE.md#lines), with the
same pairs, connector and frames as the suit's four. Other units on the head can join the same
line; Míša does not need to, it plugs into Nataša (see [Míša's socket](#míšas-socket)).

## The processor's pins

Nataša's **STM32H523RE** in LQFP64 has 49 I/Os (DS14540, table 2). She needs 30; the pins come
from DS14540's pinout (figure 7) and alternate functions (tables 14 and 15), the numbers from the
LQFP64 column of its pin table:

| what | pins | where |
|---|---|---|
| the suit clock in | 1 | PH0-OSC_IN (5), the HSE in bypass, as on a block |
| the head line: transmit, the echo, DE, receive from the master | 4 | the block's pins and AFs, so one line driver serves both firmwares: USART1_TX PA9 (42), USART1_RX PA10 (43), USART1_DE PA12 (45), all AF7; UART4_RX PA11 (44), AF6 |
| the sound: one I2S, full duplex | 4 | SPI3 in I2S mode, AF6: CK PC10 (51), WS PA15 (50), SDO to the DAC PC12 (53), SDI from the microphones PC11 (52) |
| the headphone amplifier's EN; the DAC's GPO, its latched clock-error interrupt | 2 | PB2 (28), an output; PB10 (29), an input |
| the motors: four PWMs from one timer, the drivers' shared EN | 5 | TIM3_CH1–CH4 on PC6, PC7, PC8, PC9 (37–40), AF2; EN on PB1 (27) |
| the buttons | 8 | inputs on the internal pull-up, 33 Ω in series: the right temple PC0–PC3 (8–11), the left PA4–PA7 (20–23) |
| Míša's wire | 2 | USART2_TX PA2 (16), USART2_RX PA3 (17), AF7 |
| SWD and SWO | 3 | PA13 SWDIO (46), PA14 SWCLK (49), PB3 SWO (55), AF0 |
| status LED | 1 | PB0 (26) |
| **total** | **30** | 19 I/Os free |

- **The same line as a block:** USART1 transmits and reads itself back, UART4 receives from the
  master, the DE comes from the USART itself (see [Rubaška](../rubaska/HARDWARE.md#sensing-module),
  *The processor's pins*).
- **SPI3, not SPI2, for the I2S.** SPI2's I2S sits on PB12–PB15, and PB13 and PB14 are the USB-C
  controller's CC pins (FT_c in the pin table); SPI3's are plain pins. The I2S takes its kernel
  clock from PLL1's Q output (SPI3SEL = 000 in RCC_CCIPR3, RM0481 Rev 5): the suit's 9.8304 MHz
  ÷ 1, × 40, ÷ 32 = 12.288 MHz, and divides it to the 3.072 MHz bit clock, 64 per frame. One
  bit clock, one word clock and two data wires serve the DAC and both microphones: the DAC's
  BCLK and FSYNC and the microphones' SCK and WS hang on CK and WS, the DAC's DIN on SDO, the
  microphones' shared SD on SDI. Neither part needs an MCLK (see [headphones](#headphones)), so
  I2S3_MCK on PC7 is free for a motor.
- **The DAC's MD pins** are straps and its GPO reports a clock error (TAD5142, table 4-1); the
  microphones' L/R selects are straps too. Nothing is written to either.
- **TIM3** gives the four PWMs; TIM2, 32-bit, stays for counting the suit clock and the
  measurement's cycles.
- **The buttons are polled** with every frame (see [buttons](#buttons)), so they take no EXTI
  lines; any GPIO does, and two groups of four keep each temple's cable on one port.
- BOOT0 goes to ground through 10 kΩ, NRST to the SWD pads, each VCAP takes 2.2 µF with an ESR
  under 100 mΩ (DS14540, table 21), as on a block. PC13 to PC15 stay free: they hang on the
  backup domain's switch and drive no current (table 13, note 2).

## Microphones

Two digital MEMS microphones with the converter inside, so there is no ADC on the board:

| part | package | what it does |
|---|---|---|
| ICS-43434 (TDK InvenSense) | 3.50 × 2.65 × 0.98 mm, port at the bottom | MEMS microphone with a 24-bit I2S output; SNR 65 dBA, sensitivity −26 dBFS ±1 dB, up to 120 dB SPL; 1.65–3.63 V, 490 µA |

- **One on each side of the head**, for stereo. Both share the bit clock, the word clock and
  the data wire: one has its select pin on ground and takes the left channel, the other on
  3.3 V and takes the right.
- They go straight to the STM32H523: the data wire into its I2S input, beside the DAC's output
  on the same SPI.
- **High-performance mode**, which takes 23 to 51.6 kHz; 48 kHz falls inside. The low-power
  mode only reaches 18.75 kHz.
- **±1 dB of sensitivity** between parts, so the two need no calibration against each other.
- **16 bits are enough.** Full scale is 120 dB SPL (−26 dBFS at 94 dB SPL) and the noise sits
  at 29 dBA SPL (65 dB under 94 dB), so the microphone spans ~91 dB; 16 bits give 96 dB. Any
  bits below carry only the microphone's own noise. It sends 24 bits in a 32-bit slot, the most
  significant first, and the STM32H523 keeps the top 16 by taking 16-bit data in a 32-bit
  channel: the I2S supports that format in full duplex, and a receiver ignores the bits after
  its data length (RM0481 Rev 5, 58.9.5, figure 829). The transmitter leaves those bits "not
  significant", so the DAC sees noise below its 16th bit, under −96 dBFS, which does not matter.
- **The port is at the bottom:** the sound comes through a hole in the board under the
  microphone.

## Headphones

A DAC and a headphone amplifier, both set by their pins, with no registers to write:

| part | package | what it does |
|---|---|---|
| TAD5142 | VQFN-24, 4 × 4 mm, 0.5 mm pitch | the DAC (datasheet SLASF32A): set by its pins, with every MD pin on ground: I2S target, AVDD 3.3 V, 32-bit words, linear-phase filter, differential line out, stereo; its PLL takes the clock from BCLK and FSYNC, so it needs no MCLK, and 48 kHz at a 3.072 MHz BCLK is in its table 6-4; 2 Vrms differential, each output ±1.41 V around 1.65 V; ~17 mA at 48 kHz, under 1 mA asleep while the clocks stand |
| TPA6132A2 | QFN-16, 3 × 3 mm | the headphone amplifier: DirectPath, 25 mW into 16 Ω, 2.3–5.5 V, 2.1 mA; gain −6, 0, 3 or 6 dB on two pins |
| 3.5 mm stereo jack | | any wired headphones |

- The amplifier's outputs are centred on ground, from its own charge pump, so there are no
  output capacitors and the jack's sleeve goes straight to ground.
- Both run from 3.3 V. The DAC's AVDD and IOVDD come up in any order, its VREF takes at least
  1 µF and nothing else, and its MD pins are fixed before the clocks start, as straps are.
- The DAC is strapped to 32-bit words (MD1 and MD2 low; 24 bits is the other choice, table 6-3):
  the STM32H523 sends its 16 bits in a 32-bit slot, as it already does for the microphones' 64
  bit clocks a frame. The straps: MD0 to ground is I2S target mode (table 6-2), MD4 and MD5 low
  the differential line-out (table 6-9), MD6 low stereo (table 6-10), MD3 to ground as the
  target mode asks. Its GPO pin, a latched interrupt on a clock error (table 4-1), goes to a pin
  of the STM32H523 (see [the processor's pins](#the-processors-pins)).

**The amplifier's input** (TPA6132A2 datasheet, SLOS597B):

- **Differential:** each DAC output pair goes to its channel's INx+ and INx−, so noise on the
  ground between the two parts does not reach the headphones.
- **G0 and G1 on ground:** −6 dB, with 26.4 kΩ inside each input.
- **22 kΩ in series and 1 µF in each of the four inputs.** The DAC's outputs sit at 1.65 V,
  above the amplifier's input common-mode range of −0.5 to 1.5 V, so the capacitors take the DC
  off. At full scale each DAC output swings ±1.41 V; with 22 kΩ against the 26.4 kΩ inside, an
  input sees ±0.77 V, inside the ±1 V the datasheet gives for a direct drive (8.2.1.2.1). The
  chain passes 0.27 × of the signal: the 2 Vrms differential gives 0.55 Vrms, ~19 mW into
  16 Ω, under the amplifier's 25 mW. The 1 µF with the ~48 kΩ puts the low corner at ~3 Hz,
  and the datasheet asks for input capacitors anyway, to keep the turn-on pop inaudible.
- **Around it:** 1 µF flying capacitor between CPP and CPN, 2.2 µF on HPVSS (at least the
  flying one), 2.2 µF on HPVDD and nothing else on that pin, 2.2 µF within 5 mm of VDD; all
  X5R or better.
- **SGND** goes to the ground terminal of the jack.
- **EN** is on a pin of the STM32H523: the amplifier comes on after the DAC runs and goes off
  before it stops, as the datasheet asks.
- Baťa sets the volume and holds a ceiling on it: 19 mW is still very loud in
  headphones.

## Buttons

Eight buttons, four at each temple or close by. A blind wearer finds them by where they sit;
each press is confirmed by a short vibration pattern of its own, for a deaf wearer too.

| part | package | count | what it does |
|---|---|---|---|
| C&K KSC2 | SMD, 6.2 × 6.2 × 3.5 mm, soft actuator | 8 | sealed tactile switch, IP67 against sweat; the stiffer KSC241J (3 N) so that a cap or a headrest does not press it |
| TPD4E05U06 | | 2 | ESD, one four-channel array for each temple's four lines, at the connector |

- **Each button between a pin of the STM32H523 and ground,** on the pin's own pull-up, with
  33 Ω at the processor: NIC-Heimdall's house rule for a line that leaves the board. Eight pins.
- **Read every cycle** with the frame, so no interrupts are needed. Nataša debounces them and
  sends one bit per button; 8 of the frame's 16 bits are taken.
- **A cable to each temple:** four lines and ground.

What the buttons do is under [software](SOFTWARE.md#buttons-and-vibration).

## Vibration

Four vibration motors in the headband give the signals: a warning from Soňa, an obstacle from
Míša, the beat from Nikita. They need no looking, and their patterns can differ: long and short
pulses, different repeat rates.

| part | package | count | what it does |
|---|---|---|---|
| KOTL C1027B603F (LCSC C2836604) | Ø10 × 2.7 mm | 4 | coin motor, ERM: 3.0 V rated, 2.7–3.3 V, 90 mA, 9,000 rpm |
| DRV2603 | WQFN-10, 2 × 2 mm | 4 | the driver, one per motor: PWM in, an ERM or an LRA out, 2.5–5.2 V (datasheet SLOS754C) |

- **One on each side of the head:** left, right, the forehead and the nape. With two
  microphones Soňa can tell the side a sound came from, Míša's obstacle ahead buzzes on the
  forehead, and Nikita's beat can take all of them, the "one" stronger.
- **The lower speed:** 9,000 rpm, a shake at ~150 Hz.
- **Straight from the line's 3.7 V,** not through the LDO, so the motors' current stays off the
  sound and the processor; their branch has its own choke (see [Power](#power)).
- **PWM from four channels of one timer** of the STM32H523 (the driver takes 10–250 kHz), and
  one EN shared by all four: five pins. LRA/ERM is tied low for ERM.
- **The duty cycle sets the drive:** 100% full forward, 50% nothing, 0% full reverse. The full
  scale is ~3.3 V into 20 Ω, 3.6 V open, the same at any supply, since the driver corrects for
  it. The motor runs at ~94% for its 3.0 V; 100% only for the 20–50 ms of overdrive at the
  start that the datasheet advises.
- **Braking:** at 0% duty, with EN still high, the driver drives the motor backwards and stops
  it. An ERM left to itself runs on after it is switched off and short pulses blur; braked, the
  patterns stay crisp. The brake is short: held too long, the motor turns backwards.
- **EN shared:** while any motor runs, EN stays high and the idle ones sit at 50%. A driver
  takes 1.7–2.5 mA with EN high, 0.3 µA with it low.
- **Supply:** the datasheet asks for the motor's highest voltage plus 250 mV. The line's 3.7 V
  less Mamka's filter, the cable and the choke leaves ~3.5–3.6 V. That is enough for
  3.0 V on the motor, which needs 3.25 V; the 3.3 V overdrive at the start, which needs 3.55 V,
  may come out a little weaker.
- **One 100 nF X5R or X7R** right at each driver's VDD, the only capacitor it asks for.
- **An LRA fits the same board:** a linear actuator that starts faster. LRA/ERM goes high, and
  the driver finds and follows its resonance by itself.
- **Two start at a time.** One motor takes 90 mA, more as it starts; two keep them at
  ~0.2 A, and the firmware starts the motors of one command 50 ms apart. The head line has a
  1 A converter of its own (see [Mamka](../mamka/HARDWARE.md#converters)), and four starting at
  once with the rest of Nataša would come close to it.

With an ordinary motor with an off-centre weight (ERM), its speed sets both how fast and how
strongly it shakes. Patterns of pulses are therefore the surer way to tell signals apart than
the frequency of the shaking itself.

The three-colour LEDs at eye level that Nataša started with are set aside: vibration does their
job better.

## Míša's socket

[Míša](../misa/README.md), the unit with the radar, the ultrasound and an IMU, plugs into one
socket on Nataša. Everything about obstacles is Míša's; Nataša carries its data and its power.

| part | package | count | what it does |
|---|---|---|---|
| JST GH, 4 positions | 1.25 mm pitch, with a lock | 1 | the UART both ways, 3.7 V and ground; JST's rating of 1 A a contact to confirm in its sheet |
| TPD4E05U06 | | 1 | ESD on the two UART lines, at the socket |

- **A UART both ways, two pins,** with 33 Ω at the processor, the house rule for a line that
  leaves the board, at exactly 1,228,800 Bd: the PLL's 196.608 MHz ÷ 160 on Nataša, the suit's
  9.8304 MHz ÷ 8, and the same from Míša's own oscillator of 9.8304 MHz.
- **"Measure":** Nataša has the suit's clock and sends Míša a *measure* container every 240
  cycles, 16 times a second, with the sample number, so the radar's frames start on the same
  ADS sample every time (see [software](SOFTWARE.md#míšas-wire)).
- **Up the line:** Míša's sphere, 112 B a frame, ~1.8 kB/s, rides in Nataša's frame's rotation,
  8 B a cycle, beside the microphones.
- **Safety without Linux:** Nataša reads the sphere as it passes and buzzes by herself when
  something in its middle row ahead is nearer than ~1 m or coming fast, even if Baťa hangs.
- **Power:** Míša takes the line's 3.7 V before Nataša's LDO, on a branch of its own, and makes
  its own rails. The radar draws ~1 W for about a millisecond a frame.

## Power

Nataša takes the head line's 3.7 V and splits it, with a choke in every branch as everywhere
else on the supplies: the house filter parts, each choke in a π filter of 10 µF + 100 nF on
both sides (see [Rubaška](../rubaska/HARDWARE.md#power)).

- **Míša** straight from 3.7 V through a π filter of its own, like the motors; its bursts stay
  off the LDO.
- **The motors** straight from 3.7 V through their own π filter with the SWPA252012S2R2MT, then
  the four DRV2603 with 100 nF each. Two motors, ~0.2 A, drop ~34 mV in the choke's 0.17 Ω.
  Behind the choke, beside its 10 µF + 100 nF, sits a 6TPE470MAZU.
- **What Nataša takes from the line,** from the parts' sheets: on the 3.3 V behind the LDO the
  STM32H523 ~50 mA typical and 84 mA at most (DS14540, table 26, as in a block), the three
  THVD receivers ~6 mA, the line driver ~37 mA for the 13% of a cycle her frame takes (~5 mA on
  average), the DAC ~17 mA (SLASF32A), the headphone amplifier 2.1 mA and ~12 mA more at full
  volume into 16 Ω, the two microphones ~1 mA, the LED ~2 mA: **~90 mA on average, ~160 mA at
  the peak**, inside the TPS7A2033's 300 mA. Straight from the 3.7 V the motors, two at once
  ~0.2 A with their drivers (see [vibration](#vibration)), and Míša's branch, ~60 mA on average
  and a burst of ~0.63 A for ~1 ms sixteen times a second while the radar chirps (its 2.1 W peak
  at ~90% in its converters, see [Míša](../misa/HARDWARE.md#the-board)). The head line's
  converter sees ~0.35 A on average and, at the worst coincidence of a chirp with two motors,
  ~1.05 A for a millisecond, which its current limit of at least 1.13 A carries (see
  [Mamka](../mamka/HARDWARE.md#converters)); the polymers at the inputs bridge the microseconds
  the converter's loop takes.
- **The LDO** to 3.3 V, the TPS7A2033 as in the sensing modules, and behind it a star of branches,
  each with its own π filter: the processor (choke and bead), the RS-485 drivers, the DAC, the
  headphone amplifier and the microphones. The parts' own capacitors from their
  datasheets sit at their pins.
- **At the input,** a polymer bulk where the cable arrives: Panasonic POSCAP **6TPE100M** (TPE
  series, case D2E), 100 µF 6.3 V, 7.3 × 4.3 × 1.8 mm, 25 mΩ at 100 kHz, 2.4 A of ripple,
  105 °C, the same as in the sensing modules; it is small so that the head line's converter
  charges little at start (see [Mamka](../mamka/HARDWARE.md#converters)). The motors' own polymer
  behind their choke is the **6TPE470MAZU** (case D15E), 470 µF 6.3 V, 7.3 × 4.3 × 1.4 mm,
  35 mΩ, 1.7 A of ripple, 85 °C / 2,000 h (5.0 V up to 105 °C), which carries their start. At
  1.4–1.8 mm both lie flat in the headband, where NIC-Heimdall's 50 V hybrid polymer stands
  10.2 mm tall. Others of the series in the same footprint: 6TPE330MAP (330 µF, 25 mΩ, 1.8 mm)
  and 6TPE220MI (220 µF, 18 mΩ, 1.8 mm, 105 °C).
- **The DRV2603 switches at ~20 kHz,** below a plain π filter's ~34 kHz corner. With the
  polymer behind the choke the corner falls to ~5 kHz (2.2 µH into ~480 µF), so the 20 kHz
  comes back through the choke ~19 dB down: at 20 kHz the polymer's 35 mΩ of ESR already
  outweighs its 17 mΩ of reactance. The choke's 0.17 Ω with the polymer's 35 mΩ damp the pair
  to a Q of ~0.3. The LDO keeps the rest off the 3.3 V. To check by simulation,
  with the rest of the filters.

## Open questions

- the microphones' data wire: whether it wants a pull-down while neither drives it, from the
  ICS-43434's datasheet; and that sheet itself, DS-000069, read once more: TDK's site did not
  serve it on 9 Oct 2026, DigiKey lists 64 dB and 550 µA where this page has 65 dBA and 490 µA,
  and which level of L/R gives the left channel is from memory,
- Míša's bursts and the motors against the head line's converter, measured: the budget above is
  from the sheets, and the radar's 2.1 W is Jorjin's peak figure,
- the pins in STM32CubeMX on a PC, as for the other boards: the clock tree and the DMA,
