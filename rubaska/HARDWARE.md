<div align="center">

# Rubaška: hardware

**The sensing module's board,** the IMU and its board, the right-leg drive and the reference,
the power, and the glove's boards.

↑ [Rubaška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## Sensing module

The sensing module is the suit's basic block; a suit has 8 to 16 of them. Together they are the
*Rebjata*, Russian for the kids: Mamka's own children, on the end of her
[Pupovina](../porjadok/HARDWARE.md#links-between-boards); one of them is a *Rebjonok*, the child. A
module is one board in its piece, as small as it can be: fewer and smaller parts, fewer pads,
smaller connectors. Its IMUs sit along the bones, each on a small board of its own, joined to the
module by I3C, two IMUs to a bus. No SPI runs over a cable anywhere.

| part | package | role |
|---|---|---|
| STM32H523CCU6 | UFQFPN48, 7 × 7 mm | the module's processor: 256 KB of flash, 272 KB of RAM; see [Porjadok](../porjadok/README.md) |
| ADS1299 | TQFP-64, 10 × 10 mm | 8 biopotential channels, 24-bit, on 16 electrodes |
| ICM-42688-P, 1–4 | LGA-14, 2.5 × 3 × 0.91 mm, on its own small board | IMU: motion and orientation of the piece |
| TPS7A4700 | VQFN-20, 5 × 5 mm | 6 → 5 V for the ADS1299 analog side, see [power](#power) |
| TPS7A2033 | X2SON 1 × 1 mm, or SOT-23-5 | 4 → 3.3 V for the rest |
| THVD1452, 2 | VSSOP-10, or SOIC-14 | the data pairs of the line |
| THVD1450 | VSON-8 or VSSOP-8, or SOIC-8 | the clock pair, receive only |
| TMUX1101 | SC70-5, 2.0 × 2.1 mm | the bias electrode's switch, see [Right-leg drive](#right-leg-drive) |

The smallest packages of a part come first. Leadless packages (QFN, X2SON, VSON) need machine
assembly, which the boards get anyway.

The modules sit on lines 1–7, a line a piece of the body, up to four units on each. They are joined
by a full-duplex (four-wire) RS-485 bus with time-division multiple access (TDMA), with a one-way
RS-485 channel for the clock alongside it; see
[Porjadok](../porjadok/HARDWARE.md#links-between-boards).

**Layout.** The board is long and narrow, in this order:

1. the line connector, with the RS-422/485 drivers right by it,
2. the processor, as close to them as it can be,
3. a gap,
4. the ADS1299 with its input circuit, and the electrode connector.

Digital and analog parts so stay apart; the ADS1299 datasheet asks that return currents of the
digital parts never cross the analog return path (SBAS499C, section 11).

**The processor's pins.** The STM32H523 in UFQFPN48 has 35 I/Os, four SPIs (three of them also
I2S), three USARTs, two UARTs and two I3C controllers (DS14540, table 2). The module needs 23:

| what | pins |
|---|---|
| ADS1299: SPI (SCLK, DIN, DOUT, CS), DRDY, START, RESET, CLK | 8 |
| IMUs: two I3C buses (SCL and SDA each) and CLKIN | 5 |
| the line: receive from the master, transmit, DE, the echo | 4 |
| the suit clock in | 1 |
| the bias electrode's switch | 1 |
| SWD (SWDIO, SWCLK, SWO) and a status LED | 4 |
| **total** | **23** |

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
| 10 | PA0 | ADS1299 RESET | GPIO |
| 11 | PA1 | the bias electrode's switch, TMUX1101 SEL, with a pull-down | GPIO |
| 12, 13 | PA2, PA3 | free | |
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
  frame in [Porjadok](../porjadok/SOFTWARE.md#the-frames)). SPI4 would stop at 16 bits
  (table 10).
- The HSE in bypass takes a digital clock of 4 to 50 MHz (table 38).
- PC13 to PC15 hang on the backup domain's power switch: 2 MHz and 30 pF at most, and no
  current to source, so not for the LED (table 13, note 2).
- Each VCAP takes 2.2 µF with an ESR under 100 mΩ (table 21).
- Twelve I/Os stay free: PC13–PC15, PH1, PA2, PA3, PA15, PB8, PB10 and PB13–PB15. PA15 is JTDI
  after reset, an alternate function with its pull-up on (RM0481 Rev 5, GPIOx_MODER reset values),
  so it drives no switch; PA1 comes up analog, and its pull-down holds the bias switch open.
- The ADS1299's PWDN and CLKSEL pins are not driven: they are tied through resistors of
  10 kΩ or more, as the datasheet asks for its mode pins, PWDN high and CLKSEL low for the
  external clock.
- The ADS1299's unused pins, as its section 10.1.1 asks: GPIO1–4 and DAISY_IN to DGND, SRB2 to AVSS,
  BIASREF left open (the mid-supply is made inside, see
  [software](SOFTWARE.md#the-ads1299s-settings)). SRB1 goes through 4.99 kΩ to the connector, for a
  reference electrode, and BIASIN is tied to BIASOUT (see [Right-leg drive](#right-leg-drive)).

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

**Clocks.** The suit clock, 9.8304 MHz, comes in through the THVD1450 and feeds the processor:
PLL1 makes the core's 49.152 MHz, on which the timers run, and the SPI's clock from a second
output, PLL3 the line's 196.608 MHz (see [Porjadok](../porjadok/SOFTWARE.md#the-clock-tree)).
Timers give the ADS1299 its CLK, the suit clock ÷ 5 = 1.96608 MHz, the IMUs their CLKIN,
÷ 256 = 38,400 Hz, and take START high at the start of a measurement; see
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
  series resistors limit the current into the ADS1299's own input diodes. The bias electrode
  and the reference electrode have a 4.99 kΩ of their own, the bias's before its switch (see
  [Right-leg drive](#right-leg-drive)).
- **The same filter on every input:** 4.99 kΩ and 220 pF C0G on all sixteen, so both ways of
  measuring (see [Right-leg drive](#right-leg-drive)) see the same inputs.

**Connectors and size.** The line arrives on the suit's cable of 14 wires in an IDC socket (see
[Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit)). The band's strip goes
into a **locking connector for flexible circuits**, the kind with a lever that clamps the
tail, ~20 ways: the sixteen electrodes, the reference, the bias electrode and the strip's
ground layer (see [electrodes](CONSTRUCTION.md#electrodes)); the module unplugs from it before
the harness is rinsed. The part is chosen when the board is drawn. The IMU buses go out the same
way, each on a stretchable strip of the glove's kind into a five-way locking connector: SCL,
SDA, +3.3 V, ground and CLKIN.

### The noise

One channel over its band, 10 Hz to ~1 kHz, at a gain of 12, with an 8 mm stud's moist contact
taken as 50 kΩ (the working figure, to be measured):

| source | noise | from |
|---|---|---|
| the ADS1299 | 0.65 µVrms | SBAS499C, table 3, 4 kSPS |
| the contacts and the resistors, 2 × (50 + 4.99) kΩ at 37 °C | 1.37 µVrms | √(4kTRB), computed |
| the steps, 44.70 nV / √12 | 0.01 µVrms | computed |
| **the electronics and the contacts together** | **~1.5 µVrms** | |
| the skin under the electrode, electrochemical | 1–20 µVrms by skin and wearer | Huigen et al. 2002 |

- **Against the EMG:** 0 to 1.5 mV rms, 0 to 10 mV peak to peak, its energy up to 500 Hz and
  most of it at 50–150 Hz (De Luca, *Surface Electromyography: Detection and Recording*, Delsys
  2002); a light contraction gives tens of microvolts. The electronics leave it a wide margin.
- **The skin decides.** The electrochemical noise is the largest, and per De Luca it grows with
  the square root of the electrode's surface resistance (after Huigen et al. 2002), so roughly
  as one over the stud's diameter; it shrinks with a larger stud, a moist contact and clean skin.
- **The stud's size** against the same working figure (contact ∝ 1 / area; computed, not
  measured):

  | stud | area | contact | the contacts' thermal noise | the skin's noise | the filter's corner |
  |---|---|---|---|---|---|
  | 10 mm | 1.56× | ~32 kΩ | 1.1 µVrms | ~0.8× | 9.8 kHz |
  | 8 mm | 1× | ~50 kΩ | 1.4 µVrms | 1× | 6.6 kHz |
  | 6 mm | 0.56× | ~89 kΩ | 1.8 µVrms | ~1.3× | 3.9 kHz |

  Every one passes the band to 500 Hz, and the DC the inputs' currents leave stays negligible
  (300 pA × 89 kΩ = 27 µV, 6 nA × 89 kΩ = 0.53 mV).
- **Measured on a sample, with no instrument:** the same channel on the body and with its inputs
  shorted inside the ADS1299 (MUX 001, SBAS499C table 17) parts the skin's noise from the
  electronics'.

## The IMU

The IMU is the **TDK InvenSense ICM-42688-P** (±16 g, ±2000 °/s, 2 KB FIFO, SPI, I2C and I3C).
It won on its noise and its clock input, and the suit's
clock gives it exactly 1,200 Hz, and 120 Hz for the steps:

- **Low noise,** so it holds still when the body does: the gyro 2.8 mdps/√Hz, the
  accelerometer 65–70 µg/√Hz, and a gyro offset that drifts ±5 mdps/°C, the least in its
  family (TDK's table in DS-000639). The ICM-45686 has 3.8 mdps/√Hz and 80 µg/√Hz (DS-000577).
- **A CLKIN input,** 31–50 kHz, so it samples from the suit's clock.
- **1,200 Hz to 120 Hz.** CLKIN scales the ODR by f_CLKIN / 32 kHz (DS-000347, section 12.5),
  so 38,400 Hz turns the 1 kHz setting into exactly 1,200 Hz, ten samples to a step of 32 ADS
  samples, and the 100 Hz setting into 120 Hz, with nothing to divide in the processor. The
  module sums the ten into the step's turn and mean force (see
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

### The IMU board

Each IMU sits on a small board of its own, on a bone or a phalanx, four layers like every board
here, the glove's too. Its supply is filtered
on the board, from the cable's 3.3 V to the chip:

| | part | JLCPCB |
|---|---|---|
| at the cable | 100 nF 50 V X7R 0402, Samsung CL05B104KB54PNC | C307331, Basic |
| in series | 6.8 Ω 0201, then TDK **MLF1608A4R7KTA00**, 4.7 µH, 0603 | |
| at VDD | 2 × 1 µF 25 V X5R 0402, Samsung CL05A105KA5NQNC, and 100 nF as above | C52923, Basic |
| at VDDIO, on the same node | 10 nF 50 V X7R 0402, Samsung CL05B103KB5NNNC | C15195, Basic |

- **What the datasheet asks:** 0.1 µF and 2.2 µF on VDD, 10 nF on VDDIO, all X7R ±10%
  (DS-000347 rev. 1.2, 4.3, table 10). The two 1 µF stand for the 2.2 µF: no 2.2 µF of 25 V or
  more is a Basic part at JLCPCB in 0402, and none in 0201 at all (JLCPCB's catalogue, 10 Oct
  2026). They are X5R, which holds its capacitance to 85 °C where X7R holds it to 125 °C; on
  the body that does. Their loss of capacitance at 3.3 V of DC bias is not checked.
- **25 V or more** on every capacitor, by choice, though the board sees 3.3 V.
- **The 6.8 Ω** damps the choke against the capacitors: 4.7 µH into ~2.1 µF resonates near
  50 kHz with a characteristic impedance of ~1.5 Ω, which 6.8 Ω swamps. The IMU's ~0.9 mA drops
  ~6 mV across it. The choke's datasheet is not read here.
- **The connector:** a five-way locking connector for flexible circuits, with a lever: SCL,
  SDA, +3.3 V, ground and CLKIN. The stretchable circuit's tail, stiffened over ~4 mm, goes in
  and the lever clamps it. The board is potted, all but the connector. The part is chosen when
  the board is drawn.
- **The fallback,** should the stretchable circuit fail on a sample: Kyocera AVX **9175-700**
  IDCs, a 3-way and a 2-way, 2.5 mm pitch, 26–28 AWG, insulation 0.70–1.00 mm for 28 AWG, 1 A a
  contact, pottable (Kyocera AVX, *9175-700*, *9176-800*), with PTFE wire of 28 AWG, 19 × 0.08
  mm, MIL-W-16878/4 Type E, ~0.89 mm across (AWC, E28-19); PTFE does not wear through at the
  sides of the fingers as silicone would.

## Right-leg drive

The bias drive holds the body at the modules' mid-supply, so that the electrodes' common voltage
stays within the ADS1299's input range, and it drains static from the body (ADS1299 datasheet
SBAS499C, sections 9.3.2.4.5 and 10.1.3). Its amplifier senses the common voltage of chosen
channels (BIAS_SENSP, BIAS_SENSN) and drives the body inverted, towards (AVDD + AVSS) / 2 =
2.5 V.

- **A lead of its own, through a switch.** Every module has a bias electrode on a lead of its
  own: BIASOUT, tied to BIASIN, goes through 4.99 kΩ and a TI **TMUX1101** to it, not through
  the ADS1299's multiplexer. The TMUX1101 (SCDS410D) is a single switch in SC70-5 for 1.08 to
  5.5 V, here on AVDD, closed at SEL high from VIH 1.49 V, so the processor's 3.3 V drives it;
  1.8 Ω closed; open, 5 pA typical and 80 pA at most at 25 °C, 0.3 nA to 85 °C, and 6 pF and
  10 pF on its two sides; 1 µA of supply at most. A pull-down on SEL keeps it open until the
  firmware closes it.
- **Every module can be the one, and the others are its spares.** The suit has 16 bias
  electrodes, one on every module near its band, best over bone with little muscle under it
  (see [Bogatyr](../bogatyr/CONSTRUCTION.md#the-electrodes-rules)). Normally one module drives: its
  switch closed and PD_BIAS on; the others have the amplifier powered down with PD_BIAS, as
  the datasheet asks when there are several devices, and their switch open. Should a bias
  electrode come off, Baťa moves the drive to another module. Driving from every module at
  once is to be tried on a sample against one (see below).
- **All eight channels measure** on every module, the driving one too, so all sixteen inputs
  of every ADS1299 are electrodes: 256 in a suit of 16 modules.
- **The loop:** 1 MΩ ∥ 1.5 nF between BIASINV and BIASOUT, the datasheet's values (figures 33
  and 68, "typical values for example only"). The common-mode gain is Rf · N / 330 kΩ
  (equation 11): with the driving module's sixteen inputs summed (BIAS_SENSP = BIAS_SENSN =
  0xFF), ~48; the capacitor puts the pole at 1 / (2π · 1 MΩ · 1.5 nF) ≈ 106 Hz, so the mains
  meets nearly the whole gain. Tuned on a sample.
- **The 4.99 kΩ** is not for the drive's sake: the drive's currents are nanoamps to microamps,
  which make microvolts across it, nothing against a contact of tens of kilohms. It parts the
  amplifier's output from the capacitance of the lead and the body, against which an op-amp
  tends to ring, and it takes static. The amplifier itself gives ~1.1 mA typical into a short
  and has 100 kHz of gain-bandwidth (SBAS499C, *Patient bias amplifier*). The datasheet leaves
  the loop's stability to the system.
- **Faults:** from outside the suit hardly any, see below. Inside, two drivers against each
  other with one at its rail drive ~2.5 V through two contacts and 2 × 4.99 kΩ, tens of
  microamps; with one driver no direct current flows, the inputs having 1 GΩ.
- **Checks at start:** the ADS1299's bias lead-off check (SBAS499C, 9.3.2.4.4, figure 37). With
  the amplifier off (PD_BIAS = 0) and BIAS_LOFF_SENS = 1, a current source and a comparator on
  the bias pin tell whether the electrode is connected: BIAS_STAT 0 connected, 1 not. TI's own
  figure puts a protection resistor of 51 kΩ between the pin and the electrode; our path is
  4.99 kΩ and the switch's 1.8 Ω, a tenth of that, so the check works through the lead of its
  own as the datasheet draws it. The switch must be closed for it, so the modules check one by
  one, each with its own switch closed, and so every spare bias electrode is checked too, not
  only the one that will drive.
- **While it runs:** with the amplifier on the current source does nothing, but the comparator
  still watches the amplifier's output against the thresholds set by LOFF[7:5], the same as for
  the other inputs (9.3.2.4.4). A bias electrode that comes off drives the loop to a rail, and
  the driving module's BIAS_STAT says so before the whole suit's channels saturate; the computer
  then moves the bias to another module.
- **The suit and the outside world:** a computer joins the suit only through an isolator or
  over the air (see [Baťa](../bata/SOFTWARE.md#output-modes)). The suit may be worn while it
  charges (see [Babuška](../babuska/HARDWARE.md#the-battery)).

**The reference electrode: the second way, on every module.** The ADS1299's SRB1 goes through
4.99 kΩ to the electrode connector, with no switch: the ADS1299's own, the SRB1 bit in MISC1,
joins it to the channels (figure 18). Every module has its reference electrode, both ways on one
suit (see [Bogatyr](../bogatyr/README.md)); the unit stays the same for a headband that takes the
brain's signals, or for a trial.

- **Differential:** the SRB1 bit clear, MISC1 = 0x00, the reference electrode on SRB1 standing
  idle. Each channel measures INnP − INnN: 8 channels of 16 electrodes. How much SRB1 leaks when
  open with an electrode on it the datasheet does not give; it is checked on a sample.
- **Against the reference:** the SRB1 bit set in MISC1, which
  routes SRB1 to the inverting input of all eight channels (SBAS499C, MISC1 and section 10.2.2,
  figure 73); the INnN pins are then cut from the amplifiers (figure 18, the switch "MAIN and not
  SRB1"). IN1P to IN8P measure against the reference electrode, and IN1N to IN8N stand idle: 8 of
  the 16 electrodes, every one against one point.
- The bias drive works in both: its lead does not go through the multiplexer.
- Which way serves the model better is to be measured on one arm (see
  [Bogatyr](../bogatyr/CONSTRUCTION.md#open-questions)); the board is the same, only registers
  change.
- **Wiring for both:** a fitted reference runs on the same strip, under the same ground layer, as
  the band's electrodes, so that in the second way the loop between an electrode and the
  reference stays small.

## The glove

The glove is **Vešč**, the Thing: the Addams' severed hand, which ends at the wrist as ours
does. It is part of every suit with arms, **a unit of its own on its arm's line,** in the fourth
slot after the shoulder's, the upper arm's and the forearm's modules (see
[Porjadok](../porjadok/HARDWARE.md#links-between-boards)), with its own drivers. What it sends,
and how, is under [software](SOFTWARE.md#the-glove); where its IMUs sit on the hand, under
[Bogatyr](../bogatyr/CONSTRUCTION.md); its stretchable circuit and its two layers, under
[construction](CONSTRUCTION.md#the-glove).

- **Its Staršaja,** the elder, sits before the wrist, on the sleeve: an **STM32H523 in LQFP64**,
  which has six U(S)ARTs without the LPUART, which is not used: one for the line and five for the
  fingers, the line's echo on a plain pin (ST's STM32_open_pin_data: five U(S)ARTs in UFQFPN48,
  six in LQFP64). Beside her the line's drivers, a THVD1452 and an AM26LV32E (see
  [Porjadok](../porjadok/HARDWARE.md#drivers-on-a-unit)), and her LDO, a TPS7A2033 as on a
  module. Which of the part's flash sizes, and her pins, are chosen when she is drawn.
- **Five Bratiški,** the younger brothers, one a finger, each an **STM32H503KB in UFQFPN32**
  (5 × 5 mm) with four IMUs, two on each of its two I3C buses: I3C1 on PB6 and PB7, I3C2 on PB3 and
  PB4, and its single wire to Staršaja on USART1_TX at PA9, half duplex (ST's
  STM32_open_pin_data, STM32H503KBUx; DS14053 Rev 4; the AFs still to read). The package has no
  OSC_IN, and none is needed: Staršaja makes the IMUs' CLKIN, 38,400 Hz, from the suit clock and
  sends it on one wire, so the IMUs sample in step with the suit, and a Bratiška only reads them,
  on its own HSI, ~5.8 kB/s of steps. Where the Bratiški sit on the hand is seen when it is
  drawn.
- **20 IMUs,** four a Bratiška: on each finger its three phalanges and its metacarpal; on the
  thumb its two phalanges, its metacarpal and a second on it, because its skin slides.
- **Across the wrist eight wires:** the five Bratiški's half-duplex wires, CLKIN, the supply and
  ground; nothing else crosses it.

**The glove's current,** an estimate on the 4 V rail, counted as the modules are, on the safe
side:

| consumer | current | source |
|---|---|---|
| Staršaja | counted as a module's processor, 53.3 mA typical, 84 mA at most | DS14540, table 26 (see [power](#power)) |
| five Bratiški at 32 MHz in VOS3 | ~4.7 mA typical and ~11.6 mA at TJ 105 °C each, between the 25 and 60 MHz rows with every peripheral on; 23.5 and 58 mA | DS14053 Rev 4, table 23 |
| 20 ICM-42688-P | 20 × 0.88 mA | TDK |
| the THVD1452 | ~2 mA | TI |
| the AM26LV32E | 8 mA typical, 17 mA at most | SLLS849E |
| the driver while it sends | ~37 mA, a few % of the time | estimate |
| **the glove** | **~0.11 A on average, ~0.22 A at worst** | |

## Power

A sensing module takes the suit's two rails, 4 V and 6 V (see
[Porjadok](../porjadok/HARDWARE.md#power)), and brings each down with one LDO:

| LDO | in | out | feeds |
|---|---|---|---|
| TI TPS7A47 | 6 V | 5 V | the ADS1299 analog side (AVDD, AVDD1) |
| TI TPS7A2033 | 4 V | 3.3 V | the processor, the RS-485 drivers, the ADS1299 digital side (DVDD), the IMUs |

- **TPS7A47:** input up to 36 V, 1 A, ~4 µVrms of noise. The output voltage is set by how its
  pins are wired on the board, with no resistors. Typical dropout is 307 mV, so going from 6 V
  to 5 V leaves room. The ADS1299 needs 4.75–5.25 V on AVDD.
- **TPS7A2033:** fixed 3.3 V, 300 mA, input 1.6–6 V, dropout at most 140 mV at 300 mA, and its
  ±1.5% from an input of 3.6 V up (SBVS338H, 5.5), low noise without a bypass capacitor. 3.3 V on
  DVDD also lets the ADS1299 be read at 20 MHz, which needs DVDD at 2.7–3.6 V. From 4 V the cable,
  the filters and the connectors leave it at least ~3.64 V at the worst corner (see
  [Porjadok](../porjadok/HARDWARE.md#end-to-end)).
- **At the inputs,** where the cable arrives, a polymer bulk each, Panasonic POSCAP TPE:
  **6TPE100M** on 4 V (100 µF 6.3 V, case D2E 7.3 × 4.3 × 1.8 mm, 25 mΩ, 2.4 A of ripple,
  105 °C) and **10TPE47MAZB** on 6 V (47 µF 10 V, case B2 3.5 × 2.8 × 1.9 mm, 35 mΩ, 1.4 A,
  85 °C, 8 V at 105 °C). They are small on purpose: each line's converter charges its modules'
  bulks at start (see [Mamka](../mamka/HARDWARE.md#converters)). The driver's ~37 mA for 20 µs
  takes ~7 mV from 100 µF. The 6 V branch draws a steady ~8 mA, so its bulk stores nothing
  worth speaking of: it damps the cable and the π filter behind it. Ceramics against polymers: see
  [Mamka](../mamka/HARDWARE.md#filtering).

**Budget of one module**

| consumer | rail | current | source |
|---|---|---|---|
| STM32H523 at 49.152 MHz in VOS1 | 3.3 V | counted as at 200 MHz in VOS0, for margin: 24.5–53.3 mA typical, 84 mA at most (TJ 105 °C); VOS1 itself gives 21.3–46.5 mA and 72 mA | DS14540, table 26 |
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
- The filter parts are the house parts:

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
  present) the ADS gets a reset. The module starts the timer output to the ADS CLK only once
  it runs on the suit clock (see [Porjadok](../porjadok/SOFTWARE.md#bring-up)), and the ADS
  supplies come up with the line before that.

## Open questions

- the pin map: checked against DS14540's pin and alternate-function tables (9 Oct 2026): every
  signal exists on its pin at the AF given, no pin or peripheral twice, and any GPDMA request
  goes to any of the 16 channels; the clock tree (see [software](SOFTWARE.md#clocks)) and
  the DMA table (see [software](SOFTWARE.md#dma)), checked on the first board,
- the ICM-42688-P on the first parts: SETDASA, which DS-000347 does not list, or else I2C at
  the static addresses,
- I3C over a cable: try the length and the rate on a sample,
- the input circuit: confirm the values on a sample,
- the noise on the body against the inputs shorted (see [The noise](#the-noise)), with the
  contact's real impedance, for each kind of electrode,
- the right-leg drive: the loop's stability and the summed channels, tuned on a sample; one
  driver against all sixteen at once,
- the bias check's comparator threshold and current (LOFF), set on a sample,
- the two ways of measuring, differential and against the reference, compared on one arm,
- the IMU board: the stretchable circuit's stiffened tail in the locking connector, bent and
  pulled, and potted round; the 1 µF's capacitance at 3.3 V,
- the glove: Staršaja's pins in LQFP64 and her flash size, the Bratiški's AFs from DS14053, the
  wires across the wrist and their rate, where the Bratiški sit on the hand; the IMUs' addresses
  on one I3C bus by AP_AD0 and SETDASA, tried on the bench,
- the module and the glove's Staršaja at 49.152 MHz, the Bratiški at 32 MHz: their currents,
  measured.

