<div align="center">

# Mamka: hardware

**The board:** what is on it, both processors' pins, the header, the lines, the clock, the helper
functions and the whole suit's power.

↑ [Mamka](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## What is on it

| part | package | count | what it does |
|---|---|---|---|
| STM32H562RG | LQFP64, 10 × 10 mm | 2 | processor 1, the time master and the bridge for the body; processor 2, the head, the sound, the battery and the power |
| SWD pads | | 2 | one set for each processor, for a programmer on the bench |
| SiTime SiT8008BI-21-33N-9.830400D | 3.2 × 2.5 mm | 1 | the suit's clock, 9.8304 MHz: a MEMS oscillator, ±20 ppm in all (tolerance, temperature, supply, load and the first year's ageing) over −40…+85 °C, 3.3 V, 4.5 mA at most, pin 1 without function; 0.1 µF at its VDD |
| SN74LVC126A | quad buffer, 14 pins | 1 | the clock from MCO1 to the clock drivers of four lines |
| SN74LVC1G126 | single buffer, 5 pins | 1 | the same for the fifth line |
| THVD1451 | 8 pins, full duplex, no enables | 5 | a line's data: drives the pair to the blocks, receives the return pair |
| THVD1450 | SOIC-8, VSSOP-8 or VSON-8 | 6 | five drive the lines' clock, one talks to the BMS |
| LMR43610R3RPER | VQFN-HR, 2 × 2 mm | 8 | Mamka's own 3.3 V; 3.7 V for each of the five lines; 6 V for the suit; 5 V for the fan |
| SWPA252012S2R2MT | 2.5 × 2.0 mm | 12 | the π filters behind the six suit rails, two chokes side by side each |
| GZ2012D301TF | 2.0 × 1.25 mm | 12 | the beads behind them, two side by side each |
| EEHZA1H470P | SMD 8 × 10.2 mm | 2 | the bulk on the battery input: 47 µF 50 V hybrid polymer, NIC-Heimdall's house part |
| socket, 2 × 20 | 2.54 mm grid | 1 | onto Baťa's header, or Kormilica's on a Raspberry Pi |
| IDC box header, 2 × 5 | 2.54 mm grid | 5 | one per line, for its 3M 1785 flat cable: three pairs and the supply |
| Noctua NF-A4x10 5V PWM | 40 × 40 × 10 mm | 1 | the backpack's fan: 4 wires, 5 V, 0.07 A, its own driver inside |
| 4-pin PC fan header | 2.54 mm grid | 1 | the fan's +5 V, ground, PWM in and speed out |

