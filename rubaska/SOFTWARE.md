<div align="center">

# Rubaška: software

**What the sensing module's firmware does:** the ADS1298's settings, the IMUs', the glove and
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

Every module carries the ADS1298: a module of the body and the head's two, chips 0x01 and 0x06,
the neck's one, chip 0x01 (see [hardware](HARDWARE.md#sensing-module)); the firmware finds them
by the ID register, and one table of values serves every chip, the bias's bits aside.

- **The clock and START** come from TIM3, the suit's clock ÷ 5 (1.96608 MHz) and START
  held high for the whole active mode; the CLK output stays low until the ADS supplies are up
  (see [hardware](HARDWARE.md#power), *From the ADS1298's datasheet*). A module's two chips share
  both, so that their first DRDYs fall together (see
  [Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement)).
- **The reads:** the two chips in cascade on SPI1, DIN, DOUT and SCLK shared, the first's chip
  select the SPI's NSS on PA4, the second's a plain pin, PA15; at DRDY the first is read, then
  the second, 216 bits each (SBAS459K, 9.4.2.1).
- **Settings come from Mamka** as writes to the chips 0x01 and 0x06 (see
  [Porjadok](../porjadok/SOFTWARE.md#the-commands)). The module carries them out between two
  reads, SDATAC, WREG, RDATAC, and answers with the result; it knows nothing of what they mean,
  beyond the switches that go with them (below).
- **The bias drive** (see [hardware](HARDWARE.md#right-leg-drive)): the first chip's amplifier,
  on the driving module PD_RLD on, on every other module powered down, its output then leaving
  the bias electrode alone; RLD_SENSP = RLD_SENSN = 0xFF on every module's first chip, so that
  its RLDINV carries the inputs' common mode for the strip's driver (see
  [hardware](HARDWARE.md#the-strips-ground-layer)); a second chip's amplifier is always powered
  down and sums nothing. Baťa picks the module, by register 0x00 of its chip 0x00, which sets
  PD_RLD.
- **The bias electrodes checked at start,** one module at a time: CONFIG3 = **0xEA** (the amplifier
  off, RLD_LOFF_SENS = 1) with LOFF = **0x03**, the DC check for this moment alone, CONFIG3 read
  back, bit 0 being RLD_STAT (0 connected). Baťa then picks a module whose bias electrode is
  connected; while it drives, CONFIG3 = 0xEE keeps RLD_LOFF_SENS on, and its RLD_STAT going to 1
  means the drive has run to a rail (see [hardware](HARDWARE.md#right-leg-drive)). The module reads
  CONFIG3 back once in every 32 cycles and puts RLD_STAT and whether its PD_RLD (bit 2) matches its
  setting in the diagnostics (see [Porjadok](../porjadok/SOFTWARE.md#the-diagnostics)); Baťa passes
  them on in the electrodes' meta packet. **The drive measured:** at the start and every 30 minutes
  the driving module sets RLD_MEAS (CONFIG3 bit 4), its first chip's channel 8 to MUX 010 at gain 1
  (CH8SET 0x12) and channel 8 out of the bias's sum (RLD_SENSP and RLD_SENSN 0x7F), reads
  RLDOUT against RLDREF, its own mid-supply, for 32 samples, and puts the channel back (SBAS459K
  9.3.1.7.2, figure 34); the channel's samples meanwhile are marked as a gap.
- **The unit's own bits:** PD_RLD, RLD_LOFF_SENS and LOFF_SENSP and LOFF_SENSN are the unit's,
  set over whatever Baťa writes; its read-back after a write skips RLD_STAT and LOFF_STATP and
  LOFF_STATN (12h, 13h), which the chip sets itself; a write of CONFIG1 or RESP in the active mode
  is refused (result 4), since it resets the digital filter (SBAS459K, 9.3.2.3).
- **The strip's ground layers,** register 0x03 of chip 0x00: 1, the default, driven at the
  common mode of the first chip's RLDINV, PA2 high; 0 on ground, the TLV9001S shut down by PA2
  low (see [hardware](HARDWARE.md#the-strips-ground-layer)). After a reset PA2 is low, the layers
  on ground until the register is applied.
- **Every channel differential,** on the head and the neck as on the body (see
  [hardware](HARDWARE.md#right-leg-drive)); the registers are the same on every module, the
  bias's bits aside.

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
| 0x04 | LOFF | **0x01**; **0x03** for the bias check at start | FLEAD_OFF 01, the AC lead-off at fDR / 4, 480 Hz at 1,920 SPS (960 Hz at 3,840), which excites only while a check runs (LOFF_SENSP and LOFF_SENSN); the threshold bits 95 / 5 % for the bias's comparator; FLEAD_OFF 11, DC, only for the check at start; 00 is not allowed with any LOFF_SENS bit on (9.6.1.5) |
| 0x05–0x0C | CH1SET–CH8SET | **0x60** | on, gain 12 (110, the ADS1298's code; 0x50 would be gain 8), MUX 000 the electrode, on every chip; the bias has a lead of its own (9.6.1.6) |
| 0x0D, 0x0E | RLD_SENSP, RLD_SENSN | **0xFF** on every module's first chip, **0x00** on the second | the sum of the first chip's sixteen inputs on RLDINV, for the bias drive on the driving module and for the strip's driver on every module (9.6.1.7) |
| 0x0F, 0x10 | LOFF_SENSP, LOFF_SENSN | **0x00**; **0xFF** both while a check runs | no excitation but in a check, and 0x00 through the bias check at start too, so no DC flows through the studs; a check when Baťa asks, never while recording, every P and N input together for one diagnostics period, as the datasheet pairs them, the P pulled up and the N pulled down so that the currents cancel in the body (see [An electrode coming off](#an-electrode-coming-off)) |
| 0x11 | LOFF_FLIP | **0x00** | the current's polarity as the datasheet has it |
| 0x12, 0x13 | LOFF_STATP, LOFF_STATN | read only | the comparators' bits, for a DC lead-off; in the AC check the tone tells, and they are not used |
| 0x14 | GPIO | **0x0F**, the reset value | GPIO1–4 as inputs; on the board they are tied to DGND |
| 0x15 | PACE | **0x00** | no pace detection |
| 0x16 | RESP | **0x20** | no respiration circuit, the ADS1298R's; bit 5 reserved, always written 1 (SBAS459K, table 32) |
| 0x17 | CONFIG4 | **0x02** | continuous conversion; PD_LOFF_COMP = 1 means the lead-off comparators **enabled**, despite the bit's name (9.6.1.11); they stay on for the bias electrode's RLD_STAT |
| 0x18, 0x19 | WCT1, WCT2 | **0x00** | the Wilson central terminal's amplifiers off |

The 25 registers 0x01 to 0x19 go in one frame of 34 B.

**1,920 SPS, and 3,840 to try.** 1,920 is the professionals' rate for surface EMG, Delsys'
Trigno 1,926, Meta's band 2,000, OT's 2,048, and the band SENIAM recommends is 10–500 Hz: the
filter's −3 dB lies at ~503 Hz on the suit's clock (SBAS459K, Electrical Characteristics, 0.262
fDR). 3,840 is the setting to try, CONFIG1 0xC3: the band to ~1 kHz, for twitches a trained eye
might want to see whole, at twice the data and processor 1's SPI at 87 % with two chips a module
(see [Porjadok](../porjadok/SOFTWARE.md#into-baťa)); the step then counts 32 samples instead of
16. The rate is set only before the first start, since the cycle, the step and the first DRDY's
place after START all follow it (SBAS459K, 9.4.1.1.1, table 12; see
[Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement)); why 3,840 is not the rate is under
[WHY](WHY.md#the-sensing-module).

**Gain 12, not 24.** A channel takes ±VREF / gain, ±333 mV at a gain of 12 on the ADS1298's 4 V
reference (SBAS459K, 9.3.1.5.2, equation 3), and the electrodes' DC offset takes its share of it
(see [Construction](CONSTRUCTION.md#electrodes)); 24 would leave half. The noise at the 2 kSPS
setting and a gain of 12 is 0.8 µVrms (SBAS459K, table 3, 5 V and the 4 V reference), against
EMG of tens of microvolts and more. The common-mode range narrows as a channel's input grows
(SBAS459K, 9.3.1.5.1, equation 2: AVDD − 0.2 V − gain · V / 2 > CM > AVSS + 0.2 V + gain ·
V / 2): with 300 mV across a channel at a gain of 12 the body may sit anywhere from 2.0 to
3.0 V, and the bias drive holds it at 2.5 V; at a gain of 24, 176 mV would leave only 2.31 to
2.69 V. The gain is one for the whole suit, as
Baťa's scale assumes (see [signals](../bata/SIGNALS.md#the-emg-channel)), the scale by the chip's
reference.

**At start,** after the datasheet's own sequence (SBAS459K, 10.1.1, figure 93): a chip wakes in
RDATAC, so first SDATAC; then CONFIG3 with PD_REFBUF and a wait for the internal reference to
settle; then the registers of 0x01 on as they came in one frame, written by two WREGs around the
read-only LOFF_STATP and LOFF_STATN, and an RREG of all of them back, compared with what was
written; only then START and RDATAC, the second chip the same after the first. The sequence of
the whole suit's start is under [Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement).
**Asleep** in the service mode the chips are in standby, by their STANDBY command, and wake by
WAKEUP (see [Porjadok](../porjadok/SOFTWARE.md#bring-up)).

## An electrode coming off

The ADS1298 itself can tell an electrode that has come off (SBAS459K, 9.3.1.7.4), and we use it
**by its AC lead-off, as a check on demand, never while recording:**

- **What the excitation is.** The chip's AC lead-off switches each excited input up and down at
  fDR / 4, 480 Hz at 1,920 SPS (9.3.1.7.4.2). LOFF's bit 4, VLEAD_OFF_EN, chooses the source (the
  LOFF register): 0 the current sources, their size by ILEAD_OFF, 6 nA at 00; 1 the pull-up and
  pull-down resistors, ~10 MΩ from the rails (figure 39: 3.3 MΩ and 12 pF a side, switched only
  with VLEAD_OFF_EN; "pullup resistor lead-off detection, 10 MΩ", Electrical Characteristics),
  ~±0.25 µA an input. **LOFF is 0x01, so most likely the 6 nA sources:** our reading of the
  register and the figure, the datasheet's words on the AC mode naming only the resistors; which
  it is, is read on the first module. At 6 nA the tone is ~0.7 mV pp a side and ~1.3 mV pp
  across a pair at a 50 kΩ contact, P and N pulled opposite ways, the size of an EMG; through the
  resistors (0x11, not used) it would be ~55 mV pp, ~8 % of the channel's 666 mV at a gain of 12.
  Either way a tone in the band the model reads, so it does not run under the recording.
- **The check:** LOFF_SENSP = LOFF_SENSN = 0xFF for one diagnostics period of 32 cycles, every P and
  N input together, the P pulled up and the N pulled down as the datasheet pairs them, so that the
  currents cancel in the body and nothing returns through the bias lead; the P inputs alone, 280 of
  them, would send their currents through the one bias electrode, ~1.7 µA at 6 nA and, through the
  resistors, ~70 µA, ~7 V across its 100 kΩ, past the amplifier's 75 µA of drive (Electrical
  Characteristics, the RLD amplifier at full swing). The unit leaves out the first four samples
  after the switch and sums each channel's other 28 of the period against the tone's pattern, four
  samples a period, locked to the samples; an amplitude over the threshold, found by testing, or a
  channel at a rail marks the pair off, and its amplitude below is the contact's own measure, the
  pair's two contacts summed. Then LOFF_SENSP = LOFF_SENSN = 0x00 again. The bits go in the
  diagnostics, 1 for a pair on the skin, both bytes the same, and stay as the last check left them
  (see [Porjadok](../porjadok/SOFTWARE.md#the-diagnostics)); which side came off, the comparators
  cannot tell without DC, so the pair is the unit.
- **When:** in the active mode, the chips converting, when Baťa asks by chip 0x00's register 0x04
  (see [Porjadok](../porjadok/SOFTWARE.md#the-registers)), never while recording: at putting-on,
  right after the first *start*, repeated every few seconds until every pair is on, the map's page
  showing it and Nataša giving one short pulse when the last pair is on, the contact ready (see
  [Baťa](../bata/SOFTWARE.md#the-map)); in the contact tests; and between two recordings. The check
  takes the next diagnostics period of 32 cycles, its bits in that period's diagnostics, and Baťa
  leaves those cycles out of the model and of any recording. While recording an electrode that comes
  off shows in its channel itself: the input floats, the channel runs to a rail or carries the mains
  at full swing, and Baťa marks it absent from the channel (see
  [Baťa](../bata/SIGNALS.md#the-electrodes-quality)).

While the suit runs no lead-off current flows through the electrode and the skin, neither DC nor
the tone, only each input's bias current of ±1 nA at most (SBAS459K, Electrical Characteristics),
so the studs are not polarised by it:
under current pulses of ±5 nA, stainless steel and platinum polarised at once, off the figure's
scale, where sintered Ag/AgCl held (Tallgren, Vanhatalo, Kaila and Voipio, *Evaluation of
commercially available electrodes and gels for recording of slow EEG potentials*, Clin
Neurophysiol 116, 799–806, 2005, fig. 2). The DC check stays only for the bias electrode at start.

## The IMUs' settings

- **960 Hz, summed to 120 Hz:** REF at 24 Hz holds the LSM6DSV16X's 800 Hz setting at 960 Hz, 40
  samples a period, or at 15 Hz, 64 (see [hardware](HARDWARE.md#the-imu)): eight samples, a sample
  every second ADS cycle, to one step of 16 ADS samples at 1,920 SPS (1/120 s), 32 at the 3,840 to
  try, the same step; the module tells the step's length from CONFIG1. It sums each step's samples
  (below) and sends 12 B per IMU per step, as a 120 Hz sample would take.
- **Over I3C,** two to a bus, each given its I3C address from its static one, 0x6A or 0x6B, by
  SETDASA (DS13510 Rev 4, table 17; see [hardware](HARDWARE.md#sensing-module), *The IMUs on
  I3C*); on the glove two to a branch, the branches switched (see [The glove](#the-glove)).
- Each IMU's 12 B go out after the step, 4 B a frame, placed by the frame's number
  ([Porjadok](../porjadok/SOFTWARE.md#a-units-data)).

**The registers,** from DS13510 Rev 4 (section 9, table 24 the map) and AN5763 Rev 4 (3.3 for
the ODR-triggered mode, 5.7 for the resets). They are addressed directly, one bank, the address
incremented through a burst (IF_INC, CTRL3). Where a register also holds fields left at their
reset values, only the field is given, and the write is a read-modify-write.

| address | register | value | why |
|---|---|---|---|
| 0x0F | WHO_AM_I | read, **0x70** | the chip's identity (9.13) |
| 0x12 | CTRL3 | **0x45**, once: SW_RESET with BDU and IF_INC as at reset | a soft reset at the start, after the boot's 10 ms at most, both sensors powered down; 150 µs, or SW_RESET read back until 0 (AN5763, 5.7) |
| 0x15 | CTRL6 | **0x44** | ±2000 °/s (FS_G 0100); LPF1_G_BW 100, the gyro's filter at ~100 Hz (table 64, the 960 Hz column); **0x64** for the 120 Hz mode, 110, ~24 Hz (9.19) |
| 0x16 | CTRL7 | **0x01** | LPF1_G_EN, the gyro's first filter on; the analog hub off (9.20) |
| 0x17 | CTRL8 | **0x23** | ±16 g (FS_XL 11); HP_LPF2_XL_BW 001, the accelerometer's filter at ODR / 10, ~96 Hz; **0x03** for the 120 Hz mode, ODR / 4, 30 Hz (9.21, table 69) |
| 0x18 | CTRL9 | **0x08** | LPF2_XL_EN, the accelerometer's second filter in the path (9.22) |
| 0x06 | ODR_TRIG_CFG | **0x14**, 40 samples a REF period at 24 Hz; **0x20**, 64 at 15 Hz | the samples a period, in twos (9.4; AN5763, 3.3) |
| 0x10, 0x11 | CTRL1, CTRL2 | **0x30**, then **0x39** | first the ODR-triggered mode with both sensors still powered down (OP_MODE 011), then the 800 Hz setting (ODR 1001), **960 Hz** under REF, written after REF has started (9.14, 9.15; AN5763, 3.3, table 15); **0x06** for the 120 Hz mode, the high-performance mode at the chip's own 120 Hz (tables 52 and 55) |
| 0x13 | CTRL4 | **0x01** | INT2_IN_LH: REF's rising edge (9.17) |
| 0x0D | INT1_CTRL | **0x00** | no in-band interrupt on any unit, INT1 itself open on the board (9.11): every IMU is read by the schedule from REF, one way for the module, the glove and the sock, a branch switched away being unable to raise one anyway |

- **What is read:** 12 B from 0x22, OUTX_L_G to OUTZ_H_A, the gyro's three axes and then the
  accelerometer's, little-endian, low byte first, in two's complement (DS13510, 9.30–9.35), at
  every sample, 960 a second per IMU, 46 kB/s for four on the two buses, ~3 % of I3C SDR; the
  temperature at 0x20–0x21 now and then into the diagnostics, °C = OUT_TEMP / 256 + 25 (table 6;
  its offset ±15 °C). The FIFO is not used: every sample is fetched as it comes, by the schedule
  from REF on every unit.
- **The sum,** what the 12 B per step carry, strapdown integration as Movella's MTw does it on
  the sensor at 1,000 Hz (its white paper, *Strap-Down Integration*): the turn over the step,
  Δθ = Σ ωᵢ Δt + ½ Σ (θᵢ₋₁ × θᵢ), the eight rate samples summed with the two-sample coning
  term, which the plain sum of rates leaves out when the piece turns about two axes at once;
  and the mean specific force over the step, Σ aᵢ / 8, no sculling term, since nobody
  integrates velocity. Both go out as three i16 each in the raw scale of ±2000 °/s and ±16 g
  (70 mdps and 0.488 mg a bit, DS13510 table 3), Δθ divided by the step and rounded with its
  error carried into the next step, so that the integral stays exact, so a reader may take
  them as a 120 Hz sample of the gyro and the accelerometer and be right to first order. A cross
  product and two sums a sample, a few dozen instructions, in the module's own time; eight a
  step, so the mean is a shift.
- **The chip's own 120 Hz** stays as a mode, set by register 1 of the module's chip 0x00: the
  high-performance mode at its own 120 Hz (DS13510, table 52), free of the suit clock, REF held
  low, the filters at ~24 and 30 Hz, the latest sample at each step as it comes. Under REF a
  120 Hz rate would want at least 8 samples and 80 ms a period (AN5763, table 15), which REF's
  24 and 15 Hz do not give. It is the fallback should the IMUs ever talk I2C at 400 kHz on I3C2,
  where 960 Hz would leave the bus too little room, and the way to compare the two on
  recordings.
- **The order** (AN5763, 3.3): the boot; the soft reset; WHO_AM_I; the ranges and the filters,
  CTRL6 to CTRL9; ODR_TRIG_CFG; CTRL1 and CTRL2 at 0x30; CTRL4; INT1_CTRL; then **REF started,**
  once every IMU on its wire is set, and CTRL1 and CTRL2 at 0x39. The data are trusted four REF
  periods later, when the chip has locked, 167 ms at 24 Hz and 267 ms at 15 Hz (3.3), which
  covers the gyro's 30 ms of turn-on (DS13510, table 4). Until REF starts the firmware holds it
  low (see [hardware](HARDWARE.md#the-imu-board)). A change of the IMU mode (chip 0x00 register
  0x01) goes the same way, the sensors powered down first (3.3).
- **REF in one phase on every unit:** at the first *start* REF's timer, TIM1, is restarted by the
  same count of suit-clock ticks that raises START (see
  [Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement)), its first edge on cycle 0 of every
  unit alike, within the ~0.2 µs the start's arrival spreads, its period of 80 cycles five steps
  of 16. Step k is then the eight samples of cycles 16k to 16k + 15 on every unit. The IMUs lock
  again within four periods, and the steps of the first 320 cycles are marked as not trusted.
- **A choice, not a datasheet value:** the filters at ~100 Hz under the sum. In noise the two
  modes come out alike, the chip's filter or the sum of eight; the sum keeps the turn right in
  a fast swing, where a step of 8.3 ms taken as one rotation is off by up to ~0.05° a step at
  300 °/s about two axes, a few degrees by the end of the swing, and at 1.04 ms far less (an
  estimate from the coning term, not a datasheet value). The corners are the sheet's for the
  960 Hz rate; that they hold under REF at 960 Hz is our inference. To be judged on
  recordings.
- **Asleep** in the service mode the IMUs go to sleep, CTRL1 and CTRL2 at 0x00, both sensors
  powered down (2.6 µA, DS13510 table 4), REF held low, and come back with the order above.

## The glove

The glove, Vešč, is a unit of its own on its arm's line, in the fourth slot: one board on the back
of the hand with one ADS1298 and Staršaja, who reads every IMU of the hand herself (see
[hardware](HARDWARE.md#the-glove)); the sock, Nosok, is the same board and firmware in a leg's
fourth slot:

- **Its frame of data** is **0x25, 58 B:** its ADS1298's eight channels in bytes 4–27 as a
  module's first chip's, and its IMUs' steps in the 28 B after them, bytes 28–55: the glove's 24
  IMUs, 288 B, in the frames 0–10 of the 16 after each step, zeros after them, a sock's eight in
  four (see [Porjadok](../porjadok/SOFTWARE.md#a-units-data)); in her table's order, branch by
  branch (see [the IMUs' settings](#the-imus-settings)). Its diagnostics are a module's with one
  chip, ones for the second's eight, the IMUs' temperatures by turns, six a frame, the 24 in four.
- **Staršaja runs a module's firmware** for her line and her chip: she gets *get ready* and
  *start* as every unit, keeps the cycle from her ADS1298's DRDY and reads it as a module reads
  its first chip. Her line and her pins are a module's too (see
  [hardware](HARDWARE.md#the-glove)), her six SELs the only pins of her own.
- **Her IMUs,** on her two I3Cs, each I3C's SDA switched among six branches of two IMUs by three
  TS3USB3031 side by side, one SEL0 and SEL1 a chip for both I3Cs, so the two buses move
  together (see [hardware](HARDWARE.md#the-glove)). A chip not in use sits on its park, USB1, and
  each change is a change of channel, 400 ns at most; the high-Z state is never set. A round at
  960 Hz takes the six positions in turn, both I3Cs reading their branch's two IMUs together,
  220 µs of the 1,041.7 µs at 10 MHz (21 %): the chips set, the reads, the next position.
- **Addresses:** at the bring-up she selects each branch in turn and gives its two IMUs, 0x6A
  and 0x6B, dynamic addresses of their own by SETDASA, one an IMU (DS13510 Rev 4, table 17), so a
  branch wrongly selected answers nothing and its gap shows; a write to one IMU, chip 0x10 on,
  goes to its branch, a write to every IMU (0x0F) branch by branch.
- **No IBI:** an IMU on a branch switched away cannot raise its in-band interrupt, so the
  glove's and the sock's IMUs have none (INT1_CTRL 0x00, see
  [the IMUs' settings](#the-imus-settings)); she reads every IMU by her schedule from REF, whose
  edges and the samples between them her TIM1 times, a sample every 1,041.7 µs.
- **REF** for every IMU of the glove is Staršaja's, made from the suit clock on her TIM1 as a
  module's, on a trace to every strip, so the IMUs sample in step with the suit. She holds REF
  low until every IMU of the board is set (see [the IMUs' settings](#the-imus-settings)).
- **With the glove off its line,** for a repair, the fourth slot stays empty; back on, it joins
  at the next bring-up, as any unit that has reset, answering *discover* by its own UID.

## Clocks

By the suit's clock tree (see [Porjadok](../porjadok/SOFTWARE.md#the-clock-tree)): the core at
49.152 MHz, PLL1P ÷ 8, in VOS1, the line's USARTs on PLL3 Q. **The module** adds:

| what | setting |
|---|---|
| SPI1 to the ADS1298 | PLL1Q ÷ 5 (field 4): 78.6432 MHz, SPI1SEL = 000 (RCC_CCIPR3, 11.8.42), the SPI's own ÷ 4: 19.66 MHz, under the 100 MHz kernel limit of VOS1 (DS14540, table 20) and the chips' 20 MHz; the first chip's select the NSS on PA4, the second's PA15 by software |
| USART1 and UART4, the line | PLL3 Q, 196.608 MHz, USART1SEL and UART4SEL = 010 (RCC_CCIPR1, 11.8.40); OVER8 = 1, BRR = 0x0012: 19,660,800 Bd |
| I3C1, I3C2 | the APB clocks, I3C1SEL and I3C2SEL = 00 (RCC_CCIPR4, 11.8.43): 49.152 MHz |
| TIM3, the ADS1298 | PSC = 0, ARR = 24: CH3 in PWM at CCR3 = 12, the CLK at 1.96608 MHz, high for 12 of its 25 counts, the datasheet giving its period, 414–514 ns (SBAS459K, 7.6; 1.94–2.25 MHz, 7.3), and not its duty; CH4 takes START high at count 18, the middle of the CLK's low half (see [Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement)) |
| TIM1, the IMUs | PSC = 1,023, a tick of 20.8 µs; ARR = 1,999, CH1 at CCR1 = 1,000: REF at 24 Hz, the suit clock ÷ 409,600; ARR = 3,199 and CCR1 = 1,600 for 15 Hz; held low, CH1 forced inactive, until every IMU on it is set and in the 120 Hz mode |
| TIM2, the start and the slots | PSC = 4: a tick of the suit clock, 101.7 ns, counted from the start command to START, and from DRDY to the slot |

**After a reset** the module takes the suit clock before it sets anything, and the line runs at
its rate from the start (see [Porjadok](../porjadok/SOFTWARE.md#the-clock-tree)).

**The glove's Staršaja** sets her clocks and timers as the module does, SPI1 for her one chip
too (see [hardware](HARDWARE.md#the-glove)).

## DMA

By the suit's rules (see [Porjadok](../porjadok/SOFTWARE.md#the-gpdma)). **The module,** 9
channels:

| channel | request (REQSEL) | what | priority | how |
|---|---|---|---|---|
| GPDMA1 0 | 27, uart4_rx | UART4 RX: Mamka's frames, a buffer of 2 × 1,024 B, a cycle's 1,024 B and a firmware frame's 519 B | 3 | circular |
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

**The glove's Staršaja** takes a module's nine as they are, her one chip's read one block; her two
I3Cs' four as a module's, a frame of two reads a position, the switches set by the core between
positions.

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

**The glove's Staršaja** the same as a module; her TIM1 at 6 with the I3Cs, REF's samples
timed and each round of reads started, the next position set as a position's reads end, the
step closed at its eighth sample.

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

- the IMUs' FIFO read once a step, eight samples, against a read a sample: ~25 % less bus time
  and eight times fewer interrupts on the glove, if the FIFO runs in the ODR-triggered mode
  (AN5763, 3.3), tried on the first module,
- INT2 as REF's input while I3C runs, CTRL5's INT_EN_I3C: asked of ST or tried on the first
  module,
- the lead-off check: what the AC excitation switches, resistors from the rails as figure 39
  draws it or the current sources, and its current, measured on the first module; the tone's
  threshold and what a poor contact looks like against an open one; the steel's offset beside
  Ag/AgCl's with a DC lead-off current and without it, on the first arm,
- 1,920 against 3,840 SPS on recordings,
- the ADS1298's register table on the first board, chip by chip, the two chips' first DRDYs
  together,
- REF at 24 against 15 Hz: the lock, the samples' place against the cycle, the step's eight
  IMU samples against its sixteen ADS samples; the filters' corners under REF, on the first
  board,
- the glove's round: the switches' change of channel between reads, the reads by the schedule
  against REF's samples, and the branches switched away quiet, on the first glove.
