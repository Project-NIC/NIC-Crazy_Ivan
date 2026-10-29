<div align="center">

# Rubaška: software

**What the sensing module's firmware does:** the ADS129x's settings, the IMUs', the glove and
the sock, and the rules from the errata.

↑ [Rubaška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

The module's firmware is C with no operating system, like every unit's
([Porjadok](../porjadok/README.md#firmware)). Its cycle, the frame it sends and how it reads its
chips are described under [Porjadok](../porjadok/SOFTWARE.md#the-frames); its registers and its
table under [the registers](../porjadok/SOFTWARE.md#the-registers); the start of a measurement under
[Starting a measurement](../porjadok/SOFTWARE.md#starting-a-measurement). This page holds what is
the module's own.

## The ADS129x's settings

A module of the body carries two ADS1298, chips 0x01 and 0x06, the head's two ADS1299 at the same
numbers, the neck's one ADS1299, chip 0x01 (see [hardware](HARDWARE.md#sensing-module)); the
firmware tells them by the ID register and keeps a table of values for each.

- **The clock and START** come from TIM3, the suit's clock ÷ 5 (1.96608 MHz) and START
  held high for the whole active mode; the CLK output stays low until the ADS supplies are up
  (see [hardware](HARDWARE.md#power), *From the ADS129x datasheets*). A module's two chips share
  both; on an ADS1299 START goes high 511 CLK periods later than on the body's ADS1298, 255 at
  3,840 SPS, so that every chip's first DRDY falls together (see
  [Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement)).
- **The reads:** the two chips in cascade on SPI1, DIN, DOUT and SCLK shared, the first's chip
  select the SPI's NSS on PA4, the second's a plain pin, PA15; at DRDY the first is read, then
  the second, 216 bits each (SBAS499C, 10.1.4.1).
- **Settings come from Mamka** as writes to the chips 0x01 and 0x06 (see
  [Porjadok](../porjadok/SOFTWARE.md#the-commands)). The module carries them out between two
  reads, SDATAC, WREG, RDATAC, and answers with the result; it knows nothing of what they mean,
  beyond the switches that go with them (below).
- **The bias drive** (see [hardware](HARDWARE.md#right-leg-drive)): the first chip's amplifier,
  on the driving module PD_BIAS on and BIAS_SENSP = BIAS_SENSN = 0xFF, on every other module
  powered down, its output then leaving the bias electrode alone; a second chip's amplifier is
  always powered down. Baťa picks the module, by register 0x00 of its chip 0x00, which sets
  PD_BIAS.
- **The bias electrodes checked at start,** one module at a time: CONFIG3 = **0xEA** (the
  amplifier off, BIAS_LOFF_SENS = 1), CONFIG3 read back, bit 0 being BIAS_STAT (0 connected).
  Baťa then picks a module whose bias electrode is connected; while it drives, CONFIG3 = 0xEE
  keeps BIAS_LOFF_SENS on, and its BIAS_STAT going to 1 means the drive has run to a rail (see
  [hardware](HARDWARE.md#right-leg-drive)). The module reads CONFIG3 back once in every 32 cycles
  and puts BIAS_STAT in the diagnostics (see [Porjadok](../porjadok/SOFTWARE.md#the-diagnostics));
  Baťa passes it on in the electrodes' meta packet.
- **The strip's ground layer,** register 0x03 of chip 0x00: 0 on ground, the TLV9001S shut down
  by PA2 low, 1 driven at the common mode of the first chip's BIASINV, PA2 high (see
  [hardware](HARDWARE.md#the-strips-ground-layer)). After a reset PA2 is low.
- **Two ways of measuring on the head and the neck,** whose ADS1299s have SRB1 and a reference
  electrode, the head's two chips sharing one (see [Bogatyr](../bogatyr/README.md)): differential
  with MISC1 = 0x00; or against the reference with MISC1 = 0x20, the chip's own switch joining SRB1
  to the channels and cutting the INnN pins off (SBAS499C, figure 18). Baťa picks the way by writing
  MISC1, the same to both of the head's chips. The body's ADS1298 have no SRB1 and measure
  differentially.

**The ADS1298's registers,** from SBAS459K section 9.6 (table 16 and the registers after it),
with the suit's values. Once the suit is tuned these are expected to stay as they are; the way to
change them while running is there so that nothing has to be rebuilt, not because they will
change.

| address | register | value | why |
|---|---|---|---|
| 0x00 | ID | read | bits 7:5 DEV_ID 100 for the ADS1298, bits 2:0 010 for eight channels (9.6.1.1) |
| 0x01 | CONFIG1 | **0xC4**; **0xC3** to try | HR = 1, the high-resolution mode; DAISY_EN = 1, multiple readback, the chips in cascade; CLK_EN = 0; DR = 100, fMOD / 256 at fMOD = fCLK / 4: 491,520 / 256 = **1,920 SPS**, or DR = 011, fMOD / 128, **3,840 SPS** (9.6.1.2) |
| 0x02 | CONFIG2 | **0x00** | the test signal off, bits 7:6 and 3 written 0 as asked (9.6.1.3) |
| 0x03 | CONFIG3 | **0xE8**, the driving module's first chip **0xEE**, **0xEA** for the bias check at start | PD_REFBUF = 1, the internal reference buffer on; bit 6 = 1 as required; VREF_4V = 1, the reference 4 V from AVDD 5 V; RLDREF_INT = 1, the mid-supply made inside; PD_RLD = 1 only on the chip that drives the body; RLD_LOFF_SENS = 1 on it, and on each module's first chip in turn for the check at start (9.6.1.4) |
| 0x04 | LOFF | **0x00** | threshold 95 / 5 %, the current source, 6 nA, DC; 24 nA is 0x0C; the threshold is picked by testing (9.6.1.5) |
| 0x05–0x0C | CH1SET–CH8SET | **0x60** | on, gain 12 (110, the ADS1298's code; 0x50 would be gain 8), MUX 000 the electrode, on every chip; the bias has a lead of its own (9.6.1.6) |
| 0x0D, 0x0E | RLD_SENSP, RLD_SENSN | the driving chip **0xFF**, others **0x00** | the sum of all sixteen inputs of the first chip (9.6.1.7) |
| 0x0F, 0x10 | LOFF_SENSP, LOFF_SENSN | **0xFF** | lead-off on every input |
| 0x11 | LOFF_FLIP | **0x00** | the current's polarity as the datasheet has it |
| 0x12, 0x13 | LOFF_STATP, LOFF_STATN | read only | they come in the status word of every read, and go in the diagnostics |
| 0x14 | GPIO | **0x0F**, the reset value | GPIO1–4 as inputs; on the board they are tied to DGND |
| 0x15 | PACE | **0x00** | no pace detection |
| 0x16 | RESP | **0x00** | no respiration circuit, the ADS1298R's |
| 0x17 | CONFIG4 | **0x02** | continuous conversion; PD_LOFF_COMP = 1 means the lead-off comparators **enabled**, despite the bit's name (9.6.1.11) |
| 0x18, 0x19 | WCT1, WCT2 | **0x00** | the Wilson central terminal's amplifiers off |

The 25 registers 0x01 to 0x19 go in one frame of 34 B.

**The ADS1299's registers,** the head's and the neck's, from SBAS499C section 9.6 (tables 11 to
28), where they differ: CONFIG1 **0xD3** (bit 7 = 1 and bits 4:3 = 10 as required; DAISY_EN = 1;
DR = 011, fMOD / 512 at fMOD = fCLK / 2: **1,920 SPS**; **0xD2**, DR = 010, 3,840 to try, table
13); CONFIG2 **0xC0** (the test signal off, table 14); CONFIG3 as the ADS1298's, its bits 6:5 =
11 as required and the reference 4.5 V (table 15); CH1SET–CH8SET **0x50** (gain 12 is the code
101 there, SRB2 open, table 17); BIAS_SENSP, BIAS_SENSN as RLD_SENSP, RLD_SENSN, and against the
reference BIAS_SENSN **0x00**, only the P sides summed, a choice of ours (tables 18, 19);
LOFF_SENSN **0x00** against the reference, the N pins standing idle; MISC1 (0x15) **0x00**, or
**0x20** against the reference, SRB1 to every channel's inverting input (table 26); MISC2 (0x16)
0x00; CONFIG4 (0x17) **0x02** (table 28); no PACE, RESP or WCT. Its 23 registers 0x01 to 0x17 go
in one frame.

**1,920 SPS, and 3,840 to try.** 1,920 is the professionals' rate for surface EMG, Delsys'
Trigno 1,926, Meta's band 2,000, OT's 2,048, and the band SENIAM recommends is 10–500 Hz: the
filter's −3 dB lies at ~503 Hz on the suit's clock (SBAS499C, table 1, 0.262 of the rate). 3,840
is the setting to try, CONFIG1 0xC3 and 0xD2: the band to ~1 kHz, for twitches a trained eye
might want to see whole, at twice the data and processor 1's SPI at 84 % with two chips a module
(see [Porjadok](../porjadok/SOFTWARE.md#into-baťa)); the step then counts 32 samples instead of
16. The rate is set only before the first start, since a write of CONFIG1 resets the digital
filter (SBAS499C, 9.4.2); why 3,840 is not the rate is under [WHY](WHY.md#the-sensing-module).

**Gain 12, not 24.** A channel takes ±VREF / gain, ±333 mV at a gain of 12 on the ADS1298's 4 V
reference and ±375 mV on the ADS1299's 4.5 V, and the electrodes' DC offset takes its share of it
(see [Construction](CONSTRUCTION.md#electrodes)); 24 would leave half. The noise at the 2 kSPS
setting and a gain of 12 is 0.8 µVrms on the ADS1298 (SBAS459K, table 3, 5 V and the 4 V
reference) and 0.46 on the ADS1299 (SBAS499C, table 3), against EMG of tens of microvolts and
more. The common-mode range narrows as a channel's input grows (SBAS499C, equation 4: AVDD −
0.2 V − gain · V / 2 > CM > AVSS + 0.2 V + gain · V / 2): with 300 mV across a channel at a gain
of 12 the body may sit anywhere from 2.0 to 3.0 V, and the bias drive holds it at 2.5 V; at a
gain of 24, 176 mV would leave only 2.31 to 2.69 V. The gain is one for the whole suit, as
Baťa's scale assumes (see [signals](../bata/SIGNALS.md#the-emg-channel)), the scale by the chip's
reference.

**At start,** after the datasheets' own sequence (SBAS499C, 10.1.2, figure 67): a chip wakes in
RDATAC, so first SDATAC; then CONFIG3 with PD_REFBUF and a wait for the internal reference to
settle; then the registers of 0x01 on as they came in one frame, written by two WREGs around the
read-only LOFF_STATP and LOFF_STATN, and an RREG of all of them back, compared with what was
written; only then START and RDATAC, the second chip the same after the first. The sequence of
the whole suit's start is under [Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement).
**Asleep** in the service mode the chips are in standby, by their STANDBY command, and wake by
WAKEUP (see [Porjadok](../porjadok/SOFTWARE.md#bring-up)).

## An electrode coming off

The ADS129x itself reports an electrode that has come off. It will rarely happen, but since
the chip can do it, we use it (SBAS499C, 9.3.2.4.3; SBAS459K, 9.3.2.4.3). We use dc detection
with the internal current source:

- The ADS drives a small current into the inputs: the ADS1299's 6 nA, 24 nA, 6 µA or 24 µA, the
  ADS1298's 6, 12, 18 or 24 nA (±20 %). One side of the channel is pulled towards the supply,
  the other towards ground.
- While the electrode holds, the current flows through the skin and the voltage stays small.
  When it comes off, the input runs to the supply and the channel saturates. Data keep coming,
  only at the end of the range.
- A comparator on every input (threshold COMP_TH, accurate to ±30 mV) then tells which
  electrode came off: bit n − 1 of LOFF_STATP belongs to input INnP (bit 0 is IN1P), and
  likewise LOFF_STATN to the INnN inputs. One bit is one physical electrode.
- The bits are valid only for channels enabled in LOFF_SENSP and LOFF_SENSN.
- Both bytes go in the diagnostics, turned over to 1 for an electrode on the skin and held at 0
  for the 32 samples once an electrode was off; see
  [Porjadok](../porjadok/SOFTWARE.md#the-diagnostics). What it means is Baťa's to judge.

The current flows through the electrode and the skin and adds a small constant offset to the
measured signal. Only the nanoamp settings are usable: through a contact of 50 kΩ, 6 µA would
already make 0.3 V, most of the range at a gain of 12, and 24 µA 1.2 V, far beyond it. We will
pick between 6 and 24 nA, and the comparator threshold, by testing.

## The IMUs' settings

- **1,920 Hz, summed to 120 Hz:** CLKIN at 38,400 Hz makes the ICM-45686's rates 1.2 times the
  setting, by our inference (see [hardware](HARDWARE.md#the-imu)), so the 1.6 kHz setting runs at
  1,920 Hz, sixteen samples to one step of 16 ADS samples at 1,920 SPS (1/120 s), 32 at the 3,840
  to try, the same step; the module tells the step's length from CONFIG1. It sums each step's
  sixteen samples (below) and sends 12 B per IMU per step, as a 120 Hz sample would take.
- **Over I3C,** two to a bus, each given its I3C address from its static one, 0x68 or 0x69, by
  SETDASA (DS-000489, 9.2 and 9.3; see [hardware](HARDWARE.md#sensing-module), *The IMUs on
  I3C*).
- Each IMU's 12 B go out after the step, 4 B a frame, placed by the frame's number
  ([Porjadok](../porjadok/SOFTWARE.md#a-units-data)).

**The registers,** from DS-000489 Rev 1.1 (16 for bank 0, 19 for IPREG_TOP1, the SYS1 and SYS2
banks after it, 13 for the indirect access) and TDK's own driver, motion.arduino.ICM45686
release 1.1.9, for what the sheet leaves out. Bank 0 is addressed directly; an **IREG**, a
register of the other banks, by its 16-bit address: IREG_ADDR_15_8 (0x7C), IREG_ADDR_7_0 (0x7D)
and IREG_DATA (0x7E) written in one burst, one IREG at a time, at least 4 µs between two
(13.2–13.4). Where a register also holds fields left at their reset values, only the field is
given, and the write is a read-modify-write.

| address | register | value | why |
|---|---|---|---|
| 0x72 | WHO_AM_I | read, **0xE9** | the chip's identity (16.79) |
| 0x7F | REG_MISC2 | SOFT_RST = 1, once | a soft reset at the start; 1 ms, then RESET_DONE read in INT1_STATUS0 (TDK's driver, `inv_imu_soft_reset`) |
| 0x31 | IOC_PAD_SCENARIO_OVRD | **0x06**: PADS_INT2_CFG_OVRD 1, PADS_INT2_CFG_OVRD_VAL 2 | pin 9 is CLKIN (TDK's driver, `inv_imu_adv_set_int2_pin_usage`; not in DS-000489 Rev 1.1) |
| IREG 0xA258 | SMC_CONTROL_0 | ACCEL_LP_CLK_SEL = 1 | wanted before RTC_MODE (AN-000478, 7.3, as ArduPilot's pull request 34904 quotes it; 19.47); TEMP_DIS stays 0, the temperature sensor on |
| IREG 0xA268 | SIFS_I3C_STC_CFG | I3C_STC_MODE = 0, as at reset | I3C's timing control and CLKIN share one interpolator, the former first (TDK's driver, `inv_imu_adv_enable_clkin_rtc`) |
| IREG 0xA4A6 | IPREG_SYS1_REG_166 | GYRO_SRC_CTRL = 10 | the gyro's interpolator and FIR on, which CLKIN wants (the same) |
| IREG 0xA57B | IPREG_SYS2_REG_123 | ACCEL_SRC_CTRL = 10 | the same for the accelerometer |
| 0x26 | RTC_CONFIG | RTC_MODE = 1 | the chip on the external clock (16.37) |
| 0x1C | GYRO_CONFIG0 | **0x15** | ±2000 °/s (GYRO_UI_FS_SEL 0001); GYRO_ODR 0101, the 1.6 kHz setting, **1,920 Hz** under CLKIN (16.27); 0x19, the 100 Hz setting, for the chip's own 120 Hz |
| 0x1B | ACCEL_CONFIG0 | **0x15** | ±16 g (ACCEL_UI_FS_SEL 001); ACCEL_ODR 0101, 1,920 Hz under CLKIN (16.26); 0x19 for 120 Hz |
| IREG 0xA4AC | IPREG_SYS1_REG_172 | GYRO_UI_LPFBW_SEL = 011 | the gyro's filter at ODR / 16, ~120 Hz under CLKIN; for the chip's own 120 Hz 001, ODR / 4, ~30 Hz |
| IREG 0xA583 | IPREG_SYS2_REG_131 | ACCEL_UI_LPFBW_SEL = 011 | the same for the accelerometer |
| 0x16 | INT1_CONFIG0 | **0x84** | reset done kept, the UI's data ready on (16.21) |
| 0x10 | PWR_MGMT0 | **0x0F**, written last | gyro and accelerometer in Low Noise mode (GYRO_MODE 11, ACCEL_MODE 11, 16.17); the gyro's data trusted 35 ms after, its start-up time (table 1) |

- **What is read:** 12 B from 0x00, ACCEL_DATA_X to GYRO_DATA_Z, little-endian as the chip gives
  them by default (DS-000489, 14), at every sample, 1,920 a second per IMU, 92 kB/s for four on
  the two buses, ~6 % of I3C SDR; the temperature at 0x0C–0x0D now and then into the
  diagnostics, °C = TEMP_DATA / 128 + 25 (table 4). The FIFO is not used: every sample is fetched
  as it comes, on the IBI or by polling.
- **The sum,** what the 12 B per step carry, strapdown integration as Movella's MTw does it on
  the sensor at 1,000 Hz (its white paper, *Strap-Down Integration*): the turn over the step,
  Δθ = Σ ωᵢ Δt + ½ Σ (θᵢ₋₁ × θᵢ), the sixteen rate samples summed with the two-sample coning
  term, which the plain sum of rates leaves out when the piece turns about two axes at once;
  and the mean specific force over the step, Σ aᵢ / 16, no sculling term, since nobody
  integrates velocity. Both go out as three i16 each in the raw scale of ±2000 °/s and ±16 g,
  Δθ divided by the step, so a reader may take them as a 120 Hz sample of the gyro and the
  accelerometer and be right to first order. A cross product and two sums a sample, a few
  dozen instructions, in the module's own time; sixteen a step, so the mean is a shift.
- **The chip's own 120 Hz** stays as a mode, set by register 1 of the module's chip 0x00: the
  100 Hz setting (0x19) and the filter at ODR / 4, the raw sample as it comes. It is the fallback
  should the IMUs ever talk I2C at 400 kHz on I3C2, where 1,920 Hz would not fit the bus, and the
  way to compare the two on recordings.
- **The order:** the soft reset; pin 9 as CLKIN; ACCEL_LP_CLK_SEL; the interpolators; RTC_MODE;
  the ranges and rates, the filters, INT1; PWR_MGMT0 last.
- **A choice, not a datasheet value:** the filter at ODR / 16 under the sum. In noise the two
  modes come out alike, the chip's filter or the sum of sixteen; the sum keeps the turn right in
  a fast swing, where a step of 8.3 ms taken as one rotation is off by up to ~0.05° a step at
  300 °/s about two axes, a few degrees by the end of the swing, and at 0.52 ms far less (an
  estimate from the coning term, not a datasheet value). To be judged on recordings.
- **The ICM-42688-P,** should the same board carry it (see [hardware](HARDWARE.md#the-imu)),
  takes its own registers from DS-000347, its 1 kHz setting at 1,200 Hz and ten samples a step,
  and °C = TEMP_DATA / 132.48 + 25 (14.5); the unit knows it by WHO_AM_I, 0x47 at 0x75, and its
  table names the part. Its register table is written should it be fitted.
- **Asleep** in the service mode the IMUs go to sleep, PWR_MGMT0 with the gyro and the
  accelerometer off, and come back with the order above.

## The glove

The glove, Vešč, is a unit of its own on its arm's line, in the fourth slot: one board on the back
of the hand with one ADS1298, Staršaja and four Bratiški (see [hardware](HARDWARE.md#the-glove)
and [Porjadok](../porjadok/SOFTWARE.md#the-bratiški)); the sock, Nosok, is the same board and
firmware in a leg's fourth slot:

- **Its frame of data** is **0x25, 58 B:** its ADS1298's eight channels in bytes 4–27 as a
  module's first chip's, and its IMUs' steps in the 28 B after them, bytes 28–55: the glove's 20
  IMUs, 240 B, in the frames 0–8 of the 16 after each step, zeros after them, a sock's eight in
  four (see [Porjadok](../porjadok/SOFTWARE.md#a-units-data)); Staršaja's own four first, read on
  her I3C buses as a module reads its (see [the IMUs' settings](#the-imus-settings)), then each
  Bratiška's in her table's order. Its diagnostics are a module's with one chip, ones for the
  second's eight, the IMUs' temperatures by turns, six a frame, the 20 in four.
- **Staršaja runs a module's firmware** for her line and her chip: she gets *get ready* and
  *start* as every unit, keeps the cycle from her ADS1298's DRDY and reads it as a module reads
  its first chip; what a module does for its second chip she does for the Bratiški. Her line is a
  module's too, one sender and two receivers, the master on USART1's RX and the echo on the
  LPUART's (see [hardware](HARDWARE.md#the-glove)).
- **The Bratiški are her chips,** 0x07–0x0A, not units: they have no number and answer no frame
  of Mamka's. A write to one of a Bratiška's IMUs, 0x14 on, she passes to him on his U(S)ART as a
  frame of 8 B with the chip made his own, 0x10–0x13, and sends his result up; a write to every
  IMU (0x0F) she passes to all four. His own registers: 0x00 his state, read only, 0 silent, 1
  running, 2 in the bootloader; 0x01–0x02 his firmware's version.
- **The CLKIN** for every IMU of the glove is Staršaja's, made from the suit clock on her TIM1 as
  a module's, on a trace to every strip and to each Bratiška's TIM2, so the IMUs sample in step
  with the suit; a Bratiška runs on his own HSI and only reads them.
- **With the glove unplugged** the fourth slot stays empty; plugged back, it joins at the next
  bring-up, as any unit that has reset, answering *discover* by its own UID.

### The Bratiški

Each Bratiška reads his finger's IMUs, two on each of his two I3C buses, sums each one's sixteen
samples into a step as a module does (see [the IMUs' settings](#the-imus-settings)) and sends
Staršaja the step on his USART2, PA5 and PA15, full duplex at **4 MBd**, 8N1 (see
[hardware](HARDWARE.md#the-glove)); on her U(S)ART to him she sends what he is owed at any time,
the link being full duplex. His time is the CLKIN's: he counts it on TIM2, 20 periods a sample
and 320 a step, from her *start* on his link, which carries the first cycle's number as Mamka's;
his HSI sets only the bit rate.

- **In the service mode,** to the first *start*, he answers her frames: the settings for his IMUs
  as writes of 8 B, chips 0x10–0x13, and the reads of his registers.
- **In the active mode** he sends the step just ended, so that she has it within 0.2 ms of the
  step's end, as a module has its own, long before the first frame that carries it, in the slot of
  the next cycle; a write for his IMUs may come down meanwhile.
- **The step,** 52 B, one length always:

| bytes | what |
|---|---|
| 0 | bits 3–0 which of his four IMUs answer, a bit an IMU; bits 7–4 zero |
| 1 | the step's number from *start*, mod 256: round in 2.1 s |
| 2–49 | the four IMUs' steps, 12 B each as a module's, zeros for one that does not answer |
| 50–51 | CRC-16/CCITT-FALSE |

- Nothing in it says which Bratiška: the U(S)ART it comes on does.
- **A step missing** from his link, or failing its CRC: Staršaja puts zeros for his IMUs in her
  frame of data, her diagnostics show them missing and his bit among her chips 0, and she sends
  him *start* once a second until his steps come back. A Bratiška that hangs is reset by his own
  IWDG, started by hardware as on every unit (see
  [Porjadok](../porjadok/SOFTWARE.md#watchdogs)); he sets his IMUs as after any reset and waits
  for her *start*. One that stays silent she resets herself, the four together, on their shared
  NRST line.
- **His firmware comes through her.** Mamka broadcasts an image of kind 3 as any (see
  [Porjadok](../porjadok/SOFTWARE.md#updating-firmware)): *begin* with the kind 3 tells Staršaja
  the blocks are her Bratiški's, and she keeps them in RAM, 64 KB at most, one window, her map at
  0x90 showing them as a unit's own. At *check and restart* she checks the CRC-32 at the image's
  end, raises the BOOT0 line, resets the four, and programs each over his USART2 through ST's
  bootloader (AN3155 Rev 22: 8 bits, even parity, the rate found from the first byte, 0x7F, at
  115,200 Bd; *Extended Erase*, *Write Memory* in 256 B, *Read Memory* to check it back), ~15 s
  for the four at once, an estimate, her state 6 meanwhile; then lowers BOOT0, resets them again,
  and the new image runs. His flash holds one image, no second bank and no trial: one that fails
  she shows in her state, 5, and programs again at the next *check and restart*, no SWD needed,
  ever. A Bratiška that comes empty from the assembler waits in the bootloader, his state 2, and is
  programmed the same way the first time.

## Clocks

By the suit's clock tree (see [Porjadok](../porjadok/SOFTWARE.md#the-clock-tree)): the core at
49.152 MHz, PLL1P ÷ 8, in VOS1, the line's USARTs on PLL3 Q. **The module** adds:

| what | setting |
|---|---|
| SPI1 to the ADS129x | PLL1Q ÷ 5 (field 4): 78.6432 MHz, SPI1SEL = 000 (RCC_CCIPR3, 11.8.42), the SPI's own ÷ 4: 19.66 MHz, under the 100 MHz kernel limit of VOS1 (DS14540, table 20) and the chips' 20 MHz; the first chip's select the NSS on PA4, the second's PA15 by software |
| USART1 and UART4, the line | PLL3 Q, 196.608 MHz, USART1SEL and UART4SEL = 010 (RCC_CCIPR1, 11.8.40); OVER8 = 1, BRR = 0x0012: 19,660,800 Bd |
| I3C1, I3C2 | the APB clocks, I3C1SEL and I3C2SEL = 00 (RCC_CCIPR4, 11.8.43): 49.152 MHz |
| TIM3, the ADS129x | PSC = 0, ARR = 24: CH3 in PWM at CCR3 = 12, the CLK at 1.96608 MHz, high for 12 of its 25 counts, the datasheets giving its period only, 414–666 ns (SBAS499C, 7.6; SBAS459K, 1.94–2.25 MHz); CH4 takes START high at count 18, the middle of the CLK's low half, on an ADS1299 511 CLK periods later than the start command's count asks (see [Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement)) |
| TIM1, the IMUs | PSC = 0, ARR = 1,279, CH1 at CCR1 = 640: CLKIN at 38,400 Hz |
| TIM2, the start and the slots | PSC = 4: a tick of the suit clock, 101.7 ns, counted from the start command to START, and from DRDY to the slot |

**After a reset** the module takes the suit clock before it sets anything, and the line runs at
its rate from the start (see [Porjadok](../porjadok/SOFTWARE.md#the-clock-tree)).

**The glove's Staršaja** sets her clocks as the module, SPI1 for her one chip too: her four
U(S)ARTs to the Bratiški take PLL3 Q as her line's, at 16× and USARTDIV = 49 (BRR = 0x0031):
4,012,408 Bd, 0.31 % fast, and 115,200 Bd with even parity while she programs them, USARTDIV =
1,707 (BRR = 0x06AB); her LPUART1, the echo's receiver, PLL3 Q too, BRR = 2,560 for the line's
19,660,800 Bd; her TIM2 does what the module's TIM3 does, PSC = 0, ARR = 24, CH2 the CLK at CCR2 =
12 and CH1 START high at count 18, and her TIM5 counts the ticks with PSC = 4 (see
[hardware](HARDWARE.md#the-glove)).
**A Bratiška** runs on his HSI and never takes the suit clock: the HSI undivided, 64 MHz (HSIDIV
= 00, RCC_CR, 10.8.1), the core and the buses at 32 MHz by the AHB's ÷ 2 (HPRE, RCC_CFGR2,
10.8.6), in VOS3; his I3C buses from the bus clock; USART2 on the HSI's kernel clock (USART2SEL =
011, RCC_CCIPR1, 10.8.34), 16× and BRR = 0x0010: 4,000,000 Bd, as exact as the HSI (RM0492 Rev
3). Which receiver tolerates what is under [hardware](HARDWARE.md#the-glove).

## DMA

By the suit's rules (see [Porjadok](../porjadok/SOFTWARE.md#the-gpdma)). **The module,** 9
channels:

| channel | request (REQSEL) | what | priority | how |
|---|---|---|---|---|
| GPDMA1 0 | 27, uart4_rx | UART4 RX: Mamka's frames, 512 B a cycle at most | 3 | circular |
| GPDMA1 1 | 21, usart1_rx | USART1 RX: the echo of the module's own sending | 3 | circular |
| GPDMA1 2 | 6, spi1_rx | SPI1 RX: a chip's 27 B in frames of 8 bits, a linked list of two nodes: the status word aside, the channels into the frame; the second chip's read the same, started by the first's end with PA15 low, into bytes 28–51 of the frame of 58 B | 3 | two blocks at each DRDY |
| GPDMA1 4 | 122, i3c1_tc_dma | I3C1's control words, a frame of two reads | 1 | one block a sample |
| GPDMA1 5 | 120, i3c1_rx_dma | I3C1 RX: 2 × 12 B | 1 | one block a sample |
| GPDMA2 0 | 22, usart1_tx | USART1 TX: the frame and whatever follows it in the slot | 3 | one block a frame |
| GPDMA2 1 | 7, spi1_tx | SPI1 TX: zeros from one fixed word while reading; a command between two reads | 3 | with each read |
| GPDMA2 4 | 138, i3c2_tc_dma | I3C2's control words | 1 | one block a sample |
| GPDMA2 5 | 136, i3c2_rx_dma | I3C2 RX: 2 × 12 B | 1 | one block a sample |

Free: GPDMA1 3 and 6–7, GPDMA2 2–3 and 6–7. The SPI runs full duplex, so its TX channel clocks the
read with zeros; the CRC of the frame is the core's (see
[Porjadok](../porjadok/SOFTWARE.md#the-gpdma)).

**The glove's Staršaja** takes a module's nine, the master's usart1_rx and the echo's lpuart1_rx
in UART4's and USART1's places and her one chip's read one block, and four more at priority 2
for the Bratiški's steps coming in, usart2_rx, usart3_rx, uart4_rx and uart5_rx on GPDMA1 3, 6
and 7 and GPDMA2 2, thirteen in all; what she sends them, a frame now and then, goes
by the FIFO and an interrupt (see [Porjadok](../porjadok/SOFTWARE.md#the-gpdma)). **A Bratiška**
six: his two buses' four as a module's, his USART2's RX and TX.

## Interrupts

By the suit's levels (see [Porjadok](../porjadok/SOFTWARE.md#interrupts)); the numbers are the
vector table's (RM0481 Rev 5, table 153). **The module:**

| level | interrupt | what it does |
|---|---|---|
| 0 | EXTI2 (13) | DRDY: SPI1's read of the first chip started, TIM2 cleared for the slot |
| 1 | GPDMA1 channel 2 (29) | a read done: after the first, PA15 low and the second chip's read started; after the second, the frame built and, in slot 1, its sending started |
| 1 | TIM2 (45) | in slots 2–4, the slot's start: the frame's sending started |
| 2 | UART4 (61) | Mamka's frames: the line idle, the frame read |
| 2 | USART1 (58) | the end of sending: the echo checked |
| 6 | I3C1 (123, 124), I3C2 (131, 132), event and error | the IMUs' frames and in-band interrupts |
| 8 | ADC1 (37), FLASH (6) | the temperature and the 3.3 V, the firmware update |

**The glove's Staršaja** the same, her USART1 at 2 for Mamka's frames and for the end of
sending, the echo in the LPUART's buffer compared, and the Bratiški's U(S)ARTs at 4, a step in
on the link's idle; **a Bratiška** his TIM2 at 0, the step, his USART2 at 4, the
I3C at 6 and the flash at 8.

## From the errata

ES0621 Rev 3; the STM32H523 exists only as revision A.

- The USART's DMAT bit is never cleared between transmissions, or the DMA requests stop (2.15.2).
- The SPI is not disabled right after EOT, or the last SCLK edge is cut short (2.17.2).
- The I3C controller is initialised with a pull-up on SDA switched on for 1 ms first, or it
  sends a stray frame to address 0x7F (2.14.3).
- In legacy I2C reads STALLT stays off, or a target holding SDA brings dummy bytes (2.14.1).
- A glitch to zero in the second half of a stop bit corrupts a USART byte (2.15.1); the RS-485
  receivers' failsafe keeps the idle line clean, and the CRC catches the rest.

## Open questions

- the lead-off current, 6 or 24 nA, and the comparator threshold, by testing,
- against the reference on the head and the neck: whether BIAS_SENSN = 0x00 or the full sum holds
  the body better,
- 1,920 against 3,840 SPS on recordings,
- the ADS1298's register table against the ADS1299's, chip by chip on the first board, the two
  chips' first DRDYs together with the ADS1299's START 511 CLK later,
- the Bratiški programmed through Staršaja: the bootloader's rate detection, which AN2606 (4.5)
  gives up to ±5 % of jitter on some parts, and the time the four take, on the first board.
