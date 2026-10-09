<div align="center">

# Rubaška: hardware

**The sensing module's board,** the IMU, the right-leg drive, the power, and the Vnučata of the
glove and the foot.

↑ [Rubaška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## Sensing module

The sensing module is the suit's basic block; a suit has 8 to 16 of them. Together they are the
*Rebjata*, Russian for the kids: Mamka's own children, on the end of her
[Pupovina](../porjadok/HARDWARE.md#links-between-boards). A module is one board
in its piece, as small as it can be: fewer and smaller parts, fewer pads, smaller connectors.
Its IMUs sit along the bones, each on a small board of its own, joined to the module by I3C,
two IMUs to a bus. No SPI runs over a cable anywhere.

| part | package | role |
|---|---|---|
| STM32H523CCU6 | UFQFPN48, 7 × 7 mm | the module's processor: 256 KB of flash, 272 KB of RAM; see [Porjadok](../porjadok/README.md) |
| ADS1299 | TQFP-64, 10 × 10 mm | 8 biopotential channels, 24-bit, on 16 electrodes |
| ICM-42688-P, 2–4 | LGA-14, 2.5 × 3 × 0.91 mm, on its own small board | IMU: motion and orientation of the piece |
| TPS7A4700 | VQFN-20, 5 × 5 mm | 6 → 5 V for the ADS1299 analog side, see [power](#power) |
| TPS7A2033 | X2SON 1 × 1 mm, or SOT-23-5 | 3.7 → 3.3 V for the rest |
| THVD1452, 2 | VSSOP-10, or SOIC-14 | the data pairs of the line |
| THVD1450 | VSON-8 or VSSOP-8, or SOIC-8 | the clock pair, receive only |

The smallest packages of a part come first. Leadless packages (QFN, X2SON, VSON) need machine
assembly, which the boards get anyway.

The blocks sit on four lines, two to four on each. They are joined by a full-duplex (four-wire)
RS-485 bus
with time-division multiple access (TDMA), with a one-way RS-485 channel for the clock alongside
it; see [Porjadok](../porjadok/HARDWARE.md#links-between-boards).

**Layout.** The board is long and narrow, in this order:

1. the line connector, with the RS-422/485 drivers right by it,
2. the processor, as close to them as it can be,
3. a gap,
4. the ADS1299 with its input circuit, and the electrode connector.

Digital and analog parts so stay apart; the ADS1299 datasheet asks that return currents of the
digital parts never cross the analog return path (SBAS499C, section 11).

**The processor's pins.** The STM32H523 in UFQFPN48 has 35 I/Os, four SPIs (three of them also
I2S), three USARTs, two UARTs and two I3C controllers (DS14540, table 2). The module needs 22,
or 23 with a glove or a foot on it:

| what | pins |
|---|---|
| ADS1299: SPI (SCLK, DIN, DOUT, CS), DRDY, START, RESET, CLK | 8 |
| IMUs: two I3C buses (SCL and SDA each) and CLKIN | 5 |
| the forearm's and the calf's modules: Interconnect to the glove or the foot | 0–1 |
| the line: receive from the master, transmit, DE, the echo | 4 |
| the suit clock in | 1 |
| SWD (SWDIO, SWCLK, SWO) and a status LED | 4 |
| **total** | **22–23** |

They land on the pins as below, from DS14540's pinout (figure 6) and its alternate functions
(tables 14 and 15). The sides of the package fall by job: the bottom is the ADS1299's, the
right the line's, the top the IMUs'.

| pin | name | use | AF |
|---|---|---|---|
| 1 | VBAT | to VDD | |
| 2–4 | PC13–PC15 | free | |
| 5 | PH0-OSC_IN | the suit clock, 9.8304 MHz, into the HSE in bypass | |
| 6 | PH1-OSC_OUT | free | |
| 7 | NRST | to the SWD connector | |
| 8, 9 | VSSA, VDDA | | |
| 10, 11 | PA0, PA1 | free | |
| 12 | PA2 | Interconnect, on the forearm's and the calf's modules: USART2_TX, half-duplex | AF7 |
| 13 | PA3 | ADS1299 RESET | GPIO |
| 14 | PA4 | ADS1299 CS: SPI1_NSS | AF5 |
| 15 | PA5 | ADS1299 SCLK: SPI1_SCK | AF5 |
| 16 | PA6 | ADS1299 DOUT: SPI1_MISO | AF5 |
| 17 | PA7 | ADS1299 DIN: SPI1_MOSI | AF5 |
| 18 | PB0 | ADS1299 CLK: TIM3_CH3 | AF2 |
| 19 | PB1 | ADS1299 START: TIM3_CH4 | AF2 |
| 20 | PB2 | ADS1299 DRDY, on EXTI2 | GPIO |
| 21 | PB10 | free | |
| 22 | VCAP | 2.2 µF | |
| 23, 24 | VSS, VDD | | |
| 25 | PB12 | the status LED | GPIO |
| 26–28 | PB13–PB15 | free | |
| 29 | PA8 | the IMUs' CLKIN: TIM1_CH1 | AF1 |
| 30 | PA9 | the line, transmit: USART1_TX | AF7 |
| 31 | PA10 | the echo: USART1_RX | AF7 |
| 32 | PA11 | the line, receive from the master: UART4_RX | AF6 |
| 33 | PA12 | the line, the driver's DE: USART1_DE | AF7 |
| 34 | PA13 | SWDIO | AF0 |
| 35, 36 | VSS, VDD | | |
| 37 | PA14 | SWCLK | AF0 |
| 38 | PA15 | free | |
| 39 | PB3 | SWO | AF0 |
| 40 | PB4 | I3C2_SDA | AF10 |
| 41 | PB5 | I3C2_SCL | AF10 |
| 42 | PB6 | I3C1_SCL | AF3 |
| 43 | PB7 | I3C1_SDA | AF3 |
| 44 | BOOT0 | to ground through 10 kΩ | |
| 45 | PB8 | free | |
| 46 | VCAP | 2.2 µF | |
| 47, 48 | VSS, VDD | | |
| pad | the exposed pad | to ground (section 6.5, note 3) | |

- SWO can only go on PB3, which is also I3C2's SCL; its other SCL is PA8, which CLKIN takes,
  so I3C2 takes PB5 and PB4.
- TIM3 gives the ADS1299 both its CLK and its START, so START keeps a fixed place against the
  CLK edges.
- The line transmits on USART1, its DE driven by the USART itself, and reads itself back on
  USART1's RX: the echo. It receives from the master on UART4. Both reach 20 Mbaud with DMA
  (section 3.35.1).
- SPI1 takes frames of 4 to 32 bits, so one reading of the ADS1299, 216 bits, comes as nine frames
  of 24 bits: the status word and the eight channels, each into a 32-bit word of its own (see the
  frame in [Porjadok](../porjadok/SOFTWARE.md#the-frame)). SPI4 would stop at 16 bits
  (table 10).
- The HSE in bypass takes a digital clock of 4 to 50 MHz (table 38).
- PC13 to PC15 hang on the backup domain's power switch: 2 MHz and 30 pF at most, and no
  current to source, so not for the LED (table 13, note 2).
- Each VCAP takes 2.2 µF with an ESR under 100 mΩ (table 21).
- Twelve I/Os stay free.
- The ADS1299's PWDN and CLKSEL pins are not driven: they are tied through resistors of
  10 kΩ or more, as the datasheet asks for its mode pins, PWDN high and CLKSEL low for the
  external clock.
- The ADS1299's unused pins, as its section 10.1.1 asks: GPIO1–4 and DAISY_IN to DGND, SRB1 and
  SRB2 to AVSS, BIASREF left open (the mid-supply is made inside, see
  [software](SOFTWARE.md#the-ads1299s-settings)); BIASIN is tied to BIASOUT (see
  [Right-leg drive](#right-leg-drive)).

**The IMUs on I3C**

- **Two IMUs to a bus**, on the processor's two I3C controllers. An ICM-42688-P has the static
  address 0x68 or 0x69, set by its AP_AD0 pin (DS-000347). If it takes SETDASA, the controller
  turns that into its I3C address; the datasheet does not list it. If it does not, the
  controller talks to both as I2C at their static addresses, which the STM32H5's I3C does too
  (legacy I2C messages, AN5879). Two to a bus either way: more would need the chips'
  provisioned IDs to differ, and nothing promises that.
- **The cable** of a bus has five wires: SCL, SDA, +3.3 V, ground and CLKIN. The data are
  small, 12 B per IMU 1,200 times a second, 29 kB/s a bus, so the bus can run well below the
  12.5 MHz of I3C SDR, which helps over a cable.
- **The IMU clock** comes on the CLKIN wire. I3C has a clock over the bus too (synchronous
  timing control, SETXTIME), and ST's documents disagree on whether the STM32H5's controller
  has it: AN5879 Rev 6, table 3, says no, DS14540 Rev 3, table 8, and RM0481 Rev 5, table 598,
  say yes. It makes no difference: the ICM-42688-P documents its rates only from CLKIN
  (DS-000347, 12.5), not from I3C timing, so the wire stays.
- **I3C2 has no Fm+:** PB4 and PB5 are FT_h pins, and only FT_f pins drive Fm+ (DS14540,
  5.3.32). Should the IMUs fall back to I2C, I3C2's bus runs at 400 kHz; I3C1 on PB6 and PB7
  (FT_f, FT_fa) could run 1 MHz. At 400 kHz two IMUs at 1,200 Hz would take ~80% of the bus,
  so as I2C the IMUs run the chip's own 120 Hz (see [software](SOFTWARE.md#the-imus-settings)).

**Clocks.** The suit clock, 9.8304 MHz, comes in through the THVD1450 and feeds the processor,
whose one PLL makes the 196.608 MHz the line and the timers run on, and the SPI's clock from a
second output (see [Porjadok](../porjadok/SOFTWARE.md#timing-of-one-cycle)). Timers give the
ADS1299 its CLK, the suit clock ÷ 5 = 1.96608 MHz, the IMUs their CLKIN, ÷ 256 = 38,400 Hz,
and take START high at the start of a measurement; see
[Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement).

**Inputs and their protection.** The inputs keep the classic circuit from the datasheet, a
series resistor and capacitors before each input, with the values recalculated for EMG:

- At 4,000 SPS the ADS1299 passes up to 1,048 Hz (−3 dB, datasheet table 1); at the suit's
  3,840 SPS ~1,006 Hz. Its modulator samples at fCLK / 2, 983 kHz from the suit's 1.96608 MHz.
- The datasheet's example, 4.99 kΩ and 4.7 nF, is made for EEG. For EMG: 4.99 kΩ in each lead
  and **220 pF C0G** across the pair. The electrode's contact adds to the resistors, so the
  corner depends on it, 1 / (2π · 2 · (R_contact + 4.99 kΩ) · 220 pF):

  | contact per electrode | corner | at the modulator's 983 kHz |
  |---|---|---|
  | ~0 (on the bench) | 72 kHz | ~23 dB down |
  | 20 kΩ | 14.5 kHz | ~37 dB down |
  | 50 kΩ, the working figure | 6.6 kHz | ~43 dB down |
  | 100 kΩ | 3.4 kHz | ~49 dB down |

  The signal band, up to ~500 Hz, passes in every case. A larger capacitor would bring the
  corner of a moist contact down into the band, and electrodes with different contacts would
  then turn the common-mode voltage into a difference.
- The datasheet asks for C0G in the differential input capacitors (section 12.1), and the same
  vibration argument as for VCAP1 makes the bias loop's 1.5 nF C0G too.
- The lead-off current through the resistor is negligible: 6 nA × 5 kΩ = 30 µV.
- **Protection** rests on the right-leg drive. It is the only wire that joins the body to the
  suit at low impedance, so it drains static from the body and holds it at mid-supply. The
  series resistors limit the current into the ADS1299's own input diodes. The bias runs
  through an input too, so its protection resistor is that input's 4.99 kΩ (see
  [Right-leg drive](#right-leg-drive)).

**Connectors and size.** The line arrives as a 3M 1785 flat cable in a 2 × 5 IDC socket (see
[Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit)). The electrode connector
carries 16 leads, so the module unplugs before the harness is rinsed: a 2 × 8 IDC socket for the
3M 3517 flat cable, ~25–28 mm long, to be checked on the part (see
[electrodes](CONSTRUCTION.md#electrodes)). Each IMU bus needs 4 or 5 positions.

## The IMU

The IMU is the **TDK InvenSense ICM-42688-P** (±16 g, ±2000 °/s, 2 KB FIFO, SPI, I2C and I3C),
the same as in NIC-Heimdall's Quake. It won on its noise and its clock input, and the suit's
clock gives it exactly 1,200 Hz, and 120 Hz for the steps:

- **Low noise,** so it holds still when the body does: the gyro 2.8 mdps/√Hz, the
  accelerometer 65–70 µg/√Hz, and a gyro offset that drifts ±5 mdps/°C, the least in its
  family (TDK's table in DS-000639). The ICM-45686 has 3.8 mdps/√Hz and 80 µg/√Hz (DS-000577).
- **A CLKIN input,** 31–50 kHz, so it samples from the suit's clock.
- **1,200 Hz to 120 Hz.** CLKIN scales the ODR by f_CLKIN / 32 kHz (DS-000347, section 12.5),
  so 38,400 Hz turns the 1 kHz setting into exactly 1,200 Hz, ten samples to a step of 32 ADS
  samples, and the 100 Hz setting into 120 Hz, with nothing to divide in the processor. The
  block sums the ten into the step's turn and mean force (see
  [software](SOFTWARE.md#the-imus-settings)); in noise that equals the chip's own filtering to
  120 Hz, and it keeps the turn right in fast swings. The ICM-45686 would get there too, if its
  rates scale the same way; its CLKIN takes 20–40 kHz (DS-000577, section 4.14). The noise
  decides.

Its ±2000 °/s can be exceeded in a violent swing or throw; ordinary movement stays well within
it. The Bosch BMI570 has lower noise on paper, but we found no external clock input on it.
DS-000347 works its own example through, 500 × 32.768 / 32 = 512 Hz; ours is
1,000 × 38.4 / 32 = 1,200 Hz, and 100 × 38.4 / 32 = 120 Hz for the fallback.

[Mamka](../mamka/README.md) describes the clocks for both the ADS1299 and the IMUs.

CLKIN comes in on pin 9, INT2/FSYNC/CLKIN, switched by `PIN9_FUNCTION` = 10 in `INTF_CONFIG5`
(bank 1, 0x7B) and `RTC_MODE` in `INTF_CONFIG1` (bank 0, 0x4D); INT1 stays for interrupts. The
clock wants a high time of at least 1 µs and edges of 5 to 500 ns (DS-000347, table 8), so the
series resistors on long CLKIN wires must not slow it past that.

## Right-leg drive

The bias drive holds the body at the modules' mid-supply, so that the electrodes' common voltage
stays within the ADS1299's input range, and it drains static from the body (ADS1299 datasheet
SBAS499C, sections 9.3.2.4.5 and 10.1.3). Its amplifier senses the common voltage of chosen
channels (BIAS_SENSP, BIAS_SENSN) and drives the body inverted, towards (AVDD + AVSS) / 2 =
2.5 V.

- **One driver for the whole suit.** Only one module's amplifier runs; the others are powered
  down with PD_BIAS, as the datasheet asks when there are several devices. Its figure 39 also
  joins the summing nodes (BIASINV) of all devices with a wire. That is left out: a
  high-impedance node on a metre of cable would pick up the mains. The body is one conductor
  and the mains couples to all of it alike, so one module's channels sense its common voltage
  well enough.
- **Every module can be the one.** Each carries 1 MΩ ∥ 1.5 nF between BIASINV and BIASOUT (the
  datasheet's figures 33 and 68) and BIASOUT tied to BIASIN. Baťa picks the driving
  module from the pieces being worn: best over bone with little muscle under it, at the ankle
  of a trouser leg for instance, hence the right leg.
- **Through channel 8, with no lead of its own.** The multiplexer routes BIASIN to an input pin:
  IN8N becomes the bias electrode (MUX = BIAS_DRN) and IN8P is held as its spare (BIAS_DRP).
  That input's 4.99 kΩ is the protection resistor in the bias path, and the electrode connector
  keeps its 16 positions. On the other modules channel 8 measures as usual. These are the two
  electrodes of the whole suit that go to the right leg.
- **Sensing:** the driving module sums its channels 1 to 7 (BIAS_SENSP = BIAS_SENSN = 0x7F).
- **Checks:** before the bias starts, the ordinary lead-off check on channel 8 tells whether its
  electrodes touch. While it runs, a lost bias shows as the common voltage drifting off and the
  channels of the whole suit saturating; the computer then moves the bias to the spare
  electrode, or to another module.
- **Its limits:** the amplifier gives ~1.1 mA typical into a short and has 100 kHz of
  gain-bandwidth. The datasheet leaves the loop's stability to the system, so it is tuned on a
  sample.
- **The suit and the outside world:** a computer joins the suit only through an isolator or
  over the air (see [Baťa](../bata/SOFTWARE.md#output-modes)). The suit may be worn while it
  charges (see [Babuška](../babuska/HARDWARE.md#the-battery)).

## The glove and the foot

The glove is an add-on, like [Deduška](../bata/HARDWARE.md#deduška): the suit works without it.
What the glove and the foot send, and how, is under
[software](SOFTWARE.md#the-glove-and-the-foot); where their parts sit on the hand and the foot,
under [construction](CONSTRUCTION.md#the-glove-and-the-foot).

Its five small processors are the *Vnučata*, Russian for the grandchildren: they hang on one of
Mamka's children, the forearm's module, not on Mamka herself. Each is an **STM32H503KBU6** in
UFQFPN32, 5 × 5 mm, one per finger, with two I3C buses of two IMUs each: four IMUs a finger,
twenty a hand. The package has 26 I/Os, two I3Cs, three USARTs and three SPIs (DS14053 Rev 4,
table 2); the I3Cs share their pins with I2C1 and I2C2.

| bus | side of the finger | IMUs |
|---|---|---|
| I3C1 | outer | the distal and the middle phalanx |
| I3C2 | inner | the proximal phalanx, and the metacarpal on the back of the hand |

- **Interconnect** is one wire shared by the five Vnučata, into a third UART on the forearm's
  module. The USARTs run half-duplex: a TX pin lets go of the wire when it is not sending,
  open-drain with one pull-up of 1 kΩ to 3.3 V on the module, a value to try: with ~100 pF of
  wire and six pins it rises in ~100 ns, a fifth of the 500 ns bit at 2 MBd (see
  [software](SOFTWARE.md#the-glove-and-the-foot)). The distances are short, so there are no line
  drivers.
- **Across the wrist** go Interconnect, CLKIN, +3.7 V and ground. CLKIN is the module's own 38,400
  Hz (the suit clock ÷ 256 from a timer); on the glove a buffer of the 74LVC244 kind fans it out to
  the fingers' cables, a series resistor on each output. The Vnučata need no time base of their
  own: they run on their internal HSI, read their IMUs when these report data, sum them into
  steps as the module does, and hold the latest step until they are called.
- **3.3 V** on the glove, as on the modules, so the wire joins the module's pins directly.

**A Vnučka's pins,** from DS14053's pinout (figure 5) and alternate functions (tables 11 and 12).
Eight I/Os are used and 18 stay free:

| pin | name | use | AF |
|---|---|---|---|
| 1, 17 | VDD | 3.3 V | |
| 4 | NRST | to the SWD pads | |
| 5 | VDDA/VREF+ | 3.3 V | |
| 8 | PA2 | Interconnect: USART2_TX, half-duplex, the module's pin and AF | AF7 |
| 14 | PB0 | the status LED | GPIO |
| 16 | VCAP | 2.2 µF, ESR under 100 mΩ (table 18) | |
| 23 | PA13 | SWDIO | AF0 |
| 24 | PA14 | SWCLK | AF0 |
| 26 | PB3 | free; SWO if wanted | AF0 |
| 27 | PB4 | I3C2_SDA | AF3 |
| 28 | PB5 | I3C2_SCL | AF3 |
| 29 | PB6 | I3C1_SCL | AF3 |
| 30 | PB7 | I3C1_SDA | AF3 |
| 31 | BOOT0 | to ground through 10 kΩ | |
| pad | the exposed pad | VSS, VSSA and VREF−: the package has no ground pin, so the pad must be soldered (figure 5, note) | |

- PB3 to PB8 are FT_fhs, so both buses can drive Fm+ if the IMUs fall back to I2C.
- I3C2 sits on PB4 and PB5 as on the module, only at AF3 here instead of AF10.
- The package has no PH0 and PH1, hence no HSE, which fits: the Vnučata run on the HSI.
- The cable carries no interrupt wire, so "when the IMUs report data" means I3C in-band
  interrupts, which the controller supports (DS14053, table 6), or polling; as I2C, polling only.

**The foot** hangs on one Vnučka on the instep, on Interconnect to the calf's module, as in the
glove, with three or four IMUs:

| bus | IMUs |
|---|---|
| I3C1 | the heel and the instep |
| I3C2 | the toes, and a fourth where it is wanted |

## Power

A sensing module takes the suit's two rails, 3.7 V and 6 V (see
[Porjadok](../porjadok/HARDWARE.md#power)), and brings each down with one LDO:

| LDO | in | out | feeds |
|---|---|---|---|
| TI TPS7A47 | 6 V | 5 V | the ADS1299 analog side (AVDD, AVDD1) |
| TI TPS7A2033 | 3.7 V | 3.3 V | the processor, the RS-485 drivers, the ADS1299 digital side (DVDD), the IMUs |

- **TPS7A47:** input up to 36 V, 1 A, ~4 µVrms of noise. The output voltage is set by how its
  pins are wired on the board, with no resistors. Typical dropout is 307 mV, so going from 6 V
  to 5 V leaves room. The ADS1299 needs 4.75–5.25 V on AVDD.
- **TPS7A2033:** fixed 3.3 V, 300 mA, input 1.6–6 V, dropout 140 mV typical at 300 mA (SBVS338H
  gives no maximum), low noise without a bypass capacitor. 3.3 V on DVDD also lets the ADS1299
  be read at 20 MHz, which needs DVDD at 2.7–3.6 V. From 3.7 V it has ~0.26 V to spare for the
  cable at the dropout's worst; at the module's peak of ~135 mA the dropout is smaller still.
- **At the inputs,** where the cable arrives, a polymer bulk each, Panasonic POSCAP TPE:
  **6TPE100M** on 3.7 V (100 µF 6.3 V, case D2E 7.3 × 4.3 × 1.8 mm, 25 mΩ, 2.4 A of ripple,
  105 °C) and **10TPE47MAZB** on 6 V (47 µF 10 V, case B2 3.5 × 2.8 × 1.9 mm, 35 mΩ, 1.4 A,
  85 °C, 8 V at 105 °C). They are small on purpose: each line's converter charges its modules'
  bulks at start (see [Mamka](../mamka/HARDWARE.md#converters)). The driver's ~37 mA for 20 µs
  takes ~7 mV from 100 µF. The 6 V branch draws a steady ~8 mA, so its bulk stores nothing
  worth speaking of: it damps the cable and the π filter behind it. Ceramics against polymers: see
  [Mamka](../mamka/HARDWARE.md#filtering).

**Budget of one module**

| consumer | rail | current | source |
|---|---|---|---|
| STM32H523 at 197 MHz in VOS1 | 3.3 V | counted as at 200 MHz in VOS0, for margin: 24.5–53.3 mA typical, 84 mA at most (TJ 105 °C); VOS1 itself gives 21.3–46.5 mA and 72 mA | DS14540, table 26 |
| ADS1299, digital side | 3.3 V | 1 mA | SBAS499C |
| ICM-42688-P, 4 | 3.3 V | 4 × 0.88 mA, 6 axes in low-noise mode | TDK |
| THVD receivers, 3 | 3.3 V | ~2 mA each; 2.4 mA typical with no load, given at 5 V | TI |
| the driver while it sends | 3.3 V | ~37 mA more, ~2 V into the two 120 Ω terminations (~60 Ω; the datasheet tests with 54 Ω), ~8% of the time | estimate |
| status LED | 3.3 V | ~2 mA | estimate |
| ADS1299, analog side | 5 V | 7.14 mA | SBAS499C |

That makes ~69 mA on average and ~135 mA at the peak on 3.3 V, well within the TPS7A2033's
300 mA, and ~8 mA on 5 V. The suit's totals are under [Porjadok](../porjadok/HARDWARE.md#power).

The LDOs only do the coarse separation. Earlier drafts had an LDO for every branch; filters do
that job now:

- Behind each LDO the supply splits into a star with one branch per consumer: on the 3.3 V
  LDO the processor, the RS-485 drivers, the ADS1299 digital side and the IMUs; on the 5 V LDO
  the ADS1299 analog side.
- Every branch has its own π filter: capacitor, choke, capacitor.
- The ADS1299 supply is a trace of its own, not a poured plane.
- The filter parts are the ones of NIC-Heimdall's house rule ([core/POWER.md][heimdall-power],
  *The filter parts*):

  | part | what it is |
  |---|---|
  | choke **SWPA252012S2R2MT** | 2.2 µH, shielded, 2.5 × 2.0 × 1.2 mm, DC resistance 0.17 Ω, self-resonance 69 MHz, saturation 1.85 A; JLCPCB C23894 |
  | ferrite bead **GZ2012D301TF** | Sunlord, 0805, 300 Ω ±25% at 100 MHz, DC resistance at most 0.20 Ω, 500 mA |

- Every choke sits in a π filter of 10 µF 50 V X7R 1206 + 100 nF 50 V X7R 0603 on both sides,
  before it on the rail and behind it at the pins. 2.2 µH into 10 µF puts the corner at
  ~34 kHz, ~70 dB down at 2.2 MHz, where Mamka's converters switch; the choke's 0.17 Ω damps the
  pair to a Q of ~3–4. The rule: the supply must not drop by more than 0.1 V even at the
  highest peak.
- **The processor branch** has the bead in series with its choke. The choke sits on the LDO
  side, the bead next to the processor. The processor is the main source of high-frequency
  noise. Above its self-resonance a choke stops filtering, while a bead is resistive from
  about 100 MHz up and burns the noise off instead of storing it; at the converters' 2 MHz a
  bead is a few ohms and filters nothing, which is why it only ever stands behind a choke.
  Against a small ceramic capacitor (~0.3 Ω at 100 MHz, an estimate) 300 Ω gives roughly
  60 dB. The bead also keeps that noise off the 3.3 V that feeds the ADS1299 and the RS-485.
  - Drop: choke and bead together are at most 0.37 Ω. The STM32H523, counted as in VOS0 for margin,
    draws 24.5–53.3 mA typical at 200 MHz depending on the peripherals, up to 84 mA at TJ 105 °C,
    the most VOS0 allows (DS14540, tables 2 and 26). That makes 20 mV at 53 mA and 31 mV at 84 mA,
    under the 0.1 V limit.
  - The bead's impedance falls with DC current, so it needs current to spare.
  - Choke and bead can each resonate with the decoupling capacitors; check by simulation.
  - Behind the bead, local decoupling right at the VDD pins covers the processor's current
    spikes.

**From the ADS1299 datasheet** (SBAS499C, section 11):

- Bypass each supply with 10 µF and 0.1 µF ceramic capacitors.
- AVDD1 feeds the charge pump and carries transients at the CLK frequency: star-connect it to
  the AVDD pins, and AVSS1 to the AVSS pins.
- Return currents of the digital parts must not cross the analog return path.
- Where a board is subject to vibration, the VCAP1 capacitor should be non-ferroelectric
  (tantalum, or C0G/NP0): X7R and X5R are piezoelectric and turn vibration into noise. A suit
  moves, so this applies here. The datasheet also asks for C0G in the differential input
  capacitors (section 12.1); the bias loop's 1.5 nF follows the same reasoning.
- Power-up: all digital and analog inputs stay low until the supplies have settled. Only then
  does CLK start; after tPOR (2¹⁸ CLK periods, 133 ms at 1.96608 MHz, counted only once CLK is
  present) the ADS gets a reset. The suit clock runs all the time, so the block holds the
  timer output to the ADS CLK low until the ADS supplies are up.

## Open questions

- the pin map: checked against DS14540's pin and alternate-function tables (9 Oct 2026): every
  signal exists on its pin at the AF given, no pin or peripheral twice, and any GPDMA request
  goes to any of the 16 channels; STM32CubeMX on a PC still to confirm the clock tree and lay
  out the DMA,
- the ICM-42688-P on the first parts: SETDASA, which DS-000347 does not list, or else I2C at
  the static addresses,
- I3C over a cable: try the length and the rate on a sample,
- the input circuit: confirm the values on a sample,
- the right-leg drive: the loop's stability and the summed channels, tuned on a sample.

[heimdall-power]: https://github.com/Project-NIC/NIC-Heimdall/blob/main/core/POWER.md
