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
| STM32H562RG | LQFP64, 10 × 10 mm | 2 | processor 1, the bridge for the body; processor 2, the head, the sound, the battery and the power |
| SWD pads | | 2 | one set for each processor, for a programmer on the bench |
| SiTime SiT8008BI-21-33N-9.830400D | 3.2 × 2.5 mm | 1 | the suit's clock, 9.8304 MHz: a MEMS oscillator, ±20 ppm in all (tolerance, temperature, supply, load and the first year's ageing) over −40…+85 °C, 3.3 V, 4.5 mA at most, pin 1 without function; 0.1 µF at its VDD |
| SN74LVC126A | quad buffer, 14 pins | 2 | the suit clock from the oscillator to both processors' OSC_IN and the five lines' clock drivers, one spare gate |
| THVD1451 | 8 pins, full duplex, no enables | 5 | a line's data: drives the pair to the blocks, receives the return pair |
| THVD1450 | SOIC-8, VSSOP-8 or VSON-8 | 6 | five drive the lines' clock, one talks to the BMS |
| LMR43610R3RPER | VQFN-HR, 2 × 2 mm | 8 | Mamka's own 3.3 V; 4 V for each of the five lines; 6 V for the suit; 5 V for the fan |
| SWPA252012S2R2MT | 2.5 × 2.0 mm | 12 | the π filters behind the six suit rails, two chokes side by side each |
| GZ2012D301TF | 2.0 × 1.25 mm | 12 | the beads behind them, two side by side each |
| EEHZA1H470P | SMD 8 × 10.2 mm | 2 | the bulk on the battery input: 47 µF 50 V hybrid polymer, the house part |
| female header, 2 × 20, extra tall | 2.54 mm grid, body 23 mm (Adafruit 1979) | 1 | onto Baťa's header, raising her ~25.5 mm over his board, over his SoC's heatsink (see [construction](CONSTRUCTION.md#the-stack)) |
| IDC box header, 2 × 5 | 2.54 mm grid | 6 | one per line, for its 3M 1785 flat cable: three pairs and the supply; one for Terem's flat cable |
| Noctua NF-A4x10 5V PWM | 40 × 40 × 10 mm | 1 | the backpack's fan: 4 wires, 5 V, 0.07 A, its own driver inside |
| 4-pin PC fan header | 2.54 mm grid | 1 | the fan's +5 V, ground, PWM in and speed out |
| fuse, 5 × 20 mm, and its holder | Schurter OGN-SMD with the 0853 cover | 1 | on the battery input, before everything on the board: fast-acting, ceramic, sand-filled, as the pack's; its value from the measured starts (see [Babuška](../babuska/HARDWARE.md#power-variants)) |
| TPS26630 | VQFN-24, 4 × 4 mm | 1–2 | the eFuse for each ROCK 5T, Baťa's and Deduška's if he is fitted: the battery to its DC jack, a current limit, a soft start, under- and overvoltage cutoffs, SHDN and PGOOD (SLVSE94G) |
| DC cable with a 5.5 × 2.1 mm plug | | 1–2 | from each eFuse to its ROCK's jack |

The STM32H562 (datasheet DS14258) in LQFP64 has 49 I/Os (53 is VFQFPN68's), 4 SPIs, 5 USARTs, 5
UARTs and 2 SAIs (table 2), up to four I2Cs with Fast-mode Plus (1 Mbit/s), 640 KB of RAM, and two
GPDMA controllers of eight channels each (section 3.16). Its USART reaches 20 Mbaud. The STM32H523,
the modules' part, has 4 USARTs, 2 UARTs and 4 SPIs, three with I2S, in LQFP64 (DS14540), and 272 KB
of RAM. It might do for processor 2, its I2S in an SPI as on Nataša, but processor 1 needs the
larger memory (see [memory](SOFTWARE.md#memory)); both stay STM32H562 (see [open
questions](#open-questions)).

**Processor 1's pins**

| what | pins | where |
|---|---|---|
| the suit clock in | 1 | PH0-OSC_IN, the HSE in bypass, from the clock buffer |
| the four body lines' clock drivers: DE | 4 | PA8, PC8, PC9, PB12, a line each in the order above, outputs |
| four body lines: to the blocks and from them | 8 | TX and RX at 19.66 Mbaud, AF7: USART2 on PA2 and PA3, USART3 on PB10 and PC4, USART6 on PC6 and PC7, USART1 on PB6 and PB7 |
| two SPIs to Baťa, as the slave | 8 | NSS, SCK, MISO, MOSI: the first SPI1 on PA4–PA7 (AF5), the second SPI3 on PA15, PC10, PC11, PC12 (AF6) |
| "data ready" to Baťa | 1 | PB1 |
| the UART to Baťa | 2 | UART4: TX on PA0, RX on PA1 (AF8) |
| Baťa's 3.3 V from header pin 1 | 1 | PC0, read as "Baťa is up" |
| SWD | 2 | PA13 SWDIO, PA14 SWCLK |
| status LED | 1 | PB0 |
| **total** | **28** | 21 I/Os free |

**Processor 2's pins**

| what | pins | where |
|---|---|---|
| its clock in | 1 | PH0-OSC_IN in bypass, from the clock buffer (DS14258, 5.3.8: 4–50 MHz) |
| the head line's clock driver: DE | 1 | PB12, an output |
| the head line: to Nataša and from her | 2 | USART3 at 19.66 Mbaud: TX on PC10, RX on PC11 (AF7) |
| the SAI to Baťa, as the I2S master | 4 | SAI1 (AF6): SCK_A on PC6, FS_A on PC5, SD_A on PC1, SD_B on PA3; block A the master and transmitting, SD_A to header pin 38 (I2S2_SDI_M1); block B synchronous to it and receiving, SD_B from pin 40 (I2S2_SDO_M1) (the ROCK 5T schematic V1.2, CON1) |
| the control channel to Baťa: I2C as the slave | 2 | I2C1 (AF4): SCL on PB6, SDA on PB7, both Fm+ pins (FT_f, FT_fa) |
| "a message waiting" to Baťa | 1 | PC4 |
| the BMS | 3 | UART5 at 9,600 Bd (AF8): TX on PC12, RX on PD2, DE on PC8 |
| EN and PGOOD: the first and the last of the 4 V chain, the 6 V, the computers' eFuses | 8 | the 4 V chain: EN PA4, PGOOD PA5; the 6 V: EN PA6, PGOOD PA7; Baťa's eFuse: SHDN PB1, PGOOD PB2; Deduška's: SHDN PC2, PGOOD PC3; the fan's 5 V follows Baťa's SHDN |
| Budilnik: HOLD to Mamka's own 3.3 V converter's EN | 1 | PB5, through a diode (see [Budilnik](#budilnik)) |
| Baťa's 3.3 V from header pin 1 | 1 | PC0, read as "Baťa is up" |
| the start button | 1 | PA2, a wake-up pin (WKUP2), through a divider from the button's node |
| the GPS, if fitted: UART and PPS | 0–3 | UART4: TX on PA0, RX on PA1 (AF8); the PPS on PA15 into TIM2_CH1 (AF1), a 32-bit timer |
| the backpack's fan | 2 | the PWM at 25 kHz on PB8, TIM4_CH3 (AF2), open-drain on a 5 V-tolerant pin (FT); the speed on PB4 into TIM3_CH1 (AF2), pulled up to 3.3 V |
| SWD | 2 | PA13 SWDIO, PA14 SWCLK |
| status LED | 1 | PB0 |
| **total** | **30–33** | 19 I/Os free, 16 with the GPS |

- The pins come from DS14258's pinout (figure 5) and alternate functions (tables 15 and 16); PC2
  and PC3 are LQFP64's pins 10 and 11, plain I/Os here.
- **Not SPI2 on PB13 and PB14:** with MISO on PB14 a slave transmits at 6 MHz at most, and with
  SCK on PB13 a master at 3 MHz (table 115, notes 2 and 3). SPI1 and SPI3 transmit at up to
  43 MHz as a slave at 2.7–3.6 V, above the ROCK 5T's 37.5 MHz, and take 4- to 32-bit frames
  (table 10).
- PC13 to PC15 hang on the backup domain's power switch: 2 MHz and 30 pF at most, and no
  current to source (table 14, note 3). They stay free on both.
- PA4 and PA5 are TT pins, which take at most VDD + 0.3 V (table 20), so the pull-up on the
  4 V chain's PGOOD at PA5 goes to Mamka's 3.3 V, not to the 4 V rail.
- PB8 drives the fan's PWM at 5 V, and above 4 V its internal pull-up and pull-down must stay
  off (table 17, note 6).

The DMA channels are laid out under [software](SOFTWARE.md#dma). Both processors keep BOOT0 pulled
low on the board; nothing on the header resets them (see [firmware](SOFTWARE.md#firmware)).

## On Baťa's header

Mamka sits on the 40-pin header of the ROCK 5T, an extra-tall female header on her underside, as one
board over the whole computer and his SoC's heatsink, short of the band of his ports (see
[construction](CONSTRUCTION.md#the-stack)). From the header she takes only the data pins, the eight
grounds and pin 1 as a signal: no 5 V and no 3.3 V, since she feeds herself.

| header pins | Radxa ROCK 5T | to Mamka |
|---|---|---|
| 19, 21, 23, 24 | SPI0_M2 with chip select 0 | processor 1: the first SPI |
| 7 | SPI1_M1's chip select 1 | processor 1: the second SPI's chip select |
| 11, 13, 15 | SPI1_M1: SCLK, MOSI, MISO | processor 1: the second SPI, through 33 Ω |
| 12, 35, 38, 40 | I2S2_M1 | processor 2: the SAI |
| 36 | GPIO3_B1, an input | processor 1: "data ready" |
| 3, 5 | I2C7_M3, with the board's audio codec off | processor 2: the control channel |
| 37 | GPIO1_A7, an input | processor 2: "a message waiting" |
| 8, 10 | UART2_M0, its debug console | processor 1: the UART |
| 1 | its 3.3 V | both processors: read as "Baťa is up" |
| 6, 9, 14, 20, 25, 30, 34, 39 | ground | ground |
| 2, 4 | its own 5 V | not taken |
| 17 | its 3.3 V, as on pin 1 | not taken |
| 16, 32 | GPIO3_A4, GPIO3_C2 | EN of Umnica A and B to Terem's cable: traces only, the ROCK's PCIe driver drives them (see [Terem](../terem/HARDWARE.md#the-converters)) |
| 18, 33 | GPIO4_C4, GPIO3_A7 | PGOOD of Umnica A and B from Terem's cable: traces only, with 10 kΩ pull-ups from pin 1; no processor pin |
| 22, 26, 27, 28, 29, 31 | | free |

- **The 33 Ω** in the second SPI are the house rule for a line that leaves the board.
- **Pin 1:** Mamka runs from the battery and could feed a switched-off computer through the
  protection diodes of its pins. Until pin 1 shows Baťa's 3.3 V, both processors keep their lines
  to him quiet, and every pull-up on the header, pins 3 and 5 for the I2C and 18 and 33 for the
  PGOODs, hangs on pin 1, the computer's own 3.3 V, never on Mamka's, so it vanishes with him.
- The ROCK 5T's pins come from Radxa's table for its V1.2; the 5T Industrial V2.01 differs only
  on pins 27 and 28, which Mamka does not use. All its GPIOs are 3.3 V.
- Pin 22 is a 1.8 V ADC input on the ROCK 5T, so "data ready" takes pin 36.
- The ROCK 5T's SPIs take the even dividers of a 200, 150 or 24 MHz source: 37.5 MHz is the
  fastest under the STM32H562's 43 MHz as a slave (see
  [Porjadok](../porjadok/SOFTWARE.md#into-baťa)).

The control channel on pins 3 and 5 and the UART on pins 8 and 10 are described under
[software](SOFTWARE.md#the-control-channel): what travels on them, and the overlays the ROCK needs
for them.

## Lines

Five lines leave Mamka: four for the suit, each with two to four basic blocks, and one for the
head, with [Nataša](../natasa/HARDWARE.md#the-head-line) and Míša behind her. They
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
  | 7, 8 | +4 V and its ground |
  | 9, 10 | +6 V and its ground |

The 4 V and the 6 V come from Mamka's own converters (see [Converters](#converters)). Five 2 × 5 box
headers, ~20 mm each, stand on her top face along the header's side, and Terem's beside them (see
[construction](CONSTRUCTION.md#the-stack)). Inside the backpack a short harness, ~10–20 cm (see
[Porjadok](../porjadok/HARDWARE.md#end-to-end)), joins them to the PT 24-61 in the shell, the one
connector of the whole suit (see [Babuška](../babuska/CONSTRUCTION.md#the-backpack)). The harness
carries a header's ten wires; the suit's 3M 1785/16, with its doubled supplies and six grounds,
begins at the PT 24-61 (see [Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit)).

## Clock

The suit's clock is *Chodiki*, Russian for the wall clock with weights that the whole household
lives by.

The board gives the clock, and the clocks of the other parts are derived from it; the cycle the
blocks keep themselves (see [Porjadok](../porjadok/SOFTWARE.md#the-channel-from-the-master)). The
clock travels over its own one-way RS-485 channel alongside the data bus, through buffers and
five drivers, one per line.

The base is **9.8304 MHz**, from a SiTime SiT8008 MEMS oscillator into two SN74LVC126A buffers, and
from them to everything: both processors' HSE in bypass and the five lines. No processor makes or
passes on the clock, so a processor's reset stops nothing. It is the family of 120: the IMUs' steps
come at 120 Hz, the rate screens run at, so every snapshot on the output is a measured one. Every
rate in the suit is the base multiplied or divided by a whole number, apart from the sound's 48 kHz.

- The PLL makes the lines' 196.608 MHz from it: straight in (÷ 1), × 40 to a 393.216 MHz VCO,
  ÷ 2. The input and the VCO lie in the PLL's wide range of 2–16 MHz and 128–560 MHz, and
  196.608 MHz stays within VOS1's 200 MHz (DS14258, tables 48 and 21). The blocks' STM32H523 has
  the same ranges (DS14540, tables 46 and 20).
- The buffers' eight gates: two to the processors' OSC_IN, five with 33 Ω in series to each line's
  THVD1450, their seven OE tied on, and one spare with its OE on ground. One short trace takes the
  oscillator to both buffers' inputs.
- **A line's clock goes out when its driver's DE is raised,** by the processor that runs the
  line: processor 1 for the four body lines, processor 2 for the head line. Until then the
  units on it see a quiet pair, their receivers hold the clock input high (fail-safe, SLLSEY3E),
  and they stay on their HSI (see [Porjadok](../porjadok/SOFTWARE.md#bring-up)).

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

The SAI's clock comes from processor 2's PLL1, the same as her system clock's: the suit clock
straight in (÷ 1), × 40 = a 393.216 MHz VCO, Q ÷ 32 = 12.288 MHz, exactly 256 × 48 kHz (see
[software](SOFTWARE.md#clocks)). The
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
| 2 × STM32H562, processor 1 at 197 MHz with every peripheral clocked, processor 2 slower | ~61 mA typical, ~82 mA at 85 °C each at 200 MHz in VOS1 (DS14258, table 28); on silicon A or Z in VOS0 ~70 and ~102 mA (see [software](SOFTWARE.md#firmware)) |
| 5 × THVD1451, each driver always on, into two 120 Ω (~60 Ω) | ~37 mA each |
| 5 × THVD1450 driving the clock, the same load, once its DE is up | ~37 mA each |
| the receivers, the buffers, the LED | a few mA |
| **total** | **~0.5–0.6 A of the 1 A** |

- Every branch sits behind the house π filter, and the processor's branch has the bead too
  (see [Rubaška](../rubaska/HARDWARE.md#power)).
- **The fan's 5 V:** one more LMR43610 with the divider 48.7 kΩ over 12.1 kΩ, 5.02 V, for the
  fan's 0.07 A. Its EN follows Baťa's SHDN: the fan runs while he does.
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
  processor 2 raises the lines' converters and the 6 V in order, and the computers' eFuses, and
  the suit comes up.
- **Stopping:** Baťa asks for it (message 0x12), or the button is held for five seconds.
  Processor 2 tells the computers to halt, drops their SHDN once Baťa's pin 1 has fallen, or
  Deduška has answered, or after a timeout, drops the lines and the 6 V, and lets HOLD fall:
  the 3.3 V converter stops and Mamka is off, processor 2 with her. What stays on the battery
  then is the BMS, the eFuses in their 21 µA sleep and Terem's converters with EN low at
  0.25 µA: tens of microamps.
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

- **The cell,** the house buck cell:

  | position | value |
  |---|---|
  | inductor | 4.7 µH, shielded, saturation 2.1 A or more, the LMR43610's highest peak current limit |
  | divider on VOUT/FB, against 1.00 V | bottom 12.1 kΩ; top 36.5 kΩ → 4.02 V, 60.4 kΩ → 5.99 V |
  | C_FF across the top resistor | 22 pF C0G |
  | C_IN | 4.7 µF 50 V X7R 1206 + 100 nF |
  | C_OUT | 3 × 10 µF 50 V 1206 + 100 nF |
  | VCC · BOOT | 1 µF · 100 nF |
- **At its highest frequency, with no clock.** With the RT pin on ground the converter runs at
  2.2 MHz with no resistor, no clock from the processor and no extra trace.
- **The inductor's ripple:** from 12 V to 4.02 V, ~0.26 A, about a quarter of the 1 A, inside the
  20–40% the datasheet asks for.
- **A converter for each line on 4 V, one for the whole suit on 6 V.** Five make 4 V, one
  for each of the four suit lines and one for the head line; one makes 6 V:

  | rail | load | capacitance it charges at start | start |
  |---|---|---|---|
  | 4 V, a suit line | ~0.27 A on average, ~0.42 A at worst, ~0.54 A with a glove | ~650 µF: four modules' 6TPE100M with their ceramics, the π filter, C_OUT | within the 3.5 ms soft start; at its fastest, 2 ms, briefly at the current limit, done in ~3.0 ms |
  | 4 V, the head line | ~0.35 A on average, ~1.0 A for a millisecond when the radar chirps while two motors run | ~900 µF, Nataša's two polymers and Míša's among them | the same |
  | 6 V, the whole suit | ~0.13 A, ~8 mA a module | ~1.4 mF: sixteen modules' 10TPE47MAZB with their ceramics | at the current limit, ~7–8 ms |

- **At the current limit** the converter holds the inductor's current between its high-side peak
  and low-side valley limits, cycle by cycle, and delivers about their average: at least
  ~1.13 A, from 1.4 A and 0.85 A at their minimum (SNVSBY5B, 7.5 and 8.3.9). It does not shut
  down; the current stays there even with the output at zero. A large capacitance so only
  charges more slowly.
- **TI's limit:** the output capacitance should stay under about ten times the design value or
  1000 µF, or else the start at full load and the loop's stability are to be studied (9.2.2.4).
  The 4 V lines stay under 1000 µF. The 6 V's ~1.4 mF is to be checked by simulation and
  measurement; should it fail, 6 V splits into two converters for two lines each, ~700 µF.
- **The lines come up one after another:** each 4 V converter's PGOOD drives the next one's
  EN, so processor 2 needs only the first EN and the last PGOOD, and the battery takes one
  line's inrush at a time.
- **Each line on its own:** a short or a faulty module takes down only its own line.
- **The battery input** at Mamka's terminals carries the house input bank, doubled: two 47 µF
  50 V hybrid polymers, Panasonic **EEHZA1H470P** (ZA series, SMD 8 × 10.2 mm, 30 mΩ, 1.8 A of
  ripple at 100 kHz, 105 °C / 10,000 h), with 10 µF 50 V 1206 and 100 nF. The bulk holds the
  input up at the end of the cable from the battery; each converter keeps its own C_IN by its
  pins. The 50 V stays although the pack gives at most 16 V: a battery plugged into a board
  rings on the cable's inductance above its own voltage, and the hybrid's ESR damps that.

## Filtering

The ripple of the converters is filtered away on its way to the chips, by a chain of cheap
parts:

1. **On Mamka,** right behind each converter: a π filter with the modules' parts, two chokes
SWPA252012S2R2MT side by side (2.2 µH, 0.17 Ω and 1.85 A each, so 1.1 µH and 0.085 Ω) with 10 µF +
100 nF on both sides, then two ferrite beads GZ2012D301TF side by side (300 Ω at 100 MHz, at most
0.2 Ω and 500 mA each). At a suit line's worst 0.42 A the pair drops ~0.08 V, ~0.10 V at 0.54 A with
a glove. No polymer sits at the board's outputs: the lines' bulks sit at the modules, and one here
would only add to what the converter charges at start. The converters sit on one side of the board
with copper poured under them, away from the clock and the processor. 2. **The cable:** every supply
wire runs twisted with a ground wire as a pair, so plus and minus lie against each other. Mamka is
some tens of centimetres from the modules. 3. **On the module:** capacitors at the input, the LDO,
and behind it a π filter with a choke whose self-resonance lies at 69 MHz (see
[Rubaška](../rubaska/HARDWARE.md#power)). The digital branch has the same. 4. **Inside the
ADS1299:** its own supply circuits behind AVDD.

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

The ROCK 5T takes 9–20 V on its DC jack, and Radxa recommends 12 V; its USB-C does not power it
(Radxa's FAQ). The pack gives ~11.5–15.6 V between 20 and 80% (an estimate until the cell is
measured, see [Babuška](../babuska/HARDWARE.md#the-battery)), 16 V at most, so each ROCK runs
straight from the battery, with no converter, through an eFuse on Mamka: one for Baťa, and a
second for Deduška if he is fitted. Mamka drives each eFuse's SHDN and reads its PGOOD, so she
switches the computers on after the start button and off once they have shut down (see
[Budilnik](#budilnik)). The Umnicas have their own converters on [Terem](../terem/README.md),
which takes the battery from Mamka, behind her fuse, on a cable of its own; a suit without them
has no Terem. The battery comes to Mamka alone: pack → fuse → BMS → 2.5 mm² cable → Mamka's
fuse → the eFuses, Terem's cable and Mamka's own converters.

- **TI TPS26630** (SLVSE94G): 4.5–60 V, up to 6 A through its own 31 mΩ FET, the current limit
  set by a resistor, the output's rise by a capacitor, an undervoltage and an overvoltage cutoff
  set by a divider, a shutdown pin and PGOOD. The protection chain of the suit is then the
  pack's fuse, the BMS, Mamka's fuse, and in every branch its own limit: Mamka's converters
  have theirs, Terem a chip fuse at its input and its converters' limits, and each ROCK, which
  has no converter and no fuse of its own (the schematic V1.2 has a bead and a TVS at its jack),
  gets its eFuse.
- **Its values:** R(ILIM) 6.04 kΩ for a limit of ~3 A (the sheet's table runs 30 kΩ for 0.6 A
  to 3 kΩ for 6 A, ~18 kΩ·A); C(dVdT) 22 nF for an output ramp of ~5–7 ms over 11.5–16 V
  (t = 20.8 × 10³ × V(IN) × C, equation 2), so the ROCK's input capacitors charge gently and the
  cable does not ring; the divider from IN_SYS, 866 kΩ, 75 kΩ and 66.5 kΩ to ground, puts the
  undervoltage cutoff at ~8.5 V and the overvoltage cutoff at ~18 V against the 1.2 V
  thresholds of UVLO and OVP (equations 9 and 10). The divider is a must: with UVLO at ground
  the part's own default of 15.5 V would never let the battery through. MODE open: a fault
  latches off, and processor 2 clears it by cycling SHDN.
- **SHDN and PGOOD:** Baťa's on PB1 and PB2, Deduška's on PC2 and PC3. SHDN is driven (the eFuse
  sleeps at ~21 µA with it low); PGOOD is an open drain pulled up to Mamka's 3.3 V. FLT is not
  wired: a ROCK that does not come up shows on PGOOD, and Baťa on header pin 1 too.
- **Its loss** at 3 A is ~0.3 W in the 31 mΩ; the ROCK's 17 W at 11.5 V is 1.5 A, ~0.07 W.
- Under 9 V, 2.25 V a cell, the ROCK 5T would go out; the suit shuts down at 20% long before,
  and the eFuse's 8.5 V is only the backstop.
- **The DC cable:** from the eFuse's OUT, with 10 µF and 100 nF at the pads, to the ROCK's jack,
  Baťa's ~10 cm across the stack, Deduška's as long as the backpack needs. The plug is
  **5.5 × 2.1 mm**: the schematic V1.2 names the jack a DC091-5521, and its centre pin in
  Radxa's 3D model V1.2 is a cylinder of 2.000 mm. Radxa's product brief (rev. 1.4) says
  "5525", 5.5 × 2.5 mm, which a later board may have; a 2.5 mm plug on a 2.0 mm pin makes a
  poor contact, so the pin is measured on the board bought.
- **Terem's cable** has ten wires, six of them grounds; the Umnicas' EN and PGOOD only cross
  Mamka as traces to the header, where the ROCK's PCIe driver drives the ENs and the ROCK reads
  the PGOODs (see [Terem](../terem/HARDWARE.md#the-converters)).

## Open questions

- both processors' pins checked against DS14258's pin and alternate-function tables (9 Oct 2026):
  every signal on its pin at the AF given, all on LQFP64, no pin or peripheral twice, PA4 and PA5
  TT, PB8 FT, WKUP2 on PA2; the clock tree (see [software](SOFTWARE.md#clocks)) and the DMA table,
  12 and 9 of 16 channels (see [software](SOFTWARE.md#dma)), to check on the first board; whether
  the STM32H523 does for processor 2 is settled for now: it would (no SAI, the sound through an SPI
  in I2S mode, 9 DMA channels), but both stay STM32H562, one part and one firmware base,
- the TPS26630's current limit against the ROCK 5T's real peaks with the glasses on its USB-C,
  measured; the jack's pin, 2.0 mm by the model, checked with a calliper on the board,
- the converters' ripple in the ADS1299 data: confirm by measurement,
- the 6 V converter's start into ~1.4 mF and its loop's stability: simulation and measurement;
  SNVSBY5B lists a hiccup time (tHICCUP, 30–75 ms) that its section 8.3.9 does not describe, so
  when the part hiccups, and whether a long start at the current limit triggers it, is to be
  found out first,
- no other helper function is planned; the clock, the sound bridge, Budilnik and the GPS are
  all the board carries.

