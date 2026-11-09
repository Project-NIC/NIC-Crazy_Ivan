<div align="center">

# Rubaška: hardware

**The sensing module's board,** the IMU and its board, the right-leg drive, the strip's ground
layer, the power, and the glove's and the sock's boards.

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

**Two chips on the body and on the head, one on the neck.** Every module carries the ADS1298,
one chip, one board and one firmware for all: a module of the body two, one on each side of the
board, 16 channels on 32 electrodes; the head's two in the same places, 16 channels on 32
electrodes; the neck's one in the first chip's place, 8 channels, the second chip's places
empty. Every channel measures differentially, P against N; no strip carries a reference
electrode (see [Right-leg drive](#right-leg-drive)).

| part | package | role |
|---|---|---|
| STM32H523CCU6 | UFQFPN48, 7 × 7 mm | the module's processor: 256 KB of flash, 272 KB of RAM; see [Porjadok](../porjadok/README.md) |
| ADS1298, 2 | TQFP-64, 10 × 10 mm | 8 biopotential channels each, 24-bit, on 16 electrodes; on the neck one, in the first's place; JLCPCB C527440 |
| LSM6DSV16X, 1–4 | LGA-14L, 2.5 × 3 × 0.83 mm, on its own small board | IMU: motion and orientation of the piece, see [The IMU](#the-imu) |
| LP2985-5.0 | SOT-23-5 | 6 → 5 V for the ADS1298's analog side, see [power](#power) |
| TPS7A2033 | X2SON 1 × 1 mm, or SOT-23-5 | 4 → 3.3 V for the rest |
| THVD1450, 3 | VSON-8 or VSSOP-8, or SOIC-8 | the line: the pair from the master and the clock, receive only; the return pair, driving it and reading it back |
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
4. the two ADS1298, one on each side of the board, or the neck's one, with their input circuits,
   and the strip's connector.

Digital and analog parts so stay apart; the ADS1298's datasheet asks that return currents of the
digital parts never cross the analog return path (SBAS459K, section 11).

**The processor's pins.** The STM32H523 in UFQFPN48 has 35 I/Os, four SPIs (three of them also
I2S), three USARTs, two UARTs and two I3C controllers (DS14540, table 2). The module needs 25:

| what | pins |
|---|---|
| ADS1298: SPI (SCLK, DIN, DOUT, the first chip's CS, the second's), both DRDYs, START, RESET, CLK | 10 |
| IMUs: two I3C buses (SCL and SDA each) and REF | 5 |
| the line: receive from the master, transmit, DE, the echo | 4 |
| the suit clock in | 1 |
| the strip's ground layer's driver, its SHDN | 1 |
| SWD (SWDIO, SWCLK, SWO) and a status LED | 4 |
| **total** | **25** |

They land on the pins as below, from DS14540's pinout (figure 6) and its alternate functions
(tables 14 and 15). The sides of the package fall by job: the bottom is the ADS1298's, the
right the line's, the top the IMUs'.

| pin | name | use | AF |
|---|---|---|---|
| 1 | VBAT | to VDD | |
| 2–4 | PC13–PC15 | free | |
| 5 | PH0-OSC_IN | the suit clock, 9.8304 MHz, into the HSE in bypass | |
| 6 | PH1-OSC_OUT | free | |
| 7 | NRST | to the SWD pads; 100 nF to ground | |
| 8, 9 | VSSA, VDDA | | |
| 10 | PA0 | ADS1298 RESET, both chips | GPIO |
| 11 | PA1 | free | |
| 12 | PA2 | the strip's ground layer's driver, TLV9001S SHDN, with a pull-down of 4.7 kΩ (see [The strip's ground layer](#the-strips-ground-layer)) | GPIO |
| 13 | PA3 | free | |
| 14 | PA4 | the first ADS1298's CS: SPI1_NSS | AF5 |
| 15 | PA5 | ADS1298 SCLK: SPI1_SCK, both chips | AF5 |
| 16 | PA6 | ADS1298 DOUT: SPI1_MISO, both chips | AF5 |
| 17 | PA7 | ADS1298 DIN: SPI1_MOSI, both chips | AF5 |
| 18 | PB0 | ADS1298 CLK: TIM3_CH3, both chips | AF2 |
| 19 | PB1 | ADS1298 START: TIM3_CH4, both chips | AF2 |
| 20 | PB2 | the first chip's DRDY, on EXTI2 | GPIO |
| 21 | PB10 | the second chip's DRDY, on EXTI10, watched only | GPIO |
| 22 | VCAP | 2.2 µF; joined to pin 46 | |
| 23, 24 | VSS, VDD | | |
| 25 | PB12 | the status LED | GPIO |
| 26–28 | PB13–PB15 | free | |
| 29 | PA8 | the IMUs' REF: TIM1_CH1 | AF1 |
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
| 46 | VCAP | 2.2 µF; joined to pin 22 | |
| 47, 48 | VSS, VDD | | |
| pad | the exposed pad | to ground (section 6.5, note 3) | |

- SWO can only go on PB3, which is also I3C2's SCL; its other SCLs are PA8, which REF takes, and
  PB5, so I3C2 takes PB5 and PB4.
- TIM3 gives the chips both their CLK and their START, so START keeps a fixed place against
  the CLK edges (see [Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement)).
- The line transmits on USART1, its DE driven by the USART itself, and reads itself back on
  USART1's RX: the echo. It receives from the master on UART4. Both reach 20 Mbaud with DMA
  (section 3.35.1).
- SPI1 takes frames of 4 to 32 bits (table 10); a chip's reading of 216 bits is read in frames of 8
  bits, the GPDMA moving the 27 bytes as they come (see
  [Porjadok](../porjadok/SOFTWARE.md#how-a-unit-builds-the-frame)). The two chips sit on it in
  cascade, DIN, DOUT and SCLK shared and a chip select each, the deselected chip's DOUT
  high-impedance (SBAS459K, 9.4.2.1): the first on the SPI's NSS, the second on PA15, read one after
  the other, 24 µs together, the first's CS held 2.03 µs after its last clock (tSCCS, 7.6). A daisy
  chain shares DIN only where every device holds the same settings, and then "the individual devices
  cannot be programmed" (9.4.2.2); the two differ in their settings.
- The HSE in bypass takes a digital clock of 4 to 50 MHz (table 38).
- PC13 to PC15 hang on the backup domain's power switch: 2 MHz and 30 pF at most, and no
  current to source, so not for the LED (table 13, note 2).
- Each VCAP takes 2.2 µF with an ESR under 100 mΩ (table 21), and the two are joined; NRST takes
  100 nF to ground (ST's reference design for the H523, AN5711 Rev 5, figure 16 and its note).
- Ten I/Os stay free: PC13–PC15, PH1, PA1, PA3, PB8 and PB13–PB15. PA15 is JTDI after reset, an
  alternate function with its pull-up on (RM0481 Rev 5, GPIOx_MODER reset values), which holds the
  second chip deselected until the firmware takes the pin, as a select should be, rising with the
  chip's own 3.3 V, not before it (our reading of 11.1); PA2 comes up analog, and its pull-down
  of 4.7 kΩ holds the TLV9001S shut down against the pull-up the chip has inside on SHDN
  (SBOS833R, 8.5; its current at a low 150 nA, 7.10, ~0.7 mV across the 4.7 kΩ; a low under
  0.2 V above V−, 7.10), the strip's ground layer on ground.
- The chips' PWDN and CLKSEL pins are not driven: they are tied through resistors of 10 kΩ or
  more, as the datasheets ask for their mode pins, PWDN high and CLKSEL low for the external
  clock.
- The chips' unused pins, as SBAS459K's pin table asks (Pin Functions, TQFP, notes 1 and 2):
  DAISY_IN and RESV1 to DGND; TESTP_PACE_OUT1 and TESTN_PACE_OUT2, pins 17 and 18, to AVDD, and
  the second chip's RLDIN with them; GPIO1–4 to DGND, read as inputs; RLDREF left open, the
  mid-supply made inside (see [software](SOFTWARE.md#the-ads129xs-settings)); WCT, pin 64, open,
  its amplifiers off; the NC pins 27 and 29 open, or through 10 kΩ to AVDD or AVSS as the table
  allows. The first chip's RLDIN is tied to its RLDOUT (see [Right-leg drive](#right-leg-drive));
  the second chip's RLDOUT and RLDINV stay open, its amplifier always powered down.

**The IMUs on I3C**

- **Two IMUs to a bus**, on the processor's two I3C controllers. An LSM6DSV16X has the static
  address 0x6A or 0x6B, set by its SDO/SA0 pin, and takes SETDASA, which turns that into its
  I3C address (DS13510 Rev 4, table 17); its provisioned ID, read by GETPID, differs only by that
  pin (table 17), so two to a bus: more would need IDs that differ, and nothing promises that.
- **The cable** of a bus has five wires: SCL, SDA, +3.3 V, ground and REF. The data are
  small, 12 B per IMU 960 times a second, 23 kB/s a bus, so the bus can run well below the
  12.5 MHz of I3C SDR, which helps over a cable.
- **A pull-up of 2.2 kΩ on each bus's SDA** at the processor, as on the glove: I3C drives push-pull
  but runs the address's arbitration and the ACKs open-drain, and the pin's own pull-up, ~40 kΩ,
  would leave a rise of ~2 µs against SCLL_OD's few hundred ns (the review's arithmetic, 5 Nov
  2026; the IMU boards carry none). 2.2 kΩ is the start, 1.8 or 1.2 kΩ if the scope wants a
  quicker rise (the owner): 1.2 kΩ is 2.75 mA at 3.3 V, under the 4 mA an IMU holds at 0.2 V
  (DS13510 Rev 4, table 4).
- **The IMUs' rate** is held by REF, on a wire of its own into each IMU's INT2 (see
  [The IMU](#the-imu)). I3C has a clock over the bus too (synchronous timing control,
  SETXTIME), and ST's documents disagree on whether the STM32H5's controller has it: AN5879
  Rev 6, table 3, says no, DS14540 Rev 3, table 8, and RM0481 Rev 5, table 598, say yes. The
  LSM6DSV16X lists SETXTIME and a synchronous mode (DS13510, 5.2.1 and table 17), but documents
  its rate held to an outside clock only from INT2 (AN5763 Rev 4, 3.3): the wire stays.
- **I3C2 has no Fm+:** PB4 and PB5 are FT_h pins, and only FT_f pins drive Fm+ (DS14540,
  5.3.32). Should the IMUs fall back to I2C, I3C2's bus runs at 400 kHz; I3C1 on PB6 and PB7
  (FT_f, FT_fa) could run 1 MHz. At 400 kHz two IMUs at 960 Hz would want ~0.65 of the bus,
  too little room left, so as I2C the IMUs run the 120 Hz mode (see
  [software](SOFTWARE.md#the-imus-settings)).

**Clocks.** The suit clock, 9.8304 MHz, comes in through the THVD1450 and feeds the processor:
PLL1 makes the core's 49.152 MHz, on which the timers run, and the SPI's clock from a second
output, PLL3 the line's 196.608 MHz (see [Porjadok](../porjadok/SOFTWARE.md#the-clock-tree)).
Timers give the ADS1298 their CLK, the suit clock ÷ 5 = 1.96608 MHz, and the IMUs their REF,
÷ 409,600 = 24 Hz or ÷ 655,360 = 15 Hz (see [The IMU](#the-imu)), and take START high at the
start of a measurement; see [Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement).

**Inputs and their protection.** The inputs keep the classic circuit from the datasheets, a
series resistor and a capacitor before each input, as cheap as it can be and no cheaper: one
resistor a lead and one capacitor a channel, nothing else fitted.

- At the 2 kSPS setting a chip passes up to 0.262 of the rate (−3 dB, SBAS459K, Electrical
  Characteristics), ~503 Hz at the suit's 1,920 SPS, SENIAM's band. The ADS1298's modulator
  samples at fCLK / 4 in its high-resolution mode, 492 kHz from the suit's 1.96608 MHz (9.6.1.2).
  Inside the chip an RC at every input acts as an EMI filter, ~3 MHz at −3 dB (9.3.1.1).
- The datasheet's example, 4.99 kΩ and 4.7 nF, is made for EEG. For EMG: **4.99 kΩ** in each
  lead and **220 pF C0G** across the pair, 0402 (0402WGF4991TCE and CL05C221JB5NNNC at JLCPCB,
  cents apiece, extended parts; the 0603 resistor is a Basic part, chosen when drawn). The
  electrode's contact adds to the resistors, so the corner depends on it,
  1 / (2π · 2 · (R_contact + 4.99 kΩ) · 220 pF):

  | contact per electrode | corner | at the ADS1298's modulator, 492 kHz |
  |---|---|---|
  | ~0 (on the bench) | 72 kHz | ~17 dB down |
  | 20 kΩ | 14.5 kHz | ~31 dB down |
  | 50 kΩ, the working figure | 6.6 kHz | ~37 dB down |
  | 100 kΩ | 3.4 kHz | ~43 dB down |

  The signal band, up to ~500 Hz, passes in every case. A larger capacitor would bring the
  corner of a moist contact down into the band, and electrodes with different contacts would
  then turn the common-mode voltage into a difference.
- The datasheet asks for C0G in the input filter's capacitors (SBAS459K, 12.1), and the same
  vibration argument as for VCAP1 makes the bias loop's 47 nF C0G too. The capacitor is across
  the pair, not to ground, so that no mismatch of two capacitors to ground turns the common mode
  into a difference, which "causes common-mode rejection degradation" (10.1.3).
- **Empty places** for a 10 pF C0G from every input to ground, TI's common-mode capacitors against
  radio, "10 or 20 times smaller than the differential capacitor" (the ADS1299's sheet, SBAS499C,
  10.2.2), fitted only if the arm shows a phone or the glasses in the signal; the strip's shielded
  leads do that job first.
- The resistors' thermal noise, 0.29 µVrms a pair over the band (√(4kTRB), 9.98 kΩ, 310 K), lies
  inside the contacts' (see [The noise](#the-noise)); no lead-off current runs while the suit is
  active (see [software](SOFTWARE.md#an-electrode-coming-off)), so nothing but the input's 1 nA
  lies across it, 5 µV (SBAS459K, Electrical Characteristics, 0–70 °C).
- **Protection** rests on the right-leg drive and the resistors, with no TVS and no clamp. The
  drive is the only wire that joins the body to the suit at low impedance, so it drains static
  from the body and holds it at mid-supply; the resistors limit the current into the chips' own
  input diodes, 10 mA at most into a pin (SBAS459K, 7.1). A discharge computed on a simple model:
  the wearer at 5 kV with 150 pF touching a handle through 330 Ω (IEC 61000-4-2's body) is a
  pulse of 15 A for ~50 ns, but the suit floats, its ground riding with the body through the
  strips' ground layers, ~17 nF or more, and the suit's ~100 pF to earth leaves 0.6 % of the
  swing between them, ~29 V: ~0.5 mA into an input for 50 ns, 26 pC, against the chip's 2 kV
  HBM rating, 1.33 A for ~150 ns (SBAS459K, 7.2). Only an earthed suit would empty the body
  through the inputs, 91 mA each for 32 ns, 3 nC, under a sixtieth of the HBM test: the USB is
  isolated (see [Baťa](../bata/SOFTWARE.md#output-modes)) and the charger's output must float
  (see [Babuška](../babuska/HARDWARE.md#charging)). No inductance in the model; tried on the
  first arm with a carpet and a door handle while recording. The bias electrode has 100 kΩ of
  its own (see [Right-leg drive](#right-leg-drive)).
- **The same filter on every input:** 4.99 kΩ and 220 pF C0G on all thirty-two. A module of two
  ADS1298 carries 32 resistors and the bias lead's 100 kΩ, 16 capacitors and 32 empty places on
  its inputs, under $0.20 of parts.

**Connectors and size.** A connector here opens only at assembly and repair: the units are potted
whole with their connectors mated and stay on the harness (see
[construction](CONSTRUCTION.md#harness-and-washing)).

- **The line** arrives on the suit's cable of 16 wires, the 3M 3811 (see
  [Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit)), in a **Molex Picoflex
  PF-50 in tin:** the IDT receptacle 90327-0316 pressed onto the cable (JLCPCB C114117) and the
  SMT header 90814-0816 on the board (C17309979). 1.27 mm and feed-through, so a unit taps the
  cable anywhere along it; 30 mating cycles in tin, enough for assembly and repair; tin against
  tin, never against gold; 1.2 A a contact (Molex catalogue MX10, G-2 and G-4).
- **The band's strip** has one footprint of **36 ways**: on a module of the body the 32
  electrodes, the bias electrode, the strip's ground layers, one node, and a +5 V for a strip
  that carries followers, 35; on the head's the same 35; on the neck's the sixteen, the bias,
  the ground and the +5 V, 19, the rest empty (see [electrodes](CONSTRUCTION.md#electrodes) and
  [The strip's ground layer](#the-strips-ground-layer)). On the first arm, while the layout
  changes on a body, the strip goes into a **Hirose FH12**, a lever connector for
  flexible circuits, 0.5 mm, gold, 2 mm high, ~20 matings (Hirose's FH12 catalogue, 2017). In a
  series it is **soldered to the board** through plated holes at 1.27 mm in two staggered rows,
  ~23 × 3.5 mm for 36 ways against the FH12-36S's 22.1 × 5.6 mm, with a plain iron, and potted
  with the unit; a repair cuts the gel and unsolders.
- **The IMU buses** go out the same way, each on a polyimide strip of six leads, SCL, SDA,
  +3.3 V, ground, REF and a second ground: in a Hirose FH12-6S, a lever connector, on the first
  arm (JLCPCB C202118), soldered in a series (see [the IMU board](#the-imu-board)).

### The noise

One channel over its band, 10 Hz to ~500 Hz, at a gain of 12, with an 8 mm stud's moist contact
taken as 50 kΩ (the working figure, to be measured):

| source | noise | from |
|---|---|---|
| the ADS1298 | 0.8 µVrms | SBAS459K, table 3, 2 kSPS, 5 V and the 4 V reference, the high-resolution mode |
| the contacts and the resistors, 2 × (50 + 4.99) kΩ at 37 °C | 0.96 µVrms | √(4kTRB), computed |
| the steps, 39.7 nV / √12 | 0.01 µVrms | computed |
| **the electronics and the contacts together** | **~1.25 µVrms** | |
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
  (1 nA × 89 kΩ = 89 µV; the lead-off's excitation runs only in a check, never under the
  recording).
- **Measured on a sample, with no instrument:** the same channel on the body and with its inputs
  shorted inside the chip (MUX 001 in CHnSET, SBAS459K, 9.3.1.3.1) parts the skin's noise from
  the electronics'.

## The IMU

The IMU is **ST's LSM6DSV16X** (DS13510 Rev 4: up to ±16 g and ±4000 °/s, set to ±16 g and
±2000 °/s; I3C, I²C and SPI), LGA-14L, 2.5 × 3 × 0.83 mm, JLCPCB C5267406. It wins on a rate
held to the suit's clock as its own documents describe it, on the steadiness of its zero and on
its price:

- **A rate held to the suit's.** In its ODR-triggered mode the chip takes a reference on INT2 and
  aligns its data, in frequency and in phase, to the reference's edges (DS13510, 6.6; AN5763
  Rev 4, 3.3). The rates it takes then, ODRsel, are 12.5 Hz × 2ⁿ, and the real rate may lie up
  to ±33 % off the one set; at 800 Hz a reference period holds at least 32 samples and 40 ms
  (AN5763, table 15). The 800 Hz setting runs at **960 Hz,** +20 %, so the reference,
  **REF,** is **24 Hz,** 40 samples a period, 41.7 ms, or **15 Hz,** 64 samples, 66.7 ms: the
  suit clock ÷ 409,600 or ÷ 655,360, five or eight steps of 120 Hz a period. The samples a period
  are set in ODR_TRIG_CFG, in twos from 8 to 510, the edge by INT2_IN_LH, its pulse at least
  5 µs long, and the chip is locked four reference periods after REF starts, 167 ms at 24 Hz
  (AN5763, 3.3). The mode has the high-performance mode's noise (AN5763, 3.1 and 3.2) and leaves
  out the chip's sensor fusion, its pedometer, its DRDY mask and its EIS (3.3), none of which the
  suit uses.
- **A steady zero:** the gyro's offset drifts ±6 mdps/°C, typical (DS13510, table 3). With no
  magnetometer a joint's turn about the vertical rests on the zero between the moments at rest,
  so the drift weighs more than the noise: a warming of ~12 °C, the room to the skin, moves the
  zero 0.07 °/s, ~4.3° of heading a minute uncorrected, where ±20 mdps/°C would make ~14°. The
  noise, 2.8 mdps/√Hz, adds up as a random walk, ~0.02° a minute and ~0.02 °/s RMS in a step of
  120 Hz, far below any movement. Our calculation from the sheet's figures, the ~12 °C an
  estimate. The accelerometer 60 µg/√Hz in the high-performance mode (table 3).
- **960 Hz to 120 Hz.** The module sums each step's eight samples into the step's turn and
  mean force (see [software](SOFTWARE.md#the-imus-settings)); in noise that equals the chip's own
  filtering to 120 Hz, and it keeps the turn right in fast swings.
- **Its current,** 0.65 mA with both sensors on in the high-performance mode, at a VDD of 1.8 V,
  the sheet's condition (DS13510, table 4).

Its ±2000 °/s can be exceeded in a violent swing or throw; ordinary movement stays well within
it, and ±4000 °/s is a setting away (FS_G, CTRL6, DS13510 9.19). The Bosch BMI570 has lower
noise on paper, but we found no external clock input on it.

[Mamka](../mamka/README.md) describes the clocks for both the ADS1298 and the IMUs.

REF comes in on pin 9, INT2, through the IMU board's 10 kΩ (see [the IMU board](#the-imu-board)).
The chip takes it once it is set in the ODR-triggered mode, in the order AN5763 gives: both sensors
powered down, the samples a period, the mode, the edge, then REF started, then the rate (3.3; see
[software](SOFTWARE.md#the-imus-settings)). INT1 stays open and no unit takes an in-band interrupt
(DS13510, INT1_CTRL, 9.11): every IMU is read on its unit's schedule from REF, the module's as the
glove's and the sock's (see [the glove](#the-glove)).

### The IMU board

Each IMU sits on a small board of its own, on a bone or a phalanx, four layers like every board
here, the glove's too. It carries only what ST asks and two parts for the address and for REF,
~$3.40 a board:

| | part | JLCPCB |
|---|---|---|
| the IMU | ST **LSM6DSV16X**, LGA-14L | C5267406 |
| at the board's input | 1 µF 25 V X5R 0402, Samsung CL05A105KA5NQNC | C52923, Basic |
| at VDD and at VDDIO, one each | 100 nF 50 V X7R 0402, Samsung CL05B104KB54PNC | C307331, Basic |
| SDO/SA0 | 0 Ω 0402, to ground or to VDDIO | C17168, Basic |
| INT2 | 10 kΩ 0402, in series with REF | C25744, Basic |

- **The pins** (DS13510 Rev 4, table 2): 1 SDO/SA0 by the 0 Ω to ground or VDDIO, the address
  0x6A or 0x6B; 2 SDx and 3 SCx to ground, the analog hub and Qvar unused ("connect to Vdd_IO or
  GND"); 4 INT1 open; 5 VDDIO and 8 VDD 100 nF each, the sheet's "recommended 100 nF"; 6 and 7
  ground; 9 INT2 through the 10 kΩ to REF; 10 OCS_Aux and 11 SDO_Aux open, as the sheet allows; 12
  CS to VDDIO, I²C and I3C, so that noise cannot turn the chip to SPI; 13 SCL and 14 SDA the bus,
  no pull-ups on the board.
- **The 10 kΩ on INT2:** from power-on the chip holds INT2 as an output forced to ground (DS13510,
  table 23) until it is set as the trigger's input. REF is shared and driven by the processor, so
  an IMU reset while REF runs would fight the driver; 10 kΩ holds that to 0.33 mA, 8 mA for the
  glove's 24 where 1 kΩ would let 79 mA, and the
  firmware keeps REF low until every IMU on it is set. Our reading of the sheet, checked on the
  first board.
- **No filter on the supply:** 100 nF at each supply pin, as ST asks (table 2, note 2), and one
  1 µF at the input, 0.79 µF at 3.3 V by Samsung's typical curve. The IMUs' 3.3 V comes from the
  module's LDO behind its π filter, and the islands on the fingers want the room.
- **25 V or more** on every capacitor, by choice, though the board sees 3.3 V.
- **The connector:** the module's six ways, SCL, SDA, +3.3 V, ground, REF and a second ground, **one
  place a board** (the owner, 6 Nov 2026): a bus reaches its two IMUs by the strip's shape, a Y or
  two tails from the module's connector, drawn for its piece, so every IMU board is the same and
  every tail of a strip alike. On the first arm, while the layout changes, the strip's stiffened
  tail goes into the module's lever connector, the FH12-6S; in a series the strip is soldered to the
  board through plated holes and the board potted whole with the joint. On the fingers the boards
  are islands soldered to the finger strip (see [construction](CONSTRUCTION.md#the-glove)).
- **The fallback,** should the finger strip fail its bending test: Kyocera AVX **9175-700**
  IDCs, a 3-way and a 2-way, 2.5 mm pitch, 26–28 AWG, insulation 0.70–1.00 mm for 28 AWG, 1 A a
  contact, pottable (Kyocera AVX, *9175-700*, *9176-800*), with PTFE wire of 28 AWG, 19 × 0.08
  mm, MIL-W-16878/4 Type E, ~0.89 mm across (AWC, E28-19); PTFE does not wear through at the
  sides of the fingers as silicone would.

## Right-leg drive

The bias drive holds the body at the modules' mid-supply, so that the electrodes' common voltage
stays within the chips' input range, and it drains static from the body (SBAS459K, 9.3.1.7.6 and
10.1.2, the datasheet's right-leg drive, RLD). Its amplifier senses the common voltage of chosen
channels (RLD_SENSP, RLD_SENSN) and drives the body inverted, towards (AVDD + AVSS) / 2 = 2.5 V.

- **A lead of its own, with nothing in it but a resistor.** Every module has a bias electrode on
  a lead of its own: the first chip's RLDOUT, tied to its RLDIN, goes through 100 kΩ to it,
  not through the chip's multiplexer and through no switch. A second ADS1298's amplifier stays
  powered down, its RLDOUT and RLDINV open (see [Sensing module](#sensing-module)).
- **Every module can be the one, and the others are its spares.** The suit has 20 bias electrodes,
  one on every module near its band and one on each glove and sock, best over bone with little
  muscle under it (see [Bogatyr](../bogatyr/CONSTRUCTION.md#the-electrodes-rules)). Normally one
  module drives, PD_RLD on; the others have the amplifier powered down with PD_RLD, as the datasheet
  asks of all but one where there are several devices (9.3.1.7.6), and their electrodes hang on the
  powered-down outputs. Should a bias electrode come off, Baťa moves the drive to another module, by
  one register bit; never two drive at once (see [why](WHY.md#the-sensing-module)).
- **A powered-down output leaves its electrode alone,** which is all the switch was there for
  (see [why](WHY.md#the-sensing-module)): the datasheet's own bias lead-off check works with the
  amplifier powered down, a current source or a pull-up on the RLD pin pulling the electrode's
  node and a comparator reading it (9.3.1.7.5, figure 42), which can only hold if the
  powered-down output leaks far less than that. It is not a stated parameter; the first module
  confirms it with that very check, RLD_STAT through a 50 kΩ resistor.
- **All channels measure** on every module, the driving one too, so every input of every chip is
  an electrode: 496 in a suit of 16 modules.
- **The loop:** 1 MΩ ∥ 47 nF between RLDINV and RLDOUT, the resistor the datasheet's (figure 43,
  "typical values"), the capacitor ours, C0G, changed with a soldering iron. Each selected input
  reaches RLDINV through 220 kΩ (figure 43; the electrical table says "internal 200-kΩ", the
  figure's value taken), so the common-mode gain is Rf · N / 220 kΩ, our reading: with the driving
  chip's sixteen inputs summed (RLD_SENSP = RLD_SENSN = 0xFF), ~73 at DC; the capacitor puts the
  pole at 1 / (2π · 1 MΩ · 47 nF) ≈ 3.4 Hz, so the loop holds the body at mid-supply with a gain of
  only ~5 at 50 Hz. The body node has a pole of its own through the lead's 100 kΩ and the bias
  electrode's contact: with the strips' ground layers driven at the common mode, the default, the
  strips and their leads drop out of it and the chips' own 20 pF an input stay (SBAS459K, Electrical
  Characteristics), ~11 nF for the suit's 560, ~140 Hz at a 2 kΩ contact (a lead read on a sweaty
  hand, 5 Nov 2026, the way not recorded; 50 kΩ stays the working figure for the inputs until
  measured) and ~95 Hz at the datasheet's 51 kΩ; with the layers on ground every input's lead joins
  them, 560 × (20 + ~86) pF ≈ 59 nF before the strips' own capacitance to the skin, the pole at
  ~20–25 Hz. The two poles set the phase margin: ~35–40° with the layers driven, ~20° on ground
  (computed, the leads an estimate; see [The strip's ground layer](#the-strips-ground-layer)). The
  capacitor is tuned on a sample, module by module, between 22 nF (a gain of ~10 at 50 Hz, less
  margin) and 100 nF (~2, more); TI's forum warns the amplifier off large capacitive loads (E2E,
  *bias shield drive*, as the search summarised it).
- **The 100 kΩ** is there for a fault's sake, the datasheet's own "patient protection resistor" of
  figure 42; the drive's currents are nanoamps to a microamp (the inputs' bias currents, ±1 nA each
  at most, 560 of them), tens of millivolts across it at the worst, nothing against the chips'
  common-mode range. The lead-off check excites every P and N input together, so its currents cancel
  in the body and none returns through this lead; the P inputs alone would send ~1.7 µA through it
  at 6 nA and, through the resistors, ~70 µA, ~7 V (see
  [software](SOFTWARE.md#an-electrode-coming-off)). It also parts the amplifier's output from the
  capacitance of the lead and the body, against which an op-amp tends to ring, and it takes static.
  The amplifier itself gives 490 µA into a short to ground and 810 µA into one to the supply at a 5
  V AVDD, and has 100 kHz of gain-bandwidth (SBAS459K, Electrical Characteristics, the RLD
  amplifier), its own pole far above the loop's crossover. The datasheet leaves the loop's stability
  to the system (9.3.1.7.6).
- **Faults:** from outside the suit hardly any, see below. Inside, with one driver no direct
  current flows whatever its amplifier does: an output stuck at a rail takes the body to that
  rail, the inputs have 1 GΩ and their protection diodes open only ~0.6 V beyond the supply
  (the inputs then past their absolute maximum of AVDD + 0.3 V, SBAS459K 7.1, at microamps).
  Two drivers against each other do: their mid-supplies differ by the LDOs' tolerance, ~50 mV,
  which the gain of ~73 turns into outputs stuck at opposite rails, 5 V across two leads and two
  contacts, ~25 µA, under the 50 µA of direct current that IEC 60601-1 allows between two
  patient connections under a single fault (10 µA normally; the standard's table as Wall
  Industries' guide gives it, the standard itself not read).
  The cable's 6 V shorted onto the lead returns through the inputs' diodes with only
  the ~0.4 V over the supply, a few microamps; nothing above 6 V reaches the suit, the pack's
  14.6 V staying in the backpack. Two drivers are a firmware fault, and three things catch it:
  every module's PD_RLD read back with CONFIG3 once in 32 cycles, so Baťa sees two set (see
  [Porjadok](../porjadok/SOFTWARE.md#the-diagnostics)); the driving module's RLDOUT, tied to its
  RLDIN, measured into one channel (RLD_MEAS and MUX 010, SBAS459K 9.3.1.7.2, figure 34) at the
  start and every 30 minutes, no oftener, since the channel leaves its electrode and its filter
  settles meanwhile; and every channel's offset jumping at once. Baťa then turns the drive off
  and Storož halts the suit with its reason (see [Baťa](../bata/SOFTWARE.md#storož)).
- **Checks at start:** the bias lead-off check (SBAS459K, 9.3.1.7.5, figure 42). With the
  amplifier off (PD_RLD = 0) and RLD_LOFF_SENS = 1, a current source and a comparator on the
  RLD pin tell whether the electrode is connected: RLD_STAT 0 connected, 1 not. TI's figure
  draws the contact as 51 kΩ ∥ 47 nF and a protection resistor of 100 kΩ (our reading of it);
  our path is the same 100 kΩ, so the check works through the lead of its own as the datasheet
  draws it.
  Every module checks its own electrode before any drives, so every spare bias electrode is
  checked too, not only the one that will drive.
- **While it runs:** with the amplifier on the current source does nothing, but the comparator
  still watches the amplifier's output against the thresholds set by LOFF[7:5], the same as for
  the other inputs (9.3.1.7.5). A bias electrode that comes off drives the loop to a rail, and
  the driving module's RLD_STAT says so before the whole suit's channels saturate; the computer
  then moves the bias to another module.
- **The suit and the outside world:** a computer joins the suit only through an isolator or
  over the air (see [Baťa](../bata/SOFTWARE.md#output-modes)). The suit is not worn while it
  charges: a bought charger is not an isolator (see [Babuška](../babuska/HARDWARE.md#charging)).

**Differential everywhere** (the owner, 3 Nov 2026): each channel measures INnP − INnN, 8
channels of 16 electrodes a chip, on the head and the neck as on the body; no unit carries a
reference electrode (see [why](WHY.md#the-sensing-module)). EEG on the head stays an open trial,
by bipolar crossed pairs, its filters per channel on Baťa (see
[Bogatyr](../bogatyr/CONSTRUCTION.md#open-questions)).

## The strip's ground layer

The band's strip is a **four-layer flexible circuit, shielded on both faces:** ground on both
outer layers, the leads between them (see [construction](CONSTRUCTION.md#electrodes)). Vias
along both edges every few centimetres make the two grounds one node, with no fence of them; the
leads run a few tenths of a millimetre in from the edge (our estimate), and every stud has a
clearance round it. The layers are **driven at the body's common mode by default** and can be
put on the module's ground, and the strip can carry a follower at every stud: three levels, drawn
on one board and one strip, so that the first arm tries them all with no new board. The numbers
are estimates on a lead of 20 cm between the two grounds, ~86 pF, about twice the 43 pF one
ground gives at 2.2 pF/cm on 25 µm polyimide, the P and N leads of a pair differing by twice as
much as under one, with the contact at 50 kΩ ± 50 %: scaled from the one ground's figures, to
be measured on the sample.

| level | what it cures | what it leaves | what it costs |
|---|---|---|---|
| **(a)** the layers on ground, no parts | the room's fields, and the fabric's static and friction on both faces; the body's common mode turned into a difference by the unequal contacts, the potential divider (Metting van Rijn, Peper & Grimbergen 1990, eqn 3), ~14 µV pp at 10 mV pp of common mode before thin leads and the pairs side by side win part of it back | a bend of the lead moving charge off its 2.5 V against the layers, ~1 µV at 1 % of its capacitance in 100 ms; what the strip generates by itself | the strips' capacitance to the skin and the leads' in the bias loop, its pole at ~20–25 Hz and the margin ~20° (see [Right-leg drive](#right-leg-drive)) |
| **(b)** the layers driven at the common mode, the default: a TLV9001S on the first chip's RLDINV, gain 0.99 | what friction and static make outside lands on the layers, nanoamps through the driver's ~3 kΩ, microvolts, alike on P and N; the divider ~3 µV pp; the bend twenty-five times down, only the electrode's ~0.1 V of offset left on the lead; the strips out of the bias loop | what the strip generates | one op-amp, two resistors and a pin; the loop's stability by the 1990 rules |
| **(c)** a follower at every stud, its output on the lead | the divider to ~0.3 µV; the bend; what the strip generates, the current flowing into the follower's output | the skin under the electrode, which nothing on the strip cures | 32 op-amps a module of the body on the strip, potted with it; 1.9 mA (TLV9001) or 17 mA (TLV9061) a module; the noise 1.25 → ~1.6 (TLV9001) or ~1.35 µVrms (TLV9061), two followers' 30 or 16 nV/√Hz over 10–500 Hz added in quadrature; **the lead-off currents end at the follower: the chips' impedance check is lost** |

- **Won back on the strip:** the divider grows with the difference between a pair's two leads,
  so the leads are thin, 3 mil (JLCPCB's 3/3 mil on 12 µm copper), and P and N run side by side
  from where they meet, N's lead going the shortest way to P and on with it. No twist is
  needed: 0.152 mm apart over 20 cm is ~30 mm², ~0.01 µV at 1 µT and 50 Hz, 1 µT our pessimistic
  figure.
- **RLDINV, not RLDOUT.** RLDOUT carries the error inverted and amplified, ~73 times the
  residual common mode, so a layer on it would couple 74 times more than one on ground, inside
  the loop. RLDINV is where the chip averages the selected channels' common mode, from the PGA
  outputs through 220 kΩ each, loading no electrode (SBAS459K, figure 43). On a module whose
  amplifier is powered down RLDINV is its sixteen inputs' common mode at ~14 kΩ, the first chip
  summing them on every module for this (see [software](SOFTWARE.md#the-ads129xs-settings)); on
  the one driving module it is the amplifier's summing node, held at mid-supply, so its layers
  sit at a steady 2.5 V and the leads' 2.5 V against them is gone there too. One circuit on
  every module, nothing to switch when Baťa moves the drive. To check on the sample: that a
  powered-down RLDOUT is high-impedance, so the loop's 1 MΩ does not load RLDINV, which the
  datasheet does not say.
- **The driver:** a **TLV9001S** (SOT-23-6, SBOS833R: 60 µA; shut down by SHDN, 0.5 µA, its output
  10 GΩ ∥ 2 pF) as the follower on RLDINV, then a series resistor to the ground layers' way and a
  pull-down from that way to ground, ~3 kΩ and ~300 kΩ, 0603, changed with a soldering iron:
  together the attenuator for 0.99 and, with the layers' capacitance, a low-pass while the driver is
  on, and the plain ground while it is off, the coupled nanoamps making microvolts across 300 kΩ, a
  thousandth of that on the leads; a 0 Ω place across the 300 kΩ puts the layers hard on ground for
  (a) and (c), whose followers have no other way to ground on the strip. Metting van Rijn's rules
  (eqns 5–9): a guard at a gain under 1 is stable for any electrode, and flat when its time constant
  is about twice the electrode's and the lead's, 2 × 50 kΩ × 86 pF ≈ 9 µs, a low-pass at ~18 kHz;
  the layers' capacitance is measured on the sample and the resistor chosen for it. A driver cut off
  above ~1 MHz leaves the bias loop's stability alone, one at 10–100 kHz adds phase to it, so the
  two are tried side by side. SHDN on PA2 with its own pull-down of 4.7 kΩ against the chip's
  internal pull-up (SBOS833R, 8.5), the layers on ground from reset until the firmware drives them:
  register 0x03 of chip 0x00, 1 by default, set by Baťa in the service mode, so the two levels are
  compared on the arm by a register (see [software](SOFTWARE.md#the-ads129xs-settings)).
- **The followers** live on the strip alone: the first strip is drawn with a follower's place at
  every stud, bridged by a 0 Ω part, likely never fitted, and a +5 V trace from the connector's
  +5 V way, fed through 10 Ω from the module's analog rail, **the trace laid only on a strip that
  carries followers** and the way left unconnected on the passive strip: 5 V behind 10 Ω along a
  wet strip at the skin would pass over the 50 µA of a single fault through a leak of under ~100
  kΩ to a stud, so the passive strip has none, and on a follower strip the coverlay is the
  barrier and the wet strip's leakage from the trace to a stud is measured before it meets a
  wearer; a strip with the followers fitted is the next version of a part that is made by
  versions anyway. TLV9061 (X2SON 0.8 × 0.8 mm,
  0.5 pA, 16 nV/√Hz, 538 µA, its sheet) or TLV9001 (the same package, 5 pA, 30 nV/√Hz, 60 µA,
  SBOS833R), both to 5.5 V, the body at 2.5 V with ±0.3 V of offset inside a rail-to-rail
  output; the module sees no difference but the lead-off check gone. The +5 V trace runs on the
  leads' layer by the edge, never between two leads.
- **What decides,** with the module's own firmware and Baťa's recordings, in this order: the
  inputs shorted inside the chip (MUX 001), the floor; a dummy body, resistors of 50 kΩ from the
  strip's studs to one point, the strip bent, tapped and rubbed with the suit's fabric while
  recording, the driver on and off, which gives the strip's own artifact in microvolts with the
  skin out of it; then on the arm, still, moving, beside a mains cable, with the charger plugged
  in, fleece over the band, the band's pressure, the contact by the lead-off check, the driver on
  against off, 20 Hz against 10 Hz in software, one module's bias loop with the strips on and then
  three; last a strip with followers against the passive one on the same arm. **The rule:** the
  passive strip stays if its own artifact lies under the electronics' ~1.25 µVrms and on the arm
  it reads like the one with followers; the driver stays on unless the arm reads the same with
  the layers on ground and the bias loop holds without it, and then its parts are left off the
  next boards; the followers come only if the dummy body shows the strip generating, the
  impedance check given up with them.
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

- **One board, two sides.** On one side the ADS1298 with its inputs, as a module's first chip (see
  [Sensing module](#sensing-module)): the hand's **16 electrodes on 8 channels,** the bias electrode
  from its RLDOUT through 100 kΩ, the strip's ground layers and their TLV9001S on RLDINV (see [The
  strip's ground layer](#the-strips-ground-layer)), 4.99 kΩ a lead and 220 pF a channel, and the
  hand's strip, 20 ways: the sixteen electrodes, the bias, the ground and the +5 V, one spare, in a
  lever connector on the first glove and soldered in a series (see [Sensing
  module](#sensing-module)). On the other side Staršaja, the line's drivers and their Picoflex
  header, the Bratiški, the IMUs' three switches and SCL's gates with their pull-ups, the two LDOs
  and the six zones' joints. The board sits over the bases of the second and third metacarpals,
  which hardly move against the wrist (see [Bogatyr](../bogatyr/CONSTRUCTION.md#the-gloves)); its
  size is seen when it is drawn.
- **Its Staršaja,** the elder, is the module's own part, the **STM32H523CCU6 in UFQFPN48,** so
  that one processor serves the module and the glove, and she reads every IMU of the hand herself.
  Her 35 I/Os (DS14540 Rev 3, table 2) go round one way: the module's pin map, its line, its
  ADS1298's CLK and START and its DMA as they are, and six of its free pins setting the switches;
  29 I/Os in all, below. Beside her the line's drivers, a module's three
  THVD1450 (see [Porjadok](../porjadok/HARDWARE.md#drivers-on-a-unit)), and her LDOs,
  a TPS7A2033 and an LP2985-5.0 as on a module (see [power](#power)).
- **Her two I3Cs read every IMU of the hand,** I3C1 on PB6 and PB7, I3C2 on PB5 and PB4, as a
  module's, two IMUs on a path, 0x6A and 0x6B by SDO/SA0: each I3C's SDA is switched among **six
  branches** of two by **three TI TS3USB3031** side by side (SCDS348D; JLCPCB C2652459), never one
  behind another. Each chip has a lane on I3C1's SDA and one on I3C2's, one SEL0 and SEL1 for both,
  so the two buses move together. Its USB1 channel, SEL 00, where its internal 6 MΩ pull-downs hold
  it from power-up (SCDS348D, the SEL pull-downs in its application section), is left unconnected as
  its **park**; the branches are on USB2 (01) and MHL (10). A chip not in use sits on its park, so
  every change is a change of channel, 400 ns at most; the high-Z state (SEL 11), up to 100 µs back
  on (table 5.6), is never used. **24 places in six zones of four,** a zone a chip's lane on one
  I3C, its two branches and an SCL of its own: a finger a zone, the thumb with the board's own, and
  the sixth the carpal bones. Staršaja makes the IMUs' REF from the suit clock for the whole board,
  on PA8 (TIM1_CH1), so they sample in step with the suit.
- **SCL** goes to each zone through a plain gate of its own, always on, a non-inverting LVC buffer,
  three on each I3C's SCL: six SN74LVC1G34 (JLCPCB C2872902; ±24 mA at 3 V, tpd 4.7 ns at most into
  50 pF, SCES519O, 5.3 and 5.8), each beside its zone's connector, or two SN74LVC3G34, triples, one
  an I3C (C130024), chosen when the board is drawn, in the smallest package JLCPCB places, a BGA too
  (the owner, 7 Nov 2026); one kind either way, so one loading fee, and no Basic or Preferred part
  fits. A zone's SCL, four IMUs' pins and a finger's strip, is ~80 pF, its edge ~11 ns at 24 mA (an
  estimate). A branch not selected sees SCL with its SDA held high by its own pull-up, so no START.
  The gates' inputs float from reset until Staršaja drives them, so each I3C's SCL has 100 kΩ before
  them, the gates' leakage at most ±2 µA (SCES519O), 0.2 V across it; each output a place for 22–33
  Ω; the gate's delay counted in SDA_HD. Each branch's SDA has 2.2 kΩ at the IMUs' side, so that it
  idles high when switched away and pulls its branch up when selected, each common SDA an empty
  place: the open-drain rise ~190 ns against SCLL_OD's 344 ns (AN5879 Rev 7, 9.5.3; scaled from 1.5
  kΩ's ~127 ns, an estimate), the IMU sinking 1.5 mA of the 4 mA it holds at 0.2 V (DS13510 Rev 4,
  table 4); the values tuned with a scope on the first glove. Fourteen pull-ups, twelve on the
  branches and two on SCL.
- **The SDA path** while a branch is selected, her pin, ~3 cm of board, the three chips' lanes, a
  finger's strip to its tip and two IMUs: ~70 pF with 10 pF an IMU's pin (not given by ST; I²C's
  ceiling a pin, NXP UM10204 Rev 7.0, table 10), ~53 pF with the strip's ground hatched under
  it, ~60 and ~43 pF at 5 pF a pin. Its edge comes in time up to 8 MHz at the IMU's guaranteed
  4 mA, up to 10 MHz at 10 mA (assumed): the bus runs at 10 MHz, 8 should the scope say so
  (estimates, our calculation).
- **A round** of reads at 960 Hz, 1,041.7 µs: the six positions of the chips in turn, both I3Cs
  reading their branch's two IMUs together, 220 µs at 10 MHz (21 %), 311 µs at 6.25 MHz (30 %). The
  IMUs are read by Staršaja's schedule from REF, not on their IBI, which a branch switched away
  cannot raise, and each has a dynamic address of its own, so a branch wrongly selected answers
  nothing (see [software](SOFTWARE.md#the-glove)). The IMUs take ~16 % of her 49.152 MHz (250 cycles
  a read and 100 a sample's sum, estimates).
- **The Bratiški,** the little brothers, are this part of the board, set apart from the rest: the
  three switches, the gates and the fourteen pull-ups, beside the six zones' connectors. They
  take ~70 mm² of the board with their courtyards, routing not counted, and ~2.6 mA on 3.3 V, ~2.5
  of it SCL's switching (estimates).
- **24 IMUs in six zones:** each finger and the thumb a zone of two branches, A and B: a finger's A
  its proximal and middle phalanges, its B the distal and a place to spare, four spares: the
  third, fourth and fifth metacarpals' heads, where the palm's arch bends, on the middle, ring and
  little fingers' B, and a second on the thumb's metacarpal, because its skin slides, on the index
  finger's B; the thumb's A its metacarpal and proximal phalanx, its B the distal and
  the board's own, on the back of the hand; the sixth zone four over the carpal bones. Which are
  fitted, all 24, 12 or 8, the recordings decide, the unit's table telling Baťa (see
  [Bogatyr](../bogatyr/CONSTRUCTION.md#the-gloves)):

  | chip, channel | I3C1 | I3C2 |
  |---|---|---|
  | each chip, USB1 (00) | its park | its park |
  | A, USB2 (01) | the thumb's A | the ring finger's A |
  | A, MHL (10) | the thumb's B | the ring finger's B |
  | B, USB2 (01) | the index's A | the little finger's A |
  | B, MHL (10) | the index's B | the little finger's B |
  | C, USB2 (01) | the middle finger's A | the carpus's A |
  | C, MHL (10) | the middle finger's B | the carpus's B |

- **Each zone's strip** carries six wires, its SCL, the SDA of its A and of its B, REF, +3.3 V and
  ground, two IMUs a branch at 0x6A and 0x6B, the carpus's a short one; it joins the board in a
  six-way lever connector on the first glove and is soldered in a series, its IMU boards soldered
  along it as islands (see [the IMU board](#the-imu-board) and
  [construction](CONSTRUCTION.md#the-glove)).
- **Across the wrist** nothing crosses but the arm's line itself, the flat cable sewn in a loose
  loop over the wrist's ulnar side to the board's Picoflex header; the glove comes off it and its
  strips only for a repair, as a module does (see
  [Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit)).

**Staršaja's pins** in the glove are the module's, pin for pin (see
[Sensing module](#sensing-module)), so that every unit has one pin map and one DMA table (6 Nov
2026): the second chip's CS on PA15 and DRDY on PB10 are hers to spare, and six of the module's
free pins set the three switches, plain outputs:

| pin | name | use |
|---|---|---|
| 11 | PA1 | chip A's SEL0 |
| 13 | PA3 | chip A's SEL1 |
| 21 | PB10 | chip B's SEL0 |
| 26 | PB13 | chip B's SEL1 |
| 27 | PB14 | chip C's SEL0 |
| 45 | PB8 | chip C's SEL1 |

PA15 is not a SEL: JTDI's pull-up after reset (RM0481 Rev 5, GPIOx_MODER reset values) would lift
a SEL against the switch's own pull-downs and take its chip out of the park; it stays free with
PB15, PC13–PC15 and PH1. 29 of the 35 I/Os are used, the module's 25 less two and the six SELs.

**The glove's current,** an estimate on the 4 V rail, counted as the modules are, on the safe
side:

| consumer | current | source |
|---|---|---|
| Staršaja | counted as a module's processor, 53.3 mA typical, 84 mA at most | DS14540, table 26 (see [power](#power)) |
| the ADS1298, digital side | 0.5 mA | SBAS459K, Power Supply |
| the IMUs' switches and gates: three TS3USB3031, SCL's gates and switching | ~2.6 mA, an estimate | SCDS348D; SCES519O; our calculation |
| 24 LSM6DSV16X | 24 × 0.65 mA, both sensors on in the high-performance mode, 15.6 mA | DS13510 Rev 4, table 4 |
| the line's drivers, three THVD1450, their receivers on | ~3 × 2.4–3 mA, ~8 mA | SLLSEY3E, ICC |
| status LED | ~2 mA | estimate |
| the driver while it sends | ~37 mA, ~8 % of the time | estimate |
| **the glove, 4 V** | **~0.085 A on average, ~0.15 A at worst** | |
| the ADS1298's analog side and the TLV9001S, on 6 V | 3.1 mA and 60 µA | SBAS459K; SBOS833R |

### The sock

The sock is **Nosok**, Russian for a sock: the glove's board and firmware for the foot, a unit of
the glove's kind in its leg's fourth slot, after the hip's, the thigh's and the calf's modules,
with its own drivers and number (see [Porjadok](../porjadok/SOFTWARE.md)). The
board sits on the calf above the ankle, where the calf's module's strip crosses too, not on the
foot, which a shoe presses: the foot's **16 electrodes on 8 channels** come up on a strip across
the ankle, and its IMU strips go down to the foot, **up to eight IMUs** to start of the board's
24 places, in Staršaja's zones as the glove's, its table telling how many.
Where they sit is under [Bogatyr](../bogatyr/CONSTRUCTION.md#the-socks); the strips and the
layers under [construction](CONSTRUCTION.md#the-sock). Its current, counted as the glove's above
with eight IMUs, **~0.075 A on average, ~0.14 A at worst** on 4 V (an estimate).

## Power

A sensing module takes the suit's two rails, 4 V and 6 V (see
[Porjadok](../porjadok/HARDWARE.md#power)), and brings each down with one LDO:

| LDO | in | out | feeds |
|---|---|---|---|
| TI LP2985-5.0 | 6 V | 5 V | the ADS1298's analog side (AVDD, AVDD1) and the strip's driver |
| TI TPS7A2033 | 4 V | 3.3 V | the processor, the RS-485 drivers, the ADS1298's digital side (DVDD), the IMUs |

- **LP2985-5.0,** TI's LP2985-N (SOT-23-5, LP2985IM5X-5.0/NOPB, JLCPCB C5380652): input up to 16 V,
  150 mA, 30 µVrms of noise with a 10 nF bypass, 70 dB of ripple rejection at 1 kHz and 40 dB at 1
  MHz (SNVS018AB); 1 µF at its input beside the input's 10 µF, 10 µF at its output and the 10 nF
  bypass. It ships as a legacy chip or a new one, the reel's label telling: the legacy chip's ON/OFF
  at most VIN, so tied to it, its output at least 2.2 µF, ceramics within its ESR; the new chip's
  ESR up to 1 Ω (5.3, 7.1.1). Its dropout at 10 mA is 98 mV typical and 148 mV at most over
  temperature (Electrical Characteristics, the new chip), so going from 6 V to 5 V leaves room. The
  ADS1298's 4 V reference wants AVDD of 4.4 V at least (SBAS459K). TI's own front-end boards feed
  these chips from ordinary low-noise LDOs (ADS1298ECG-FE, SBAU171D); the π filters behind it take
  the converters' megahertz, where an LDO is weak.
- **TPS7A2033:** fixed 3.3 V, 300 mA, input 1.6–6 V, dropout at most 145 mV at 300 mA in the SOT-23,
  and its ±1.5% from an input of 3.6 V up (SBVS338H, 5.5), low noise without a bypass capacitor. 3.3
  V on DVDD also lets the chips be read at 20 MHz, an SCLK period of 50 ns at a DVDD of 2.7–3.6 V
  (SBAS459K, 7.6). From 4 V the cable, the filters and the connectors leave it at least ~3.66 V at
  the worst corner (see [Porjadok](../porjadok/HARDWARE.md#end-to-end)).
- **At the inputs,** where the cable arrives, an RC each, no polymer: a **22 µF 25 V X5R 1206**
  (Samsung CL31A226KAHNNNE, JLCPCB C12891, Basic) behind **0.5 Ω**, two 1 Ω 0603 side by side,
  beside the 10 µF; on the 6 V a 10 µF in its place, the suit's one 6 V converter otherwise past the
  ~300 µF TI's guidance allows. It damps the cable: a module plugged into a live line peaks at ≤
  4.52 V on 4 V, under the TPS7A2033's 6.5 V (SBVS338H, 5.1), and at ≤ 7.18 V on 6 V, under the
  LP2985's 16 V (SNVS018AB), computed for a line of 0.2–1.0 µH and 0.08–0.35 Ω (the 3M 3811 ~0.44
  µH/m, an estimate). An input holds ~26 µF, which each line's converter charges at start (see
  [Mamka](../mamka/HARDWARE.md#converters)); the driver's ~37 mA for ~30 µs, a frame of 58 B, takes
  ~42 mV from it. The 6 V branch draws a steady ~7 mA, so its RC stores nothing worth speaking of:
  it damps the cable and the π filter behind it. The glove and the sock take the same RC at their
  inputs.

**Budget of one module**

| consumer | rail | current | source |
|---|---|---|---|
| STM32H523 at 49.152 MHz in VOS1 | 3.3 V | counted as at 200 MHz in VOS0, for margin: 24.5–53.3 mA typical, 84 mA at most (TJ 105 °C); VOS1 itself gives 21.3–46.5 mA and 72 mA | DS14540, table 26 |
| ADS1298, 2, digital side | 3.3 V | 2 × 0.5 mA in the high-resolution mode; the neck's one 0.5 mA | SBAS459K, Power Supply |
| LSM6DSV16X, 4 | 3.3 V | 4 × 0.65 mA, both sensors on in the high-performance mode, given at a VDD of 1.8 V | DS13510 Rev 4, table 4 |
| THVD receivers, 3 | 3.3 V | ~2 mA each; 2.4 mA typical with no load, given at 5 V | TI |
| the driver while it sends | 3.3 V | ~37 mA more, ~2 V into the two 120 Ω terminations (~60 Ω; the datasheet tests with 54 Ω), ~8% of the time | estimate |
| status LED | 3.3 V | ~2 mA | estimate |
| ADS1298, 2, analog side | 5 V | 2 × 3.1 mA in the high-resolution mode; the neck's one 3.1 mA | SBAS459K, Power Supply |
| TLV9001S, the strip's driver | 5 V | 60 µA on, 0.5 µA shut down | SBOS833R |

That makes ~68 mA on average and ~133 mA at the peak on 3.3 V, well within the TPS7A2033's
300 mA, and ~7 mA on 5 V, the head's module too, ~4 on the neck's. The suit's totals are under
[Porjadok](../porjadok/HARDWARE.md#power).

The LDOs only do the coarse separation; the filters do the rest:

- Behind each LDO the supply splits into a star with one branch per consumer: on the 3.3 V
  LDO the processor, the RS-485 drivers, the ADS1298's digital side and the IMUs; on the 5 V
  LDO the ADS1298's analog side and the strip's driver.
- Every branch has its own π filter: capacitor, choke, capacitor.
- The ADS1298's supply is a trace of its own, not a poured plane.
- The filter parts are the house parts:

  | part | what it is |
  |---|---|
  | choke **SWPA252012S2R2MT** | 2.2 µH, shielded, 2.5 × 2.0 × 1.2 mm, DC resistance 0.17 Ω, self-resonance 69 MHz, saturation 1.85 A; JLCPCB C23894 |
  | ferrite bead **GZ2012D601TF** | Sunlord, 0805, 600 Ω ± 25 % at 100 MHz, DC resistance at most 0.30 Ω, 500 mA (Sunlord's GZ series sheet, the GZ2012 table); JLCPCB C1017, Basic |

- Every choke sits in a π filter of 10 µF 50 V X7R 1206 + 100 nF 50 V X7R 0603 on both sides,
  before it on the rail and behind it at the pins. 2.2 µH into 10 µF puts the corner at
  ~34 kHz, ~59 dB down at 1 MHz, where Mamka's converters switch; the choke's 0.17 Ω damps the
  pair to a Q of ~3–4. The rule: the supply must not drop by more than 0.1 V even at the
  highest peak.
- **The processor branch** has the bead in series with its choke. The choke sits on the LDO
  side, the bead next to the processor. The processor is the main source of high-frequency
  noise. Above its self-resonance a choke stops filtering, while a bead is resistive from
  about 100 MHz up and burns the noise off instead of storing it; at the converters' 1 MHz a
  bead is a few ohms and filters nothing, which is why it only ever stands behind a choke.
  Against a small ceramic capacitor (~0.3 Ω at 100 MHz, an estimate) 600 Ω gives roughly
  66 dB. The bead also keeps that noise off the 3.3 V that feeds the ADS1298 and the RS-485.
  - Drop: choke and bead together are at most 0.47 Ω. The STM32H523, counted as in VOS0 for margin,
    draws 24.5–53.3 mA typical at 200 MHz depending on the peripherals, up to 84 mA at TJ 105 °C,
    the most VOS0 allows (DS14540, tables 2 and 26). That makes 25 mV at 53 mA and 40 mV at 84 mA,
    under the 0.1 V limit.
  - The bead's impedance falls with DC current, so it needs current to spare.
  - Choke and bead can each resonate with the decoupling capacitors; check by simulation.
  - Behind the bead, local decoupling right at the VDD pins covers the processor's current
    spikes.

**From the ADS1298's datasheet,** for its three supplies, AVDD, AVDD1 and DVDD (SBAS459K,
section 11, Power Supply Recommendations):

- Bypass each supply with 1 µF and 0.1 µF ceramic capacitors; the π filters' 10 µF and 100 nF
  at the pins hold more.
- AVDD1 feeds the charge pump and carries transients at the CLK frequency: star-connect it to
  the AVDD pins, and AVSS1 to the AVSS pins.
- Return currents of the digital parts must not cross the analog return path.
- Where a board is subject to vibration, the VCAP1 capacitor should be non-ferroelectric
  (tantalum, or C0G/NP0): X7R and X5R are piezoelectric and turn vibration into noise. A suit
  moves, so this applies here. The datasheet also asks for C0G in the input filter's
  capacitors (section 12.1); the bias loop's 47 nF follows the same reasoning.
- Power-up (11.1, table 38): all digital and analog inputs stay low until the supplies have
  settled. Only then does CLK start; after tPOR (2¹⁸ CLK periods, 133 ms at 1.96608 MHz, counted
  only once CLK is present) and with VCAP1 above 1.1 V the ADS gets a reset. The module starts
  the timer output to the ADS CLK only once it runs on the suit clock (see
  [Porjadok](../porjadok/SOFTWARE.md#bring-up)), and the ADS supplies come up with the line
  before that.

## Open questions

- the pin map: checked against DS14540's pin and alternate-function tables (9 Oct 2026): every
  signal exists on its pin at the AF given, no pin or peripheral twice, and any GPDMA request
  goes to any of the 16 channels; PA2, PA15 and PB10, given on 29 Oct 2026 as plain GPIO and
  EXTI10, to be checked the same way; the clock tree (see [software](SOFTWARE.md#clocks)) and
  the DMA table (see [software](SOFTWARE.md#dma)), checked on the first board,
- the two chips in cascade on one SPI: the second's select on PA15, both reads within 24 µs, the
  second chip's DRDY against the first's, on the first board,
- the LSM6DSV16X held by REF: the 800 Hz setting at 960 Hz, REF at 24 against 15 Hz, the lock
  and the samples' place against the cycle; the 10 kΩ on INT2 against an IMU reset while REF
  runs; on the first board,
- I3C over a cable: try the length and the rate on a sample,
- the input circuit: confirm the values on a sample,
- the noise on the body against the inputs shorted (see [The noise](#the-noise)), with the
  contact's real impedance, for each kind of electrode; the LP2985's share of it, the inputs
  shorted inside the chip (MUX 001) against SBAS459K's table 3 on the first module (see
  [why](WHY.md#the-sensing-module)),
- the right-leg drive: the loop's stability and the summed channels, tuned on a sample, with the
  strips' ground layers driven and on ground, the capacitor between 22 and 100 nF, the lead's
  100 kΩ fixed by the fault current; the common-mode gain of ~73, our reading of figure 43; the
  body's common mode at 50 Hz measured, against the ~10 mV pp the levels are reckoned on; one
  driving module for the whole body, checked as the modules are added,
- the bias check's comparator threshold and current (LOFF), set on a sample,
- a powered-down bias amplifier's output with an electrode on it, which the datasheet does not
  state: confirmed on the first module by the bias lead-off check through 50 kΩ, the switch
  having gone on the strength of that check,
- the strip's ground layers: driven, on ground and with followers, the three levels on the first
  arm in the order [The strip's ground layer](#the-strips-ground-layer) gives; the leads'
  capacitance to the two grounds and a pair's difference, measured; the four-layer strip against
  two layers with JLCPCB's shielding film on the skin's side,
- the IMU board: the strip's tail in the lever connector on the first arm, and the strip soldered
  and potted in a series, bent and pulled,
- the glove: Staršaja's pins above checked against DS14540's tables 14 and 15, the board's size and
  its place on the back of the hand with the hand's strip, the zones' strips' six wires in their
  connectors; the carpus's four places, whether IMUs on its skin follow its bones or the skin
  sliding over them; the IMU's SDA pin capacitance and drive on a scope, which set the bus's clock,
  10 MHz or 8; the switches' change of channel between reads, and the branches switched away quiet;
  the sock: the foot's strip across the ankle and its IMU strips; the IMUs' addresses by SDO/SA0 and
  a dynamic address an IMU by SETDASA, branch by branch, tried on the bench,
- the module and the glove's Staršaja at 49.152 MHz: their currents, and the glove's SCL
  switching, measured.