The STM32H562 (datasheet DS14258) in LQFP64 has 49 I/Os (53 is VFQFPN68's), 4 SPIs, 5 USARTs, 5
UARTs and 2 SAIs (table 2), up to four I2Cs with Fast-mode Plus (1 Mbit/s), 640 KB of RAM, and two
GPDMA controllers of eight channels each (section 3.16). Its USART reaches 20 Mbaud. The STM32H523,
the modules' part, has 4 USARTs, 2 UARTs and 4 SPIs, three with I2S, in LQFP64 (DS14540), and 272 KB
of RAM. It might do for processor 2, its I2S in an SPI as on Nataša, but processor 1 needs the
larger memory (see [memory](SOFTWARE.md#memory)); that is to check in STM32CubeMX.

**Processor 1's pins**

| what | pins | where |
|---|---|---|
| the suit's oscillator | 1 | PH0-OSC_IN, the HSE in bypass |
| the suit clock out, and the gate on its buffers | 2 | MCO1 on PA8 (AF0); the buffers' OE on PC8 |
| the clock for processor 2 | 1 | MCO2 on PC9 (AF0), the same 9.8304 MHz |
| four body lines: to the blocks and from them | 8 | TX and RX at 19.66 Mbaud, AF7: USART2 on PA2 and PA3, USART3 on PB10 and PC4, USART6 on PC6 and PC7, USART1 on PB6 and PB7 |
| two SPIs to Baťa, as the slave | 8 | NSS, SCK, MISO, MOSI: the first SPI1 on PA4–PA7 (AF5), the second SPI3 on PA15, PC10, PC11, PC12 (AF6) |
| "data ready" to Baťa | 1 | PB1 |
| the UART to Baťa | 2 | UART4: TX on PA0, RX on PA1 (AF8) |
| Baťa's 3.3 V from header pin 1 | 1 | PC0, read as "Baťa is up" |
| SWD | 2 | PA13 SWDIO, PA14 SWCLK |
| status LED | 1 | PB0 |
| **total** | **27** | 22 I/Os free |

**Processor 2's pins**

| what | pins | where |
|---|---|---|
| its clock in | 1 | PH0-OSC_IN in bypass, from processor 1's MCO2 (DS14258, 5.3.8: 4–50 MHz) |
| the head line: to Nataša and from her | 2 | USART3 at 19.66 Mbaud: TX on PC10, RX on PC11 (AF7) |
| the SAI to Baťa, as the I2S master | 4 | SAI1 (AF6): SCK_A on PC6, FS_A on PC5, SD_A on PC1, SD_B on PA3; block A the master, block B synchronous to it, one data direction each |
| the control channel to Baťa: I2C as the slave | 2 | I2C1 (AF4): SCL on PB6, SDA on PB7, both Fm+ pins (FT_f, FT_fa) |
| "a message waiting" to Baťa | 1 | PC4 |
| the BMS | 3 | UART5 at 9,600 Bd (AF8): TX on PC12, RX on PD2, DE on PC8 |
| EN and PGOOD: the first and the last of the 3.7 V chain, the 6 V, the computers' supply | 6 | the 3.7 V chain: EN PA4, PGOOD PA5; the 6 V: EN PA6, PGOOD PA7; the computers: EN PB1 (Kormilica's LM61460 EN, Terem's eFuse SHDN), PGOOD PB2, to Kormilica or Terem; the fan's 5 V follows the computers' EN |
| Budilnik: HOLD to Mamka's own 3.3 V converter's EN | 1 | PB5, through a diode (see [Budilnik](#budilnik)) |
| Baťa's 3.3 V from header pin 1 | 1 | PC0, read as "Baťa is up" |
| the start button | 1 | PA2, a wake-up pin (WKUP2), through a divider from the button's node |
| the GPS, if fitted: UART and PPS | 0–3 | UART4: TX on PA0, RX on PA1 (AF8); the PPS on PA15 into TIM2_CH1 (AF1), a 32-bit timer |
| the backpack's fan | 2 | the PWM at 25 kHz on PB8, TIM4_CH3 (AF2), open-drain on a 5 V-tolerant pin (FT); the speed on PB4 into TIM3_CH1 (AF2), pulled up to 3.3 V |
| SWD | 2 | PA13 SWDIO, PA14 SWCLK |
| status LED | 1 | PB0 |
| **total** | **27–30** | 22 I/Os free, 19 with the GPS |

- The pins come from DS14258's pinout (figure 5) and alternate functions (tables 15 and 16).
- **Not SPI2 on PB13 and PB14:** with MISO on PB14 a slave transmits at 6 MHz at most, and with
  SCK on PB13 a master at 3 MHz (table 115, notes 2 and 3). SPI1 and SPI3 transmit at up to
  43 MHz as a slave at 2.7–3.6 V, above the ROCK 5T's 37.5 MHz, and take 4- to 32-bit frames
  (table 10).
- PC13 to PC15 hang on the backup domain's power switch: 2 MHz and 30 pF at most, and no
  current to source (table 14, note 3). They stay free on both.
- PA4 and PA5 are TT pins, which take at most VDD + 0.3 V (table 20), so the pull-up on the
  3.7 V chain's PGOOD at PA5 goes to Mamka's 3.3 V, not to the 3.7 V rail.
- PB8 drives the fan's PWM at 5 V, and above 4 V its internal pull-up and pull-down must stay
  off (table 17, note 6).

The DMA channels are laid out in STM32CubeMX. Both processors keep BOOT0 pulled
low on the board; nothing on the header resets them (see [firmware](SOFTWARE.md#firmware)).

## On Baťa's header

Mamka sits straight on the 40-pin header of a ROCK 5T, or on top of Kormilica on a Raspberry Pi
(see [Kormilica](../kormilica/CONSTRUCTION.md#on-the-header)), a socket on her underside. From
the header she takes only the data pins, the eight grounds and pin 1 as a signal: no 5 V and no
3.3 V, since she feeds herself. Over the computer she is only a strip with
that socket; the rest reaches out past the computer's edge on the header's side. That wing
carries the converters, the connectors and the tall parts: the hybrid polymers stand 10.2 mm.
Nothing lies over the Raspberry Pi's Active Cooler, and nothing over Mamka (see
[Babuška](../babuska/CONSTRUCTION.md#the-backpack)). The strip screws to the computer's two holes on
the header's side, the wing's outer edge to the insert on two spacers of its own; the ROCK 5T's
holes come from its 2D drawing, and the strip takes both pairs if they do not collide. On the
ROCK 5T the same edge carries its USB-C beside the header (Radxa's photo), the port for the
glasses, so the wing leaves it free.

| header pins | Radxa ROCK 5T | Raspberry Pi 5 | to Mamka |
|---|---|---|---|
| 19, 21, 23, 24 | SPI0_M2 with chip select 0 | SPI0 on GPIO 8–11 with one chip select (overlay `spi0-1cs`) | processor 1: the first SPI |
| 7 | SPI1_M1's chip select 1 | GPIO 4, SPI3's chip select (overlay `spi3-1cs-pi5`, Pi 5 only) | processor 1: the second SPI's chip select |
| 11, 13, 15 | SPI1_M1: SCLK, MOSI, MISO | plain GPIOs, left as inputs | processor 1: the second SPI, through 33 Ω |
| 26, 31, 29 | plain GPIOs, left as inputs | SPI3: SCLK on GPIO 7, MOSI on 6, MISO on 5 | the same lines, through 33 Ω |
| 12, 35, 38, 40 | I2S2_M1 | PCM / I2S on GPIO 18–21 | processor 2: the SAI |
| 36 | GPIO3_B1, an input | GPIO 16, an input | processor 1: "data ready" |
| 3, 5 | I2C7_M3, with the board's audio codec off | I2C1 on GPIO 2 and 3 | processor 2: the control channel |
| 37 | GPIO1_A7, an input | GPIO 26, an input | processor 2: "a message waiting" |
| 8, 10 | UART2_M0, its debug console | UART0 on GPIO 14 and 15 | processor 1: the UART |
| 1 | its 3.3 V | its 3.3 V | both processors: read as "Baťa is up" |
| 6, 9, 14, 20, 25, 30, 34, 39 | ground | ground | ground |
| 2, 4 | its own 5 V | 5.1 V from Kormilica | not taken |
| 16, 32 | GPIO3_A4, GPIO3_C2 | GPIO 23, 12 | EN of Umnica A and B to Terem's cable: traces only, the ROCK's PCIe driver drives them (see [Terem](../terem/HARDWARE.md#the-converters)) |
| 18, 33 | GPIO4_C4, GPIO3_A7 | GPIO 24, 13 | PGOOD of Umnica A and B from Terem's cable, or Kormilica's Hailo converter on 18: traces only, with 10 kΩ pull-ups from pin 1; no processor pin |
| 22, 27, 28 | | | free |

- **The second SPI on both sets at once,** so no jumpers: on each computer the other set is a
  plain GPIO left as an input. It hangs on the line as a stub of a few centimetres, which
  37.5 MHz bears; a scope is to confirm it. The system must not turn those pins to outputs; the
  33 Ω, NIC-Heimdall's house rule for a line that leaves the board, limit the current if it
  does.
- **Pin 1:** Mamka runs from the battery and could feed a switched-off computer through the
  protection diodes of its pins. Until pin 1 shows Baťa's 3.3 V, both processors keep their lines
  to him quiet, and every pull-up on the header, pins 3 and 5 for the I2C and 18 and 33 for the
  PGOODs, hangs on pin 1, the computer's own 3.3 V, never on Mamka's, so it vanishes with him.
- The ROCK 5T's pins come from Radxa's table for its V1.2; the 5T Industrial V2.01 differs only
  on pins 27 and 28, which Mamka does not use. All its GPIOs are 3.3 V.
- Pin 22 is a 1.8 V ADC input on the ROCK 5T, so "data ready" takes pin 36, free on both.
- On the Raspberry Pi SPI1 is not used: its pins are 18–21, the I2S. SPI0 keeps one chip
  select, so GPIO 7 stays free for SPI3.
- The ROCK 5T's SPIs take the even dividers of a 200, 150 or 24 MHz source: 37.5 MHz is the
  fastest under the STM32H562's 43 MHz as a slave (see
  [Porjadok](../porjadok/SOFTWARE.md#into-baťa)).

The control channel on pins 3 and 5 and the UART on pins 8 and 10 are described under
[software](SOFTWARE.md#the-control-channel): what travels on them, and the overlays the computers
need for them.

## Lines

Five lines leave Mamka: four for the suit, each with two to four basic blocks, and one for the
head, with [Nataša](../natasa/HARDWARE.md#the-head-line) and whatever else sits on the head. They
end at Mamka: the four body lines at processor 1, which puts the data together and hands it to
Baťa over SPI, the head line at processor 2, which hands its sound over the I2S and its few other
bytes over the I2C.
Details under [Porjadok](../porjadok/HARDWARE.md#links-between-boards).

Each line has on Mamka:

- **a THVD1451** for its data, full duplex with no enable pins: its driver is always on the
  pair to the blocks, where Mamka is the only one that sends, and its receiver takes the
  return pair. Every pair is terminated at both ends with 120 Ω, for the 3M 1785's 118 Ω: here
  on Mamka and on the last block. Between the blocks' frames nobody drives the return pair, and
  the receiver's failsafe then reads high;
- **a THVD1450** that drives its clock: DE high, the receiver off;
- **a 2 × 5 IDC box header** for the flat cable, the pairs side by side as the cable has them:

  | position | |
  |---|---|
  | 1, 2 | data to the blocks |
  | 3, 4 | data from the blocks |
  | 5, 6 | the clock |
  | 7, 8 | +3.7 V and its ground |
  | 9, 10 | +6 V and its ground |

The 3.7 V and the 6 V come from Mamka's own converters (see [Converters](#converters)). Five 2 × 5
box headers, ~20 mm each, take ~100 mm of edge, more than the Raspberry Pi's 85 mm. Inside the
backpack a short harness joins them to the PT 24-61 in the shell, the one connector of the whole
suit (see [Babuška](../babuska/CONSTRUCTION.md#the-backpack)).

## Clock

The suit's clock is *Chodiki*, Russian for the wall clock with weights that the whole household
lives by.

The board is the time master, and the clocks of the other parts are derived from it. The clock
travels over its own one-way RS-485 channel alongside the data bus, through buffers and five
drivers, one per line.

The base is **9.8304 MHz**, from a SiTime SiT8008 MEMS oscillator into processor 1's HSE in
bypass; processor 2 takes the same clock from processor 1's MCO2. It is the family of 120: the
IMUs' steps come at 120 Hz, the rate screens run at, so every snapshot on the output is a
measured one.
Every rate in the suit is the base multiplied or divided by a whole number, apart from the
sound's 48 kHz.

- The PLL makes the lines' 196.608 MHz from it: straight in (÷ 1), × 40 to a 393.216 MHz VCO,
  ÷ 2. The input and the VCO lie in the PLL's wide range of 2–16 MHz and 128–560 MHz, and
  196.608 MHz stays within VOS1's 200 MHz (DS14258, tables 48 and 21). The blocks' STM32H523 has
  the same ranges (DS14540, tables 46 and 20).
- MCO1 on PA8 hands the same 9.8304 MHz out undivided, through an SN74LVC126A quad buffer and an
  SN74LVC1G126 for the fifth line, one gate per line with 33 Ω in series, to each line's
  THVD1450. That is how Bifrost hands the clock to its spurs in NIC-Heimdall. The buffers' OE
  share one pin, so the clock reaches the lines only when Mamka lets it.
- MCO2 on PC9 hands it to processor 2's OSC_IN in bypass (DS14258, 5.3.8: 4–50 MHz), so the
  head line and the sound run from the same clock as the body.

| to | clock | from 9.8304 MHz |
|---|---|---|
| ADS1299 | 1.96608 MHz | ÷ 5 |
| ADS1299 samples | 3,840 SPS | ÷ 2,560 |
| ICM-42688-P, CLKIN input | 38,400 Hz | ÷ 256 |
| ICM-42688-P samples | 1,200 Hz | ÷ 8,192 |
| IMU steps | 120 Hz, 3,840 / 32 | ÷ 81,920 |
| the lines | 19,660,800 Bd | × 2 |

The ADS1299 accepts 1.5 to 2.25 MHz. Its sample rates then come out as 240, 480, 960, 1,920,
3,840, 7,680 and 15,360 SPS.

A 9.8304 MHz clock means roughly 19.7 Mbit/s on the line. Its THVD1450 driver handles up to
50 Mbit/s.

## Helper functions

Besides the clock, the board carries helper functions. The first is the sound bridge between
Baťa and [Nataša](../natasa/SOFTWARE.md#sound-across-the-suit) in the headband. The
SAI of processor 2 is the I2S master and runs stereo both ways: the headphones' sound from
Baťa, the two microphones back to it. The path is described there.

The SAI's clock comes from processor 2's PLL2 or PLL3 (the STM32H562 has three, DS14258): the suit
clock straight in (÷ 1), × 40 = a 393.216 MHz VCO, P ÷ 32 = 12.288 MHz, exactly 256 × 48 kHz. The
input and the VCO lie in the wide range of 2–16 MHz and 128–560 MHz (table 48), and the multiplier
is a whole number, so the PLL needs no fractional mode. The SAI divides 12.288 MHz by 4 to a bit
clock of 3.072 MHz, 64 per frame.

The second helper is the **GPS**, an add-on. Its module (a u-blox NEO-M8N) sits on Mamka's
board with a UART to processor 2, and its antenna on the backpack's shoulder strap, on a short
coaxial cable. No USB, no box of its own.

- The position, one to ten times a second, is a few bytes. It goes to Baťa over the control
  channel with "a message waiting", like the battery's state.
- The PPS, a pulse at the start of every second, goes into a timer of processor 2, which counts
  the suit clock. Mamka notes "UTC second so-and-so began at sample N" and sends that along. The
  suit's own time is never rewritten, only labelled; the pulse is caught to the timer's tick of
  ~102 ns.

## Mamka's own supply

Mamka feeds herself and her children from the battery, all on one part, TI **LMR43610R3RPER**
(see [Converters](#converters)). Her own 3.3 V uses the fixed version's VOUT/FB straight on the
output, with no divider (SNVSBY5B, device comparison table); the RT pin on ground sets 2.2 MHz.

| consumer | current |
|---|---|
| 2 × STM32H562, processor 1 at 197 MHz with every peripheral clocked, processor 2 slower | ~61 mA typical, ~82 mA at 85 °C each at 200 MHz in VOS1 (DS14258, table 28) |
| 5 × THVD1451, each driver always on, into two 120 Ω (~60 Ω) | ~35 mA each |
| 5 × THVD1450 driving the clock, the same load | ~35 mA each |
| the receivers, the buffers, the LED | a few mA |
| **total** | **~0.5–0.6 A of the 1 A** |

- Every branch sits behind the house π filter, and the processor's branch has the bead too
  (see [Rubaška](../rubaska/HARDWARE.md#power)).
- **The fan's 5 V:** one more LMR43610 with the divider 48.7 kΩ over 12.1 kΩ, 5.02 V, for the
  fan's 0.07 A. Its EN follows the computers': the fan runs while they do.
- **Nothing runs while the suit is off:** Mamka's own 3.3 V converter is held off, and the start
  button and processor 2 wake it and let it go, see [Budilnik](#budilnik) below.

## Budilnik

*Budilnik*, Russian for the alarm clock: it wakes the household with one press, and when everyone
has gone to bed it lets the house go dark. The suit starts like a car with a start button and
switches itself off completely when it is done; nothing on Mamka draws from the battery in
between.

- **The latch** is the EN pin of Mamka's own 3.3 V LMR43610: 100 kΩ to ground hold it off
  (below the 0.5 V wake threshold the converter sleeps at 0.25 µA, SNVSBY5B). The start button
  joins the battery to a node, and 100 kΩ from that node to EN lift it to 5–8 V at 11.5–16 V,
  above the 1.23 V precision threshold and under the pin's 42 V rating. The converter starts,
  processor 2 boots in milliseconds and drives **HOLD**, PB5, high through a diode onto EN:
  ~3 V, enough to hold. The button may be let go. Processor 2 reads the button on PA2 through a
  divider of 100 kΩ over 33 kΩ from the node, 2.9–4 V, within the FT pin's 5 V.
- **Starting:** hold the button until the status LED lights, a few tens of milliseconds; then
  processor 2 raises the lines' converters and the 6 V in order, and the computers' supply on
  Kormilica or Terem, and the suit comes up.
- **Stopping:** Baťa asks for it (message 0x12), or the button is held for five seconds.
  Processor 2 tells the computers to halt, drops their EN once their PGOOD has fallen or
  after a timeout, drops the lines and the 6 V, and lets HOLD fall: the 3.3 V converter stops
  and Mamka is off, processor 2 with her. What stays on the battery then is the BMS, the eFuses
  in their 21 µA sleep and the LM61460s with EN low: tens of microamps.
- **A hang** ends the same way by itself: the watchdog resets processor 2, its pins go to
  inputs, HOLD falls and the suit is off, unless the button is being held.

## Converters

All the suit's rails come from one part on Mamka, TI **LMR43610R3RPER** (1 A, datasheet
SNVSBY5B), the RT version whose VOUT/FB pin takes either the output for a fixed 3.3 V or a
divider for any other voltage. Mamka's own 3.3 V and the fan's 5 V use the same part.

| | |
|---|---|
| input | 3.0–36 V, transients to 42 V |
| output | up to 1 A, set by a divider from 1 V to 95% of the input |
| switching | 2.2 MHz (2.1–2.3 MHz) with the RT pin tied to ground |
| package | VQFN-HR, 9 pins, 2 × 2 mm |

- **The cell** is NIC-Heimdall's buck cell ([galvani/HARDWARE.md][heimdall-buck], *The buck
  cell*):

  | position | value |
  |---|---|
  | inductor | 4.7 µH, shielded, saturation 2.1 A or more, the LMR43610's highest peak current limit |
  | divider on VOUT/FB, against 1.00 V | bottom 12.1 kΩ; top 33.2 kΩ → 3.74 V, 60.4 kΩ → 5.99 V |
  | C_FF across the top resistor | 22 pF C0G |
  | C_IN | 4.7 µF 50 V X7R 1206 + 100 nF |
  | C_OUT | 3 × 10 µF 50 V 1206 + 100 nF |
  | VCC · BOOT | 1 µF · 100 nF |
- **At its highest frequency, with no clock.** With the RT pin on ground the converter runs at
  2.2 MHz with no resistor, no clock from the processor and no extra trace.
- **The inductor's ripple:** from 12 V to 3.74 V, ~0.25 A, a quarter of the 1 A, inside the
  20–40% the datasheet asks for.
- **A converter for each line on 3.7 V, one for the whole suit on 6 V.** Five make 3.7 V, one
  for each of the four suit lines and one for the head line; one makes 6 V:

  | rail | load | capacitance it charges at start | start |
  |---|---|---|---|
  | 3.7 V, a suit line | ~0.27 A on average, ~0.42 A at worst | ~650 µF: four modules' 6TPE100M with their ceramics, the π filter, C_OUT | within the 3.5 ms soft start; at its fastest, 2 ms, briefly at the current limit, done in ~2.9 ms |
  | 3.7 V, the head line | ~0.35 A on average, ~1.05 A for a millisecond when the radar chirps while two motors run | ~900 µF, Nataša's two polymers and Míša's among them | the same |
  | 6 V, the whole suit | ~0.13 A, ~8 mA a module | ~1.4 mF: sixteen modules' 10TPE47MAZB with their ceramics | at the current limit, ~7–8 ms |

- **At the current limit** the converter holds the inductor's current between its high-side peak
  and low-side valley limits, cycle by cycle, and delivers about their average: at least
  ~1.13 A, from 1.4 A and 0.85 A at their minimum (SNVSBY5B, 7.5 and 8.3.9). It does not shut
  down; the current stays there even with the output at zero. A large capacitance so only
  charges more slowly.
- **TI's limit:** the output capacitance should stay under about ten times the design value or
  1000 µF, or else the start at full load and the loop's stability are to be studied (9.2.2.4).
  The 3.7 V lines stay under 1000 µF. The 6 V's ~1.4 mF is to be checked by simulation and
  measurement; should it fail, 6 V splits into two converters for two lines each, ~700 µF.
- **The lines come up one after another:** each 3.7 V converter's PGOOD drives the next one's
  EN, so processor 2 needs only the first EN and the last PGOOD, and the battery takes one
  line's inrush at a time.
- **Each line on its own:** a short or a faulty module takes down only its own line.
- **The battery input** at Mamka's terminals carries NIC-Heimdall's house input bank
  ([galvani/HARDWARE.md][heimdall-buck], where it sits on every 12 V node), doubled: two 47 µF
  50 V hybrid polymers, Panasonic **EEHZA1H470P** (ZA series, SMD 8 × 10.2 mm, 30 mΩ, 1.8 A of
  ripple at 100 kHz, 105 °C / 10,000 h), with 10 µF 50 V 1206 and 100 nF. The bulk holds the
  input up at the end of the cable from the battery; each converter keeps its own C_IN by its
  pins. The 50 V stays although the pack gives at most 16 V: a battery plugged into a board
  rings on the cable's inductance above its own voltage, and the hybrid's ESR damps that.

## Filtering

The ripple of the converters is filtered away on its way to the chips, by a chain of cheap
parts:

1. **On Mamka,** right behind each converter: a π filter with the modules' parts, two
   chokes SWPA252012S2R2MT side by side (2.2 µH, 0.17 Ω and 1.85 A each, so 1.1 µH and
   0.085 Ω) with 10 µF + 100 nF on both sides, then two ferrite beads GZ2012D301TF side by side
   (300 Ω at 100 MHz, at most 0.2 Ω and 500 mA each). At a suit line's worst 0.42 A the pair
   drops ~0.08 V. No polymer sits at the board's outputs: the lines' bulks sit at the modules,
   and one here would only add to what the converter charges at start. The converters sit on
   one side of the wing with copper poured under them, away from the clock and the processor.
2. **The cable:** every supply wire runs twisted with a ground wire as a pair, so plus and minus
   lie against each other. Mamka is some tens of centimetres from the modules.
3. **On the module:** capacitors at the input, the LDO, and behind it a π filter with a choke
   whose self-resonance lies at 69 MHz (see [Rubaška](../rubaska/HARDWARE.md#power)). The digital
   branch has the same.
4. **Inside the ADS1299:** its own supply circuits behind AVDD.

**Polymers and ceramics.** A ceramic capacitor loses capacitance under DC voltage. The house
rule's 50 V parts lose little at 3.3–6 V, which is why it takes them, but the loss grows at the
battery's 7–16 V.

- **A polymer bulk wherever a cable arrives:** the battery input (the hybrid polymers above)
  and the modules' inputs (see [Rubaška](../rubaska/HARDWARE.md#power) and
  [Nataša](../natasa/HARDWARE.md#power)). Mamka's outputs carry none, to keep what each
  converter charges small (see [Converters](#converters)).
- **Ceramics stay where a datasheet puts them:** at a converter's VIN pins, its hot loop, and on
  its output, its control loop; at the LDOs; the 100 nF at every pin; the charge pumps.
- **The π filters' 10 µF stay ceramic.** At 3.3–6 V on 50 V their loss is small, and at the
  converters' 2 MHz a ceramic filters better than a polymer with its ESR and ESL. The exception
  is Nataša's motor branch, where a polymer behind the choke puts the corner below the motor
  drivers' 20 kHz.

One LC stage, 2.2 µH into 10 µF with its corner at ~34 kHz, takes ~2 MHz down by ~70 dB on
paper, and the chain has several. The LDOs reject best at low frequencies, where the EMG lies.
Neither the converter's exact frequency, nor a lock to the suit's clock, nor its pulse mode at
light load (this version has no forced PWM) therefore matters.

## The computers' supply

[Kormilica](../kormilica/README.md) feeds a Raspberry Pi on its header pins 2 and 4;
[Terem](../terem/README.md) feeds a ROCK 5T, Baťa or Deduška, through an eFuse on its DC jack,
and its Umnicas. Mamka drives the converter's EN or the eFuse's SHDN and reads their PGOOD on a
short cable, so she switches the computers on after the start button and off once they have
shut down (see [Budilnik](#budilnik)). Terem's cable has eight wires: four of them, the two
Umnicas' EN and PGOOD, only cross Mamka as traces to the header, where the ROCK's PCIe driver
drives the ENs and the ROCK reads the PGOODs (see [Terem](../terem/HARDWARE.md#the-converters)).

## Open questions

- both processors' pins checked against DS14258's pin and alternate-function tables (9 Oct
  2026): every signal on its pin at the AF given, all on LQFP64, no pin or peripheral twice,
  PA4 and PA5 TT, PB8 FT, WKUP2 on PA2; STM32CubeMX on a PC still to confirm the clock tree and
  lay out the DMA, 12 and 9 of 16 channels; whether
  the STM32H523 does for processor 2 is settled for now: it would (no SAI, the sound through an
  SPI in I2S mode, 9 DMA channels), but both stay STM32H562, one part and one firmware base,
- the second SPI on both sets of pins: the stubs at 37.5 MHz on a scope,
- the converters' ripple in the ADS1299 data: confirm by measurement,
- the 6 V converter's start into ~1.4 mF and its loop's stability: simulation and measurement;
  SNVSBY5B lists a hiccup time (tHICCUP, 30–75 ms) that its section 8.3.9 does not describe, so
  when the part hiccups, and whether a long start at the current limit triggers it, is to be
  found out first,
- the 3.7 V budget end to end, from the converter through the π filter, the cable and the PT
  24-61 to each module's LDO,
- no other helper function is planned; the clock, the sound bridge, Budilnik and the GPS are
  all the board carries.

[heimdall-buck]: https://github.com/Project-NIC/NIC-Heimdall/blob/main/galvani/HARDWARE.md
