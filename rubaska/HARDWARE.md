<div align="center">

# Rubaška: hardware

**The sensing module's board,** the IMU and its board, the right-leg drive and the reference,
the strip's ground layer, the power, and the glove's and the sock's boards.

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

**Two chips on the body and on the head, one on the neck.** A module of the body carries two
ADS1298, one on each side of the board, 16 channels on 32 electrodes; the head's module two
ADS1299 in the same places, 16 channels on 32 electrodes with one reference electrode for both;
the neck's one ADS1299 in the first chip's place, 8 channels, its SRB1 the reference electrode's.
One board takes either chip, the two being pin-compatible (SBAS499C, Features): the pin tables
differ on pins 17 and 18, SRB1 and SRB2 on the ADS1299, TESTP_PACE_OUT1 and TESTN_PACE_OUT2 on
the ADS1298, and on pin 64, reserved and left open on the ADS1299, the WCT output on the ADS1298,
so at each chip's place pin 17's 4.99 kΩ to the reference electrode and pin 18's tie to AVSS are
0 Ω parts fitted only under an ADS1299, the head's two SRB1s reaching the one reference through a
4.99 kΩ each (our inference, to confirm on the head's board), and pin 64 stays open under both;
the second chip's places stay empty on the neck's module.

| part | package | role |
|---|---|---|
| STM32H523CCU6 | UFQFPN48, 7 × 7 mm | the module's processor: 256 KB of flash, 272 KB of RAM; see [Porjadok](../porjadok/README.md) |
| ADS1298, 2 | TQFP-64, 10 × 10 mm | 8 biopotential channels each, 24-bit, on 16 electrodes; on the head two ADS1299 and on the neck one in the first's place, the same footprint |
| ICM-45686, 1–4 | LGA-14, 2.5 × 3 × 0.81 mm, on its own small board | IMU: motion and orientation of the piece |
| TPS7A4700 | VQFN-20, 5 × 5 mm | 6 → 5 V for the ADS129x analog side, see [power](#power) |
| TPS7A2033 | X2SON 1 × 1 mm, or SOT-23-5 | 4 → 3.3 V for the rest |
| THVD1452, 2 | VSSOP-10, or SOIC-14 | the data pairs of the line |
| THVD1450 | VSON-8 or VSSOP-8, or SOIC-8 | the clock pair, receive only |
| TLV9001S | SOT-23-6 | the strip's ground layer's driver, see [The strip's ground layer](#the-strips-ground-layer) |

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
4. the two ADS129x, one on each side of the board, or the neck's one ADS1299, with their input
   circuits,
   and the electrode connector.

Digital and analog parts so stay apart; the ADS1299's datasheet asks that return currents of the
digital parts never cross the analog return path (SBAS499C, section 11).

**The processor's pins.** The STM32H523 in UFQFPN48 has 35 I/Os, four SPIs (three of them also
I2S), three USARTs, two UARTs and two I3C controllers (DS14540, table 2). The module needs 25:

| what | pins |
|---|---|
| ADS129x: SPI (SCLK, DIN, DOUT, the first chip's CS, the second's), both DRDYs, START, RESET, CLK | 10 |
| IMUs: two I3C buses (SCL and SDA each) and CLKIN | 5 |
| the line: receive from the master, transmit, DE, the echo | 4 |
| the suit clock in | 1 |
| the strip's ground layer's driver, its SHDN | 1 |
| SWD (SWDIO, SWCLK, SWO) and a status LED | 4 |
| **total** | **25** |

They land on the pins as below, from DS14540's pinout (figure 6) and its alternate functions
(tables 14 and 15). The sides of the package fall by job: the bottom is the ADS129x's, the
right the line's, the top the IMUs'.

| pin | name | use | AF |
|---|---|---|---|
| 1 | VBAT | to VDD | |
| 2–4 | PC13–PC15 | free | |
| 5 | PH0-OSC_IN | the suit clock, 9.8304 MHz, into the HSE in bypass | |
| 6 | PH1-OSC_OUT | free | |
| 7 | NRST | to the SWD connector | |
| 8, 9 | VSSA, VDDA | | |
| 10 | PA0 | ADS129x RESET, both chips | GPIO |
| 11 | PA1 | free | |
| 12 | PA2 | the strip's ground layer's driver, TLV9001S SHDN, with a pull-down | GPIO |
| 13 | PA3 | free | |
| 14 | PA4 | the first ADS129x's CS: SPI1_NSS | AF5 |
| 15 | PA5 | ADS129x SCLK: SPI1_SCK, both chips | AF5 |
| 16 | PA6 | ADS129x DOUT: SPI1_MISO, both chips | AF5 |
| 17 | PA7 | ADS129x DIN: SPI1_MOSI, both chips | AF5 |
| 18 | PB0 | ADS129x CLK: TIM3_CH3, both chips | AF2 |
| 19 | PB1 | ADS129x START: TIM3_CH4, both chips | AF2 |
| 20 | PB2 | the first chip's DRDY, on EXTI2 | GPIO |
| 21 | PB10 | the second chip's DRDY, on EXTI10, watched only | GPIO |
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
| 38 | PA15 | the second ADS1298's CS, by software | GPIO |
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
- TIM3 gives the ADS129x both their CLK and their START, so START keeps a fixed place against
  the CLK edges; on the head's and the neck's ADS1299 the firmware takes START high 511 CLK
  periods later than on the body's ADS1298 (see
  [Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement)).
- The line transmits on USART1, its DE driven by the USART itself, and reads itself back on
  USART1's RX: the echo. It receives from the master on UART4. Both reach 20 Mbaud with DMA
  (section 3.35.1).
- SPI1 takes frames of 4 to 32 bits (table 10); a chip's reading of 216 bits is read in frames of
  8 bits, the GPDMA moving the 27 bytes as they come (see
  [Porjadok](../porjadok/SOFTWARE.md#how-a-unit-builds-the-frame)). The two chips sit on it in
  cascade, DIN, DOUT and SCLK shared and a chip select each, the deselected chip's DOUT
  high-impedance (SBAS499C, 10.1.4.1): the first on the SPI's NSS, the second on PA15, read one
  after the other, 22 µs together. A daisy chain would share DIN, and "the individual devices
  cannot be programmed when sharing a common DIN" (10.1.4.2); the two differ in their settings.
- The HSE in bypass takes a digital clock of 4 to 50 MHz (table 38).
- PC13 to PC15 hang on the backup domain's power switch: 2 MHz and 30 pF at most, and no
  current to source, so not for the LED (table 13, note 2).
- Each VCAP takes 2.2 µF with an ESR under 100 mΩ (table 21).
- Ten I/Os stay free: PC13–PC15, PH1, PA1, PA3, PB8 and PB13–PB15. PA15 is JTDI after reset, an
  alternate function with its pull-up on (RM0481 Rev 5, GPIOx_MODER reset values), which holds
  the second chip deselected until the firmware takes the pin, as a select should be; PA2 comes
  up analog, and its pull-down holds the TLV9001S shut down, the strip's ground layer on ground.
- The chips' PWDN and CLKSEL pins are not driven: they are tied through resistors of 10 kΩ or
  more, as the datasheets ask for their mode pins, PWDN high and CLKSEL low for the external
  clock.
- The chips' unused pins, as the ADS1299's section 10.1.1 asks: GPIO1–4, DAISY_IN and RESV1 to
  DGND, BIASREF (the ADS1298's RLDREF) left open, the mid-supply made inside (see
  [software](SOFTWARE.md#the-ads129xs-settings)); pin 64 open under both chips, reserved on the
  ADS1299 and the WCT output on the ADS1298; the ADS1298's pins 17 and 18, its test outputs,
  open. On the ADS1299 pin 17, SRB1, goes through 4.99 kΩ to the connector for the reference
  electrode and pin 18, SRB2, to AVSS, both by 0 Ω parts fitted under it alone. The first chip's
  BIASIN, the ADS1298's RLDIN, is tied to its BIASOUT (see [Right-leg drive](#right-leg-drive));
  the second chip's bias pins stay open, its amplifier always powered down.

**The IMUs on I3C**

- **Two IMUs to a bus**, on the processor's two I3C controllers. An ICM-45686 has the static
  address 0x68 or 0x69, set by its AP_AD0 pin (DS-000489, 9.3), and takes SETDASA, which turns
  that into its I3C address (9.2, table 13). The ICM-42688-P's sheet does not list SETDASA;
  fitted, it may want the controller to talk to both as I2C at their static addresses, which
  the STM32H5's I3C does too (legacy I2C messages, AN5879). Two to a bus either way: more would
  need the chips' provisioned IDs to differ, and nothing promises that.
- **The cable** of a bus has five wires: SCL, SDA, +3.3 V, ground and CLKIN. The data are
  small, 12 B per IMU 1,920 times a second, 46 kB/s a bus, so the bus can run well below the
  12.5 MHz of I3C SDR, which helps over a cable.
- **The IMU clock** comes on the CLKIN wire. I3C has a clock over the bus too (synchronous
  timing control, SETXTIME), and ST's documents disagree on whether the STM32H5's controller
  has it: AN5879 Rev 6, table 3, says no, DS14540 Rev 3, table 8, and RM0481 Rev 5, table 598,
  say yes. The ICM-45686 has it (SIFS_I3C_STC_CFG, DS-000489), but on the interpolator CLKIN
  uses, and the ICM-42688-P documents its rates only from CLKIN (DS-000347, 12.5): the wire
  stays.
- **I3C2 has no Fm+:** PB4 and PB5 are FT_h pins, and only FT_f pins drive Fm+ (DS14540,
  5.3.32). Should the IMUs fall back to I2C, I3C2's bus runs at 400 kHz; I3C1 on PB6 and PB7
  (FT_f, FT_fa) could run 1 MHz. At 400 kHz two IMUs at 1,920 Hz would want ~1.3 times the
  bus, so as I2C the IMUs run the chip's own 120 Hz (see [software](SOFTWARE.md#the-imus-settings)).

**Clocks.** The suit clock, 9.8304 MHz, comes in through the THVD1450 and feeds the processor:
PLL1 makes the core's 49.152 MHz, on which the timers run, and the SPI's clock from a second
output, PLL3 the line's 196.608 MHz (see [Porjadok](../porjadok/SOFTWARE.md#the-clock-tree)).
Timers give the ADS129x their CLK, the suit clock ÷ 5 = 1.96608 MHz, the IMUs their CLKIN,
÷ 256 = 38,400 Hz, and take START high at the start of a measurement; see
[Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement).

**Inputs and their protection.** The inputs keep the classic circuit from the datasheets, a
series resistor and a capacitor before each input, as cheap as it can be and no cheaper: one
resistor a lead and one capacitor a channel, nothing else fitted.

- At the 2 kSPS setting a chip passes up to 0.262 of the rate (−3 dB, SBAS459K, Electrical
  Characteristics; SBAS499C, table 1), ~503 Hz at the suit's 1,920 SPS, SENIAM's band. The
  ADS1298's modulator samples at fCLK / 4 in its high-resolution mode, 492 kHz from the suit's
  1.96608 MHz, the ADS1299's at fCLK / 2, 983 kHz.
- The datasheet's example, 4.99 kΩ and 4.7 nF, is made for EEG. For EMG: **4.99 kΩ** in each
  lead and **220 pF C0G** across the pair, 0402 (0402WGF4991TCE and CL05C221JB5NNNC at JLCPCB,
  cents apiece, extended parts; the 0603 resistor is a Basic part, chosen when drawn). The
  electrode's contact adds to the resistors, so the corner depends on it,
  1 / (2π · 2 · (R_contact + 4.99 kΩ) · 220 pF):

  | contact per electrode | corner | at the ADS1298's modulator, 492 kHz | at the ADS1299's, 983 kHz |
  |---|---|---|---|
  | ~0 (on the bench) | 72 kHz | ~17 dB down | ~23 dB |
  | 20 kΩ | 14.5 kHz | ~31 dB down | ~37 dB |
  | 50 kΩ, the working figure | 6.6 kHz | ~37 dB down | ~43 dB |
  | 100 kΩ | 3.4 kHz | ~43 dB down | ~49 dB |

  The signal band, up to ~500 Hz, passes in every case. A larger capacitor would bring the
  corner of a moist contact down into the band, and electrodes with different contacts would
  then turn the common-mode voltage into a difference.
- The datasheet asks for C0G in the differential input capacitors (SBAS499C, 12.1), and the same
  vibration argument as for VCAP1 makes the bias loop's 1.5 nF C0G too. The capacitor is across
  the pair, not to ground: that "removes dependence on component mismatch" (10.2.2).
- **Empty places** for a 10 pF C0G from every input to ground, the datasheet's common-mode
  capacitors against radio, "10 or 20 times smaller than the differential capacitor" (10.2.2),
  fitted only if the arm shows a phone or the glasses in the signal; the strip's shielded leads
  do that job first.
- The resistor's thermal noise, 0.41 µVrms a pair over the band, lies inside the contacts' (see
  [The noise](#the-noise)); the lead-off current across it is steady and small, 6 nA × 4.99 kΩ =
  30 µV, the input's 300 pA 1.5 µV.
- **Protection** rests on the right-leg drive and the resistors, with no TVS and no clamp. The
  drive is the only wire that joins the body to the suit at low impedance, so it drains static
  from the body and holds it at mid-supply; the resistors limit the current into the chips' own
  input diodes, 10 mA at most into a pin (SBAS499C, 7.1). A discharge computed on a simple model:
  the wearer at 5 kV with 150 pF touching a handle through 330 Ω (IEC 61000-4-2's body) is a
  pulse of 15 A for ~50 ns, but the suit floats, its ground riding with the body through the
  strips' ground layers, ~17 nF, and the suit's ~100 pF to earth leaves 0.6 % of the swing
  between them, ~29 V: ~0.5 mA into an input for 50 ns, 26 pC, against the chip's 1 kV HBM
  rating, 0.67 A for ~150 ns (SBAS499C, 7.2). Only an earthed suit would empty the body through
  the inputs, 91 mA each for 32 ns, 3 nC, a thirtieth of the HBM test: the USB is isolated (see
  [Baťa](../bata/SOFTWARE.md#output-modes)) and the charger's output must float (see
  [Babuška](../babuska/HARDWARE.md#charging)). No inductance in the model; tried on the first arm
  with a carpet and a door handle while recording. The bias electrode and the reference
  electrode have a 4.99 kΩ of their own (see [Right-leg drive](#right-leg-drive)).
- **The same filter on every input:** 4.99 kΩ and 220 pF C0G on all thirty-two, so both ways of
  measuring on the head and the neck (see [Right-leg drive](#right-leg-drive)) see the same
  inputs. A module of two ADS1298 carries 33 resistors, 16 capacitors and 32 empty places on its
  inputs, under $0.20 of parts.

**Connectors and size.** The line arrives on the suit's cable of 16 wires in an IDC socket of 2 × 8
(see [Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit)). The band's strip goes
into a **locking connector for flexible circuits**, the kind with a lever that clamps the tail, one
footprint of **36 ways** at 0.5 mm: on a module of the body the 32 electrodes, the bias electrode,
the strip's ground layer and a +5 V for a strip that carries followers, 35; on the head's the 32
electrodes, the reference, the bias, the ground layer and the +5 V, all 36; on the neck's the
sixteen, the reference, the bias, the ground layer and the +5 V, 20, the rest empty (see
[electrodes](CONSTRUCTION.md#electrodes) and [The strip's ground layer](#the-strips-ground-layer));
the module unplugs from it before the harness is rinsed. Such a lever connector bears ~20 matings
(Hirose's FH12 as the kind), enough when the piece is rinsed with its modules on and the strip is
unplugged only at assembly and repair; sweat in the open connector is the risk, so on the first
boards the connector is potted after the last mating, and in the suit the tail may be soldered by
hot bar and potted, the module and its strip one part, if the trials show the connector failing. The
part is chosen when the board is drawn. The IMU buses go out the same way, each on a stretchable
strip of the glove's kind into a five-way locking connector: SCL, SDA, +3.3 V, ground and CLKIN.

### The noise

One channel over its band, 10 Hz to ~500 Hz, at a gain of 12, with an 8 mm stud's moist contact
taken as 50 kΩ (the working figure, to be measured):

| source | noise | from |
|---|---|---|
| the ADS1298 | 0.8 µVrms | SBAS459K, table 3, 2 kSPS, 5 V and the 4 V reference, the high-resolution mode |
| the ADS1299, on the head and the neck | 0.46 µVrms | SBAS499C, table 3, 2 kSPS |
| the contacts and the resistors, 2 × (50 + 4.99) kΩ at 37 °C | 0.96 µVrms | √(4kTRB), computed |
| the steps, 39.7 nV / √12 | 0.01 µVrms | computed |
| **the electronics and the contacts together** | **~1.25 µVrms, ~1.1 on the head and the neck** | |
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
  | 10 mm | 1.56× | ~32 kΩ | 0.8 µVrms | ~0.8× | 9.8 kHz |
  | 8 mm | 1× | ~50 kΩ | 0.96 µVrms | 1× | 6.6 kHz |
  | 6 mm | 0.56× | ~89 kΩ | 1.26 µVrms | ~1.3× | 3.9 kHz |

  Every one passes the band to 500 Hz, and the DC the inputs' currents leave stays negligible
  (300 pA × 89 kΩ = 27 µV, 6 nA × 89 kΩ = 0.53 mV).
- **Measured on a sample, with no instrument:** the same channel on the body and with its inputs
  shorted inside the chip (MUX 001, SBAS499C, table 17; the ADS1298's CHnSET the same) parts the
  skin's noise from the electronics'.

## The IMU

The IMU is the **TDK InvenSense ICM-45686** (DS-000489 Rev 1.1: ±32 g and ±4000 °/s, set to
±16 g and ±2000 °/s; I3C, I2C and SPI). It wins on the steadiness of its zero and on its clock
input:

- **A steady zero:** the gyro's offset drifts ±5 mdps/°C over −40 to +85 °C, board-level
  (DS-000489, table 1). With no magnetometer a joint's turn about the vertical rests on the zero
  between the moments at rest, so the drift weighs more than the noise: a warming of ~12 °C, the
  room to the skin, moves the zero 0.06 °/s, ~3.6° of heading a minute uncorrected, where ±20
  mdps/°C would make ~14°. The noise, 3.8 mdps/√Hz, adds up as a random walk, ~0.03° a minute
  and ~0.03 °/s RMS in a step of 120 Hz, far below any movement. Our calculation from the sheet's
  figures, the ~12 °C an estimate. The accelerometer 80 µg/√Hz; the gyro's cross-axis
  sensitivity ±0.2 % (tables 1 and 2).
- **A CLKIN input,** 20–40 kHz on pin 9 (DS-000489, 4.14), so it samples on the suit's clock,
  38,400 Hz.
- **1,920 Hz to 120 Hz.** Its rates are 100 Hz × 2ⁿ (GYRO_CONFIG0, ACCEL_CONFIG0). The chip has no
  register for the clock's frequency, RTC_CONFIG holding only RTC_ALIGN and RTC_MODE (16.37), and
  TDK measured 100.00 Hz at the 100 Hz setting with 32 kHz on CLKIN (*ICM-456xx External Clock
  Input (CLKIN)*, 10 Feb 2026). So its rates follow the clock, 38,400 Hz making them 1.2 times
  the setting: the 1.6 kHz setting **1,920 Hz**, sixteen samples to a step of 16 ADS samples,
  and the 100 Hz setting 120 Hz. **This is our inference, not TDK's words;** it is asked of TDK
  and measured on the first board. The module sums the sixteen into the step's turn and mean
  force (see [software](SOFTWARE.md#the-imus-settings)); in noise that equals the chip's own
  filtering to 120 Hz, and it keeps the turn right in fast swings.
- **The same board takes the ICM-42688-P,** the family's quietest gyro (2.8 mdps/√Hz, ±5 mdps/°C
  over 0–70 °C, DS-000347), should the ICM-45686's rate under CLKIN fail: pins 4–9 are the same,
  the reserved pins 2, 3 and 7 go to ground on both (the pin tables of both), and its CLKIN
  takes 31–50 kHz, so 38,400 Hz holds; its 1 kHz setting runs at 1,200 Hz, ten samples a step
  (DS-000347, 12.5). The unit's table names the part fitted (see
  [Porjadok](../porjadok/SOFTWARE.md#the-registers)).

Its ±2000 °/s can be exceeded in a violent swing or throw; ordinary movement stays well within
it, and ±4000 °/s is a setting away. The Bosch BMI570 has lower noise on paper, but we found no
external clock input on it.

[Mamka](../mamka/README.md) describes the clocks for both the ADS129x and the IMUs.

CLKIN comes in on pin 9, INT2/FSYNC/CLKIN, switched by IOC_PAD_SCENARIO_OVRD (0x31), a register
TDK's own driver sets (motion.arduino.ICM45686, release 1.1.9) and DS-000489 Rev 1.1 does not
describe; RTC_MODE in RTC_CONFIG (0x26) then puts the chip on it, through its interpolator (see
[software](SOFTWARE.md#the-imus-settings)). INT1 stays for interrupts. DS-000489 gives the
clock's timing no table we found; the ICM-42688-P's, a high time of at least 1 µs and edges of
5 to 500 ns (DS-000347, table 8), is kept for both, so the series resistors on long CLKIN wires
must not slow it past that.

### The IMU board

Each IMU sits on a small board of its own, on a bone or a phalanx, four layers like every board
here, the glove's too. Its supply is filtered
on the board, from the cable's 3.3 V to the chip:

| | part | JLCPCB |
|---|---|---|
| at the cable | 100 nF 50 V X7R 0402, Samsung CL05B104KB54PNC | C307331, Basic |
| in series | 6.8 Ω 0201, then TDK **MLF1608A4R7KTA00**, 4.7 µH, 0603 | |
| at VDD | 2 × 1 µF 25 V X5R 0402, Samsung CL05A105KA5NQNC, and 100 nF as above | C52923, Basic |
| at VDDIO, on the same node | 100 nF as above | C307331, Basic |

- **What the datasheets ask:** the ICM-45686 0.1 µF on VDD and 0.1 µF on VDDIO, X7R ±10 %, a
  larger one on VDD should the supply's ripple pass 50 mV peak to peak (DS-000489, 4.5, table
  11); the ICM-42688-P 0.1 µF and 2.2 µF on VDD and 10 nF on VDDIO (DS-000347 rev. 1.2, 4.3,
  table 10). The board carries what both ask, 100 nF on VDDIO being more than the ICM-42688-P's
  10 nF. The two 1 µF stand for the 2.2 µF: no 2.2 µF of 25 V or
  more is a Basic part at JLCPCB in 0402, and none in 0201 at all (JLCPCB's catalogue, 10 Oct
  2026). They are X5R, which holds its capacitance to 85 °C where X7R holds it to 125 °C; on
  the body that does. Their loss of capacitance at 3.3 V of DC bias is not checked.
- **25 V or more** on every capacitor, by choice, though the board sees 3.3 V.
- **The 6.8 Ω** damps the choke against the capacitors: 4.7 µH into ~2.1 µF resonates near
  50 kHz with a characteristic impedance of ~1.5 Ω, which 6.8 Ω swamps. The IMU's ~0.4 mA drops
  ~3 mV across it, the ICM-42688-P's ~0.9 mA ~6 mV. The choke's datasheet is not read here.
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
stays within the chips' input range, and it drains static from the body (SBAS499C, 9.3.2.4.5 and
10.1.3; the ADS1298's right-leg drive is the same circuit under its own names, RLD for BIAS,
SBAS459K). Its amplifier senses the common voltage of chosen channels (BIAS_SENSP, BIAS_SENSN)
and drives the body inverted, towards (AVDD + AVSS) / 2 = 2.5 V.

- **A lead of its own, with nothing in it but a resistor.** Every module has a bias electrode on
  a lead of its own: the first chip's BIASOUT, tied to its BIASIN, goes through 4.99 kΩ to it,
  not through the chip's multiplexer and through no switch. A second ADS1298's bias amplifier
  stays powered down, its BIASOUT and BIASIN open.
- **Every module can be the one, and the others are its spares.** The suit has 16 bias
  electrodes, one on every module near its band, best over bone with little muscle under it
  (see [Bogatyr](../bogatyr/CONSTRUCTION.md#the-electrodes-rules)). Normally one module drives,
  PD_BIAS on; the others have the amplifier powered down with PD_BIAS, as the datasheet asks
  when there are several devices (9.3.2.4.5), and their electrodes hang on the powered-down
  outputs. Should a bias electrode come off, Baťa moves the drive to another module, by one
  register bit; never two drive at once (see [why](WHY.md#the-sensing-module)).
- **A powered-down output leaves its electrode alone,** which is all the switch was there for
  (see [why](WHY.md#the-sensing-module)): the datasheet's own bias lead-off check works with the
  amplifier powered down, a current source of 6–24 nA on the BIASOUT pin pulling the electrode's
  node and a comparator reading it (9.3.2.4.4, figure 37), which can only hold if the powered-down
  output leaks far less than that. It is not a stated parameter; the first module confirms it
  with that very check, BIAS_STAT through a 50 kΩ resistor.
- **All channels measure** on every module, the driving one too, so every input of every chip is
  an electrode: 480 in a suit of 16 modules.
- **The loop:** 1 MΩ ∥ 1.5 nF between BIASINV and BIASOUT, the datasheet's values (figures 33
  and 68, "typical values for example only"), 0603 parts changed with a soldering iron. The
  common-mode gain is Rf · N / 330 kΩ (equation 11): with the driving chip's sixteen inputs
  summed (BIAS_SENSP = BIAS_SENSN = 0xFF), ~48; the capacitor puts the pole at
  1 / (2π · 1 MΩ · 1.5 nF) ≈ 106 Hz, so the mains meets nearly the whole gain. The body node has
  a pole of its own through the bias electrode's ~55 kΩ: with the strips' ground layers on
  ground, ~17 nF a suit, and every input's 20 + 43 pF, 16 nF more, at ~87 Hz beside the loop's;
  with the ground layers driven at the common mode they drop out of it, the chips' 5 nF stay,
  ~565 Hz (see [The strip's ground layer](#the-strips-ground-layer)). Tuned on a sample, module by
  module; TI's forum warns the amplifier off large capacitive loads (E2E, *bias shield drive*,
  as the search summarised it).
- **The 4.99 kΩ** is not for the drive's sake: the drive's currents are nanoamps to microamps,
  which make microvolts across it, nothing against a contact of tens of kilohms. It parts the
  amplifier's output from the capacitance of the lead and the body, against which an op-amp
  tends to ring, and it takes static. The amplifier itself gives ~1.1 mA typical into a short
  and has 100 kHz of gain-bandwidth (SBAS499C, *Patient bias amplifier*). The datasheet leaves
  the loop's stability to the system.
- **Faults:** from outside the suit hardly any, see below. Inside, two drivers against each
  other with one at its rail drive ~2.5 V through two contacts and 2 × 4.99 kΩ, tens of
  microamps; with one driver no direct current flows, the inputs having 1 GΩ.
- **Checks at start:** the bias lead-off check (SBAS499C, 9.3.2.4.4, figure 37). With the
  amplifier off (PD_BIAS = 0) and BIAS_LOFF_SENS = 1, a current source and a comparator on the
  bias pin tell whether the electrode is connected: BIAS_STAT 0 connected, 1 not. TI's own
  figure puts a protection resistor of 51 kΩ between the pin and the electrode; our path is
  4.99 kΩ, a tenth of that, so the check works through the lead of its own as the datasheet
  draws it. Every module checks its own electrode before any drives, so every spare bias
  electrode is checked too, not only the one that will drive.
- **While it runs:** with the amplifier on the current source does nothing, but the comparator
  still watches the amplifier's output against the thresholds set by LOFF[7:5], the same as for
  the other inputs (9.3.2.4.4). A bias electrode that comes off drives the loop to a rail, and
  the driving module's BIAS_STAT says so before the whole suit's channels saturate; the computer
  then moves the bias to another module.
- **The suit and the outside world:** a computer joins the suit only through an isolator or
  over the air (see [Baťa](../bata/SOFTWARE.md#output-modes)). The suit may be worn while it
  charges, the charger's output floating (see [Babuška](../babuska/HARDWARE.md#charging)).

**The reference electrode: the second way, on the head and the neck.** Their ADS1299s' SRB1 goes
through 4.99 kΩ each to the electrode connector, the head's two chips to the one electrode, with
no switch: the chip's own, the SRB1 bit in
MISC1, joins it to the channels (figure 18). The body's ADS1298 have no SRB1 (the pin tables), so
the body measures differentially alone and carries no reference electrode (see
[why](WHY.md#the-sensing-module)); the head's and the neck's module stays the same unit for a
headband that takes the brain's signals, or for a trial.

- **Differential:** the SRB1 bit clear, MISC1 = 0x00, the reference electrode on SRB1 standing idle.
  Each channel measures INnP − INnN: 8 channels of 16 electrodes a chip. How much SRB1 leaks when
  open with an electrode on it the datasheet does not give; it is checked on a sample.
- **Against the reference:** the SRB1 bit set in MISC1, which routes SRB1 to the inverting input of
  all eight channels (SBAS499C, MISC1 and section 10.2.2, figure 73); the INnN pins are then cut
  from the amplifiers (figure 18, the switch "MAIN and not SRB1"). IN1P to IN8P measure against the
  reference electrode, and IN1N to IN8N stand idle: 8 of a chip's 16 electrodes, every one against
  one point, the head's sixteen P against its one reference.
- The bias drive works in both: its lead does not go through the multiplexer.
- Which way serves the model better is to be measured on the head and the neck (see
  [Bogatyr](../bogatyr/CONSTRUCTION.md#open-questions)); the board is the same, only registers
  change.
- **Wiring for both:** a fitted reference runs on the same strip, under the same ground layer, as
  the band's electrodes, so that in the second way the loop between an electrode and the
  reference stays small.

## The strip's ground layer

The band's strip carries its leads under a solid ground layer on its outer face, the leads toward
the skin (see [construction](CONSTRUCTION.md#electrodes)). The layer is on the module's ground by
default and can be driven at the body's common mode, and the strip can carry a follower at every
stud: three levels, drawn on one board and one strip, so that the first arm tries them all with no
new board. The numbers are estimates on a lead of 20 cm, 2.2 pF/cm on 25 µm polyimide, 43 pF, the
P and N leads of a pair differing by 13 pF, with the contact at 50 kΩ ± 50 %, to be measured on
the sample.

| level | what it cures | what it leaves | what it costs |
|---|---|---|---|
| **(a)** the layer on ground, no parts | the room's fields and the fabric's static on the leads; the body's common mode turned into a difference by the unequal contacts, the potential divider (Metting van Rijn, Peper & Grimbergen 1990, eqn 3), ~7 µV pp at 10 mV pp of common mode | a bend of the lead moving charge off its 2.5 V against the layer, ~0.5 µV at 1 % of its capacitance in 100 ms; what the strip generates by itself | the strips' 17 nF and the leads' 11 nF in the bias loop |
| **(b)** the layer driven at the common mode: a TLV9001S on the first chip's BIASINV, gain 0.99 | the divider four times down, ~1.6 µV; the bend twenty-five times, only the electrode's ~0.1 V of offset left on the lead; the strips out of the bias loop | what the strip generates | one op-amp, two resistors and a pin; the loop's stability by the 1990 rules |
| **(c)** a follower at every stud, its output on the lead | the divider to ~0.3 µV; the bend; what the strip generates, the current flowing into the follower's output | the skin under the electrode, which nothing on the strip cures | 18 op-amps a module on the strip, potted with it; 1.1 mA (TLV9001) or 9.7 mA (TLV9061) a module; the noise 1.25 → 2.0 or 1.7 µVrms; **the lead-off currents end at the follower: the chips' impedance check is lost** |

- **BIASINV, not BIASOUT.** BIASOUT carries the error inverted and amplified, ~48 times the
  residual common mode, so a layer on it would couple 49 times more than one on ground, inside
  the loop. BIASINV is where the chip averages the selected channels' common mode, from the PGA
  outputs through 330 kΩ each, loading no electrode (SBAS499C, figure 38); the daisy chain of
  several chips ties their BIASINVs for that reason (figure 39). On a module whose bias amplifier
  is powered down BIASINV is its sixteen inputs' common mode at ~20 kΩ; on the one driving module
  it is the amplifier's summing node, held at mid-supply, so its layer sits at a steady 2.5 V and
  the leads' 2.5 V against the layer is gone there too. One circuit on every module, nothing to
  switch when Baťa moves the drive. To check on the sample: that a powered-down BIASOUT is
  high-impedance, so the loop's 1 MΩ does not load BIASINV, which the datasheet does not say.
- **The driver:** a **TLV9001S** (SOT-23-6, SBOS833R: 60 µA; shut down by SHDN, 0.5 µA, its
  output 10 GΩ ∥ 2 pF) as the follower on BIASINV, then a series resistor to the ground layer's
  way and a pull-down from that way to ground, ~3 kΩ and ~300 kΩ, 0603, changed with a soldering
  iron: together the attenuator for 0.99 and the low-pass of ~4 µs while the driver is on, and
  the plain ground while it is off, the coupled nanoamps making microvolts across 300 kΩ, a
  thousandth of that on the leads. Metting van Rijn's rules (eqns 5–9): a guard at a gain under 1
  is stable for any electrode, and flat when its time constant is about twice the electrode's
  and the lead's, 2 × 50 kΩ × 43 pF ≈ 4 µs, a low-pass at ~37 kHz; a driver cut off above ~1 MHz
  leaves the bias loop's stability alone, one at 10–100 kHz adds phase to it, so the two are
  tried side by side. SHDN on PA2 with its own pull-down, the layer on ground from reset until
  the firmware says otherwise: register 0x03 of chip 0x00, set by Baťa in the service mode, so
  the two levels are compared on the arm by a register (see
  [software](SOFTWARE.md#the-ads129xs-settings)).
- **The followers** live on the strip alone: the first strip is drawn with a follower's place at
  every stud, bridged by a 0 Ω part, and a +5 V trace from the connector's +5 V way, fed through
  10 Ω from the module's analog rail; a strip with the followers fitted is the next version of a
  part that is made by versions anyway. TLV9061 (X2SON 0.8 × 0.8 mm, 0.5 pA, 16 nV/√Hz, 538 µA,
  its sheet) or TLV9001 (the same package, 5 pA, 30 nV/√Hz, 60 µA, SBOS833R), both to 5.5 V, the
  body at 2.5 V with ±0.3 V of offset inside a rail-to-rail output; the module sees no difference
  but the lead-off check gone. The +5 V trace runs beside the ground layer's edge, never between
  two leads.
- **What decides,** with the module's own firmware and Baťa's recordings, in this order: the
  inputs shorted inside the chip (MUX 001), the floor; a dummy body, resistors of 50 kΩ from the
  strip's studs to one point, the strip bent, tapped and rubbed with the suit's fabric while
  recording, the driver off and on, which gives the strip's own artifact in microvolts with the
  skin out of it; then on the arm, still, moving, beside a mains cable, with the charger plugged
  in, fleece over the band, the band's pressure, the impedance by AC lead-off, the driver off
  against on, 20 Hz against 10 Hz in software, one module's bias loop with the strips on and then
  three; last a strip with followers against the passive one on the same arm. **The rule:** the
  passive strip stays if its own artifact lies under the electronics' ~1.25 µVrms and on the arm
  it reads like the one with followers; the driver stays on if the arm shows the 50 Hz residue or
  the bias loop needing it, else off and its parts not fitted on the next boards; the followers
  come only if the dummy body shows the strip generating, the impedance check given up with them.
- **What no strip cures:** the skin under the electrode, whose potential changes with stretch and
  pressure (de Talhouet & Webster, Physiol. Meas. 17, 1996; Chi, Jung & Cauwenberghs, IEEE Rev.
  Biomed. Eng. 3, 2010): the moist ring, the band's pressure and the high-pass do that (see
  [Baťa](../bata/SIGNALS.md#the-emg-channel)). The professionals part the same way: BioSemi puts
  the first stage in the electrode and measures no impedance, TMSi drives its cables' shields,
  Delsys and Meta put the amplifier in the sensor (BioSemi's FAQ on shielding and active
  electrodes; TMSi's SAGA manual as the search quoted it; Kaifosh et al., Nature 645, 2025, the
  Methods; Delsys' white paper on surface EMG).

## The glove

The glove is **Vešč**, the Thing: the Addams' severed hand, which ends at the wrist as ours
does. It is part of every suit with arms, **a unit of its own on its arm's line,** in the fourth
slot after the shoulder's, the upper arm's and the forearm's modules (see
[Porjadok](../porjadok/HARDWARE.md#links-between-boards)), with its own drivers: **one board on
the back of the hand** that carries the hand's EMG and its IMUs both. What it sends, and how, is
under [software](SOFTWARE.md#the-glove); where its electrodes and its IMUs sit on the hand, under
[Bogatyr](../bogatyr/CONSTRUCTION.md#the-gloves); its strips and its two layers, under
[construction](CONSTRUCTION.md#the-glove).

- **One board, two sides.** On one side the ADS1298 with its inputs, as a module's first chip
  (see [Sensing module](#sensing-module)): the hand's **16 electrodes on 8 channels,** the bias
  electrode from its BIASOUT through 4.99 kΩ, the strip's ground layer and its TLV9001S on
  BIASINV (see [The strip's ground layer](#the-strips-ground-layer)), 4.99 kΩ a lead and 220 pF a
  channel, and a lever connector of 20 ways for the hand's strip: the sixteen electrodes, the
  bias, the ground layer and the +5 V, one spare. On the other side Staršaja, the line's drivers
  and its IDC socket, the four Bratiški, the two LDOs and the five finger strips' connectors. The
  board sits over the bases of the second and third metacarpals, which hardly move against the
  wrist (see [Bogatyr](../bogatyr/CONSTRUCTION.md#the-gloves)); its size is seen when it is drawn.
- **Its Staršaja,** the elder, is the module's own part, the **STM32H523CCU6 in UFQFPN48,** so that
  one processor serves the module and the glove. Its 35 I/Os and six serial ports, five U(S)ARTs and
  the LPUART (DS14540 Rev 3, table 2), go round one way: the line keeps a module's one sender and
  two receivers, the master on USART1's RX and the echo on the LPUART's, which receives at the
  line's rate; the four Bratiški take USART2, USART3, UART4 and UART5; and since USART3's RX is PB1
  alone, where a module has START, her TIM2 makes the ADS1298's CLK and START and TIM5 counts the
  ticks; 33 I/Os in all, below. Beside her the line's drivers, a THVD1452 for the return pair and
  the quad receiver AM26LV32E for the pair from the master, the echo and the clock (see
  [Porjadok](../porjadok/HARDWARE.md#drivers-on-a-unit)), and her LDOs, a TPS7A2033 and a TPS7A47 as
  on a module (see [power](#power)).
- **Four Bratiški,** the younger brothers, on the board beside her, one a finger: each an
  **STM32H503KB in UFQFPN32** (5 × 5 mm) reading four IMUs, two on each of its two I3C buses, and
  sending their steps to Staršaja on a U(S)ART of its own. The package has no OSC_IN, and none is
  needed: Staršaja makes the IMUs' CLKIN, 38,400 Hz, from the suit clock for the whole board, so
  the IMUs sample in step with the suit, and a Bratiška only reads them, on his own HSI, ~6.2 kB/s
  of steps.
- **No SWD on a Bratiška.** An STM32H503 with nothing in its flash boots ST's bootloader with
  BOOT0 low, and with BOOT0 high always, its product state Open as delivered (AN2606 Rev 70,
  table 2, pattern 17; RM0492 Rev 3, table 8); the bootloader listens on USART2 among others, PA5
  and PA15, the very pins to Staršaja (AN2606, table 121). So the four come empty from the
  assembler and Staršaja programs them over the board's traces (AN3155 Rev 22: 8 bits, even
  parity, the rate found from a first byte 0x7F, 1,200 to 115,200 Bd; *Write Memory* 256 B at a
  time, *Read Memory* to check, each packet with an XOR checksum), and recovers one that will not
  answer by the BOOT0 line and a reset. The pads for SWD, and the debugger, are hers alone. How
  his image reaches her is under [software](SOFTWARE.md#the-bratiški).
- **The links** on the board, Staršaja's U(S)ART to each Bratiška's USART2, run full duplex at
  4 MBd, 8N1, push-pull, no pull-up: a step of 52 B in 0.13 ms (see
  [software](SOFTWARE.md#the-bratiški)). The receivers tolerate 3.33 % at Staršaja's USARTs,
  whose divider, 49, is not a multiple of 16 (RM0481 Rev 5, table 630), and 3.75 % at the Bratiška
  (RM0492 Rev 3, table 292), against the clocks' ~1.8 % at worst: the HSI 63.7–64.3 MHz at 30 °C
  and ±1 % over −20…105 °C (DS14053 Rev 4, table 40), Staršaja +0.31 %; on a trace of a few
  centimetres the edges cost nothing.
- **20 IMUs, 20 places:** on Staršaja's two buses the thumb's metacarpal and its two phalanges
  and the board's own, on the back of the hand; on each Bratiška's first bus the finger's proximal
  and middle phalanges, on its second the distal and a place to spare, four spares for the palm's
  arch, the fourth and fifth metacarpals' heads, and a second on the thumb's metacarpal, because
  its skin slides. Which are fitted, 20, 12 or 8, the recordings decide, the unit's table telling
  Baťa (see [Bogatyr](../bogatyr/CONSTRUCTION.md#the-gloves)). Each finger's strip carries seven
  wires, its Bratiška's two buses, CLKIN, +3.3 V and ground, in a seven-way lever connector on the
  board, the IMU boards along it in their five-way ones (see [the IMU board](#the-imu-board)).
- **Across the wrist** nothing crosses but the arm's line itself, the flat cable sewn in
  meanders over the wrist's back to the board's IDC socket; the glove unplugs from it and from its
  strips as a module does (see
  [Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit)).

**Staršaja's pins** in the glove, from the module's (see [Sensing module](#sensing-module)): the
second chip's two pins free, the master's receiver on USART1 and the echo's on the LPUART, UART4
and USART3 given to the Bratiški with USART2 and UART5, the ADS1298's CLK and START on TIM2, and
RESET, SHDN and the LED moved; the signals and their alternate functions from ST's
STM32_open_pin_data (STM32H523CCUx and GPIO modes v1_0, 29 Oct 2026), to be read against
DS14540's tables 14 and 15 when she is drawn:

| pin | name | use | AF |
|---|---|---|---|
| 1 | VBAT | to VDD | |
| 2 | PC13 | the strip's ground layer's driver, TLV9001S SHDN, with a pull-down | GPIO |
| 3, 4 | PC14, PC15 | free | |
| 5 | PH0-OSC_IN | the suit clock, 9.8304 MHz, into the HSE in bypass | |
| 6 | PH1-OSC_OUT | the Bratiški's NRST line, open-drain | GPIO |
| 7 | NRST | to the SWD connector | |
| 8, 9 | VSSA, VDDA | | |
| 10 | PA0 | to the third Bratiška: UART4_TX | AF8 |
| 11 | PA1 | ADS1298 CLK: TIM2_CH2 | AF1 |
| 12 | PA2 | to the first Bratiška: USART2_TX | AF7 |
| 13 | PA3 | from the first Bratiška: USART2_RX | AF7 |
| 14 | PA4 | the ADS1298's CS: SPI1_NSS | AF5 |
| 15 | PA5 | ADS1298 SCLK: SPI1_SCK | AF5 |
| 16 | PA6 | ADS1298 DOUT: SPI1_MISO | AF5 |
| 17 | PA7 | ADS1298 DIN: SPI1_MOSI | AF5 |
| 18 | PB0 | ADS1298 RESET | GPIO |
| 19 | PB1 | from the second Bratiška: USART3_RX | AF7 |
| 20 | PB2 | the ADS1298's DRDY, on EXTI2 | GPIO |
| 21 | PB10 | to the second Bratiška: USART3_TX | AF7 |
| 22 | VCAP | 2.2 µF | |
| 23, 24 | VSS, VDD | | |
| 25 | PB12 | from the fourth Bratiška: UART5_RX | AF14 |
| 26 | PB13 | to the fourth Bratiška: UART5_TX | AF14 |
| 27 | PB14 | the status LED | GPIO |
| 28 | PB15 | the line, receive from the master: USART1_RX | AF4 |
| 29 | PA8 | the IMUs' CLKIN, the whole board's: TIM1_CH1 | AF1 |
| 30 | PA9 | the line, transmit: USART1_TX | AF7 |
| 31 | PA10 | the echo: LPUART1_RX | AF3 |
| 32 | PA11 | from the third Bratiška: UART4_RX | AF6 |
| 33 | PA12 | the line, the driver's DE: USART1_DE | AF7 |
| 34 | PA13 | SWDIO | AF0 |
| 35, 36 | VSS, VDD | | |
| 37 | PA14 | SWCLK | AF0 |
| 38 | PA15 | ADS1298 START: TIM2_CH1, with a pull-down of 10 kΩ | AF1 |
| 39 | PB3 | SWO | AF0 |
| 40 | PB4 | I3C2_SDA | AF10 |
| 41 | PB5 | I3C2_SCL | AF10 |
| 42 | PB6 | I3C1_SCL | AF3 |
| 43 | PB7 | I3C1_SDA | AF3 |
| 44 | BOOT0 | to ground through 10 kΩ | |
| 45 | PB8 | the Bratiški's BOOT0 line | GPIO |
| 46 | VCAP | 2.2 µF | |
| 47, 48 | VSS, VDD | | |
| pad | the exposed pad | to ground (section 6.5, note 3) | |

- **The line as a module's,** one sender and two receivers: she sends on USART1's TX and takes the
  master's frames on its RX, PB15, and reads her own sending back on the LPUART's RX, PA10, at the
  line's 19.66 MBd: ten kernel clocks a bit, of the 3 to 4,096 allowed (RM0481 Rev 5, 57.4.8), BRR
  2,560, and a tolerance of 3.90 % (table 640) for what is her own signal; so UART4 is free for a
  Bratiška, and she listens before she talks on the echo's receiver as a module does. SWD and SWO
  stay. Two I/Os are left, PC14 and PC15.
- **PA15 as START** is JTDI after reset, pulled up (RM0481 Rev 5, GPIOx_MODER reset values), so
  START carries a pull-down of 10 kΩ, which holds it low from power-up to *start*, as the chip
  wants it, until the firmware drives it; PC13 as SHDN sources nothing but its pull-down's few
  microamps, which a pin of the backup domain allows (DS14540, table 13, note 2), and comes up
  with the TLV9001S shut down, the strip's ground layer on ground.
- **LPUART1** takes PLL3 Q as the USARTs, 196.608 MHz (LPUART1SEL = 010, RCC_CCIPR3, 11.8.42), up
  to 200 MHz in VOS1 as theirs (DS14540 Rev 3, table 20), receive only, its FIFO of 8 B and its
  DMA the USARTs' (DS14540, table 9). **TIM2 and TIM5:** TIM2 makes the ADS1298's CLK on its CH2
  and START on its CH1, the module's TIM3 PWM moved, and TIM5, 32 bits like TIM2 (DS14540, 3.31.2),
  counts the suit clock's ticks from the start command to START and from DRDY to the slot, with no
  pin. PH1 is a plain GPIO with the HSE in bypass (RM0481 Rev 5, 13.3.12).

**The Bratiška's pins** (DS14053 Rev 4, figure 5, tables 11 and 12):

| pin | name | what | AF |
|---|---|---|---|
| 4 | NRST | the reset line from Staršaja, shared by the four, open-drain | — |
| 6 | PA0 | the CLKIN, counted: TIM2_ETR | AF14 |
| 11 | PA5 | to Staršaja: USART2_TX | AF9 |
| 25 | PA15 | from Staršaja: USART2_RX | AF9 |
| 26 | PB3 | I3C2_SCL | AF3 |
| 27 | PB4 | I3C2_SDA | AF3 |
| 29 | PB6 | I3C1_SCL | AF3 |
| 30 | PB7 | I3C1_SDA | AF3 |
| 31 | BOOT0 | the BOOT0 line from Staršaja, shared by the four, 10 kΩ to ground | — |

Nothing else of his is wired but the supply, VCAP and the exposed pad; the WLCSP25, 2.33 × 2.24
mm at a 0.40 mm pitch, carries every pin above too (DS14053 Rev 4, figure 4), should the hand's
board want it (see [WHY](WHY.md#the-sensing-module)).

**The glove's current,** an estimate on the 4 V rail, counted as the modules are, on the safe
side:

| consumer | current | source |
|---|---|---|
| Staršaja | counted as a module's processor, 53.3 mA typical, 84 mA at most | DS14540, table 26 (see [power](#power)) |
| the ADS1298, digital side | 0.5 mA | SBAS459K, Power Supply |
| four Bratiški at 32 MHz in VOS3 | ~4.7 mA typical and ~11.6 mA at TJ 105 °C each, between the 25 and 60 MHz rows with every peripheral on; 18.8 and 46.4 mA | DS14053 Rev 4, table 23 |
| 20 ICM-45686 | 20 × 0.42 mA at 1.6 kHz in low-noise mode; counted as the ICM-42688-P's 0.88 mA, which the same board may carry, 17.6 mA | DS-000489, table 3; TDK |
| the THVD1452 | ~2 mA | TI |
| the AM26LV32E | 8 mA typical, 17 mA at most | SLLS849E |
| status LED | ~2 mA | estimate |
| the driver while it sends | ~37 mA, ~8 % of the time | estimate |
| **the glove, 4 V** | **~0.11 A on average, ~0.21 A at worst** | |
| the ADS1298's analog side and the TLV9001S, on 6 V | 3.1 mA and 60 µA | SBAS459K; SBOS833R |

### The sock

The sock is **Nosok**, Russian for a sock: the glove's board and firmware for the foot, a unit of
the glove's kind in its leg's fourth slot, after the hip's, the thigh's and the calf's modules,
with its own drivers and number (see [Porjadok](../porjadok/SOFTWARE.md#the-bratiški)). The
board sits on the calf above the ankle, where the calf's module's strip crosses too, not on the
foot, which a shoe presses: the foot's **16 electrodes on 8 channels** come up on a strip across
the ankle, and its IMU strips go down to the foot, **up to eight IMUs** to start, on Staršaja's
own places and one or two Bratiški, the other Bratiški unfitted, its table telling how many.
Where they sit is under [Bogatyr](../bogatyr/CONSTRUCTION.md#the-socks); the strips and the
layers under [construction](CONSTRUCTION.md#the-sock). Its current, counted as the glove's above
with two Bratiški and eight IMUs, **~0.09 A on average, ~0.17 A at worst** on 4 V.

## Power

A sensing module takes the suit's two rails, 4 V and 6 V (see
[Porjadok](../porjadok/HARDWARE.md#power)), and brings each down with one LDO:

| LDO | in | out | feeds |
|---|---|---|---|
| TI TPS7A47 | 6 V | 5 V | the ADS129x analog side (AVDD, AVDD1) and the strip's driver |
| TI TPS7A2033 | 4 V | 3.3 V | the processor, the RS-485 drivers, the ADS129x digital side (DVDD), the IMUs |

- **TPS7A47:** input up to 36 V, 1 A, ~4 µVrms of noise. The output voltage is set by how its
  pins are wired on the board, with no resistors. Typical dropout is 307 mV, so going from 6 V
  to 5 V leaves room. The ADS1299 needs 4.75–5.25 V on AVDD (SBAS499C), and the ADS1298's 4 V
  reference wants AVDD of 4.4 V at least (SBAS459K).
- **TPS7A2033:** fixed 3.3 V, 300 mA, input 1.6–6 V, dropout at most 140 mV at 300 mA, and its
  ±1.5% from an input of 3.6 V up (SBVS338H, 5.5), low noise without a bypass capacitor. 3.3 V on
  DVDD also lets the chips be read at 20 MHz, an SCLK period of 50 ns at a DVDD of 2.7–3.6 V
  (SBAS499C, 7.6; SBAS459K, the timing requirements). From 4 V the cable,
  the filters and the connectors leave it at least ~3.67 V at the worst corner (see
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
| ADS1298, 2, digital side | 3.3 V | 2 × 0.5 mA in the high-resolution mode; the head's two ADS1299 2 mA, the neck's one 1 mA | SBAS459K, Power Supply; SBAS499C |
| ICM-45686, 4 | 3.3 V | 4 × 0.42 mA at 1.6 kHz in low-noise mode; counted as the ICM-42688-P's 0.88 mA, which the same board may carry | DS-000489, table 3; TDK |
| THVD receivers, 3 | 3.3 V | ~2 mA each; 2.4 mA typical with no load, given at 5 V | TI |
| the driver while it sends | 3.3 V | ~37 mA more, ~2 V into the two 120 Ω terminations (~60 Ω; the datasheet tests with 54 Ω), ~8% of the time | estimate |
| status LED | 3.3 V | ~2 mA | estimate |
| ADS1298, 2, analog side | 5 V | 2 × 3.1 mA in the high-resolution mode; the head's two ADS1299 14.3 mA, the neck's 7.14 | SBAS459K, Power Supply; SBAS499C |
| TLV9001S, the strip's driver | 5 V | 60 µA on, 0.5 µA shut down | SBOS833R |

That makes ~69 mA on average and ~135 mA at the peak on 3.3 V, well within the TPS7A2033's
300 mA, and ~7 mA on 5 V, ~15 on the head's module and ~8 on the neck's. The suit's totals are under
[Porjadok](../porjadok/HARDWARE.md#power).

The LDOs only do the coarse separation; the filters do the rest:

- Behind each LDO the supply splits into a star with one branch per consumer: on the 3.3 V
  LDO the processor, the RS-485 drivers, the ADS129x digital side and the IMUs; on the 5 V LDO
  the ADS129x analog side and the strip's driver.
- Every branch has its own π filter: capacitor, choke, capacitor.
- The ADS129x supply is a trace of its own, not a poured plane.
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
  60 dB. The bead also keeps that noise off the 3.3 V that feeds the ADS129x and the RS-485.
  - Drop: choke and bead together are at most 0.37 Ω. The STM32H523, counted as in VOS0 for margin,
    draws 24.5–53.3 mA typical at 200 MHz depending on the peripherals, up to 84 mA at TJ 105 °C,
    the most VOS0 allows (DS14540, tables 2 and 26). That makes 20 mV at 53 mA and 31 mV at 84 mA,
    under the 0.1 V limit.
  - The bead's impedance falls with DC current, so it needs current to spare.
  - Choke and bead can each resonate with the decoupling capacitors; check by simulation.
  - Behind the bead, local decoupling right at the VDD pins covers the processor's current
    spikes.

**From the ADS1299's datasheet** (SBAS499C, section 11), the ADS1298's asking the same of its
three supplies, AVDD, AVDD1 and DVDD (SBAS459K, Power Supply Recommendations):

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
  goes to any of the 16 channels; PA2, PA15 and PB10, given on 29 Oct 2026 as plain GPIO and
  EXTI10, to be checked the same way; the clock tree (see [software](SOFTWARE.md#clocks)) and
  the DMA table (see [software](SOFTWARE.md#dma)), checked on the first board,
- the two chips in cascade on one SPI: the second's select on PA15, both reads within 22 µs, the
  second chip's DRDY against the first's, on the first board,
- the ICM-45686's rate under CLKIN at 38,400 Hz, the 1.6 kHz setting at 1,920 Hz by our
  inference: asked of TDK, measured on the first board; and pin 9 made CLKIN by
  IOC_PAD_SCENARIO_OVRD, which DS-000489 Rev 1.1 does not describe,
- I3C over a cable: try the length and the rate on a sample,
- the input circuit: confirm the values on a sample,
- the noise on the body against the inputs shorted (see [The noise](#the-noise)), with the
  contact's real impedance, for each kind of electrode,
- the right-leg drive: the loop's stability and the summed channels, tuned on a sample, with the
  strips' ground layers on ground and driven; one driving module for the whole body, checked as
  the modules are added,
- the bias check's comparator threshold and current (LOFF), set on a sample,
- a powered-down bias amplifier's output with an electrode on it, which the datasheet does not
  state: confirmed on the first module by the bias lead-off check through 50 kΩ, the switch
  having gone on the strength of that check,
- the strip's ground layer: on ground, driven and with followers, the three levels on the first
  arm in the order [The strip's ground layer](#the-strips-ground-layer) gives; the TPU strips'
  meanders as a shield; the lever connector potted after mating against a soldered tail,
- the two ways of measuring, differential and against the reference, compared on the head and
  the neck,
- the IMU board: the stretchable circuit's stiffened tail in the locking connector, bent and
  pulled, and potted round; the 1 µF's capacitance at 3.3 V,
- the glove: Staršaja's pins above checked against DS14540's tables 14 and 15, the board's size and
  its place on the back of the hand with the hand's strip, the finger strips' seven wires in their
  connectors; the Bratiški programmed through the bootloader over the board's traces, the BOOT0 and
  NRST lines, on the first board; the sock: the foot's strip across the ankle and its IMU strips;
  the IMUs' addresses on one I3C bus by AP_AD0 and SETDASA, tried on the bench,
- the module and the glove's Staršaja at 49.152 MHz, the Bratiški at 32 MHz: their currents,
  measured.

