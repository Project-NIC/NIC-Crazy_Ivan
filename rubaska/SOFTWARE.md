<div align="center">

# Rubaška: software

**What the sensing module's firmware does:** the ADS1299's settings, the IMUs', the glove and
the foot on the line, and the rules from the errata.

↑ [Rubaška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

The block's firmware is C with no operating system, like every module's
([Porjadok](../porjadok/README.md#firmware)). Its cycle, the frame it sends and how it reads the
ADS1299 are described under [Porjadok](../porjadok/SOFTWARE.md#the-frame); the start of a
measurement under [Starting a measurement](../porjadok/SOFTWARE.md#starting-a-measurement). This
page holds what is the block's own.

## The ADS1299's settings

- **The clock and START** come from TIM3, the clock ÷ 5 from the suit's (1.96608 MHz) and START
  held high for the whole measurement; the CLK output stays low until the ADS supplies are up
  (see [hardware](HARDWARE.md#power), *From the ADS1299 datasheet*).
- **Settings come from the master** in ready-made writes, one transaction a cycle between two
  reads: SDATAC, WREG, RDATAC (see
  [Porjadok](../porjadok/SOFTWARE.md#the-channel-from-the-master)). The block carries them out
  and can read them back; it knows nothing of what they mean.
- **The bias drive** (see [hardware](HARDWARE.md#right-leg-drive)): on the one driving module
  BIAS_SENSP = BIAS_SENSN = 0x7F, channel 8's MUX set to BIAS_DRN with IN8P as the spare
  (BIAS_DRP); on every other module PD_BIAS. Baťa picks the module.

**The registers,** from SBAS499C section 9.6 (tables 11 to 28), with the suit's values. Once the
suit is tuned these are expected to stay as they are; the way to change them while running is
there so that nothing has to be rebuilt, not because they will change.

| address | register | value | why |
|---|---|---|---|
| 0x00 | ID | read | bits 4:0 must read `11110`: bit 4 always 1, DEV_ID 11, NU_CH 10 for the eight-channel part; REV_ID is not compared (table 12) |
| 0x01 | CONFIG1 | **0xD2** | bit 7 = 1 and bits 4:3 = 10 as required; DAISY_EN = 1, multiple readback, one chip; CLK_EN = 0, no clock output; DR = 010, fMOD / 256 = 983,040 / 256 = **3,840 SPS** (table 13) |
| 0x02 | CONFIG2 | **0xC0** | the test signal off; for a test 0xD0 with an amplitude and a frequency (table 14) |
| 0x03 | CONFIG3 | **0xE8**, the driving module **0xEE** | PD_REFBUF = 1, the internal 4.5 V reference buffer on; bits 6:5 = 11 as required; BIASREF_INT = 1, the mid-supply made inside; PD_BIAS = 1 and BIAS_LOFF_SENS = 1 only on the module that drives the body (table 15) |
| 0x04 | LOFF | **0x00** | threshold 95 / 5%, 6 nA, DC; 24 nA is 0x04; the threshold is picked by testing (table 16) |
| 0x05–0x0C | CH1SET–CH8SET | **0x60** | on, gain 24 (110), SRB2 open, MUX 000 the electrode; on the driving module CH8SET **0x67**: MUX 111, BIAS_DRN, IN8N is the bias electrode (table 17) |
| 0x0D, 0x0E | BIAS_SENSP, BIAS_SENSN | driving **0x7F**, others **0x00** | the sum of channels 1 to 7 (tables 18, 19) |
| 0x0F, 0x10 | LOFF_SENSP, LOFF_SENSN | **0xFF**, driving **0x7F** | lead-off on every channel; on the driving module channel 8 drives the bias and gets none |
| 0x11 | LOFF_FLIP | **0x00** | the current's polarity as the datasheet has it |
| 0x12, 0x13 | LOFF_STATP, LOFF_STATN | read only | they go in the status word of every frame |
| 0x14 | GPIO | **0x0F**, the reset value | GPIO1–4 as inputs; on the board they are tied to DGND, so GPIO[7:4] in the status word reads 0000 |
| 0x15 | MISC1 | **0x00** | SRB1 open (table 26) |
| 0x16 | MISC2 | **0x00** | reserved |
| 0x17 | CONFIG4 | **0x02** | continuous conversion; PD_LOFF_COMP = 1 means the lead-off comparators **enabled**, despite the bit's name (table 28) |

**At start,** after the datasheet's own sequence (10.1.2, figure 67): the chip wakes in RDATAC,
so first SDATAC; then CONFIG3 with PD_REFBUF and a wait for the internal reference to settle;
then one WREG of 0x01 to 0x17, 23 registers, and an RREG of 0x00 to 0x17 back, compared with
what was written; only then START and RDATAC. The sequence of the whole suit's start is under
[Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement).

## An electrode coming off

The ADS1299 itself reports an electrode that has come off. It will rarely happen, but since
the chip can do it, we use it (datasheet SBAS499C, section 9.3.2.4.3). We use dc detection with
the internal current source:

- The ADS drives a small current into the inputs: 6 nA, 24 nA, 6 µA or 24 µA (±20%). One side
  of the channel is pulled towards the supply, the other towards ground.
- While the electrode holds, the current flows through the skin and the voltage stays small.
  When it comes off, the input runs to the supply and the channel saturates. Data keep coming,
  only at the end of the range.
- A comparator on every input (threshold COMP_TH, accurate to ±30 mV) then tells which
  electrode came off: bit n − 1 of LOFF_STATP belongs to input INnP (bit 0 is IN1P), and
  likewise LOFF_STATN to the INnN inputs. One bit is one physical electrode.
- The bits are valid only for channels enabled in LOFF_SENSP and LOFF_SENSN.
- Both bytes go in every frame; see [Porjadok](../porjadok/SOFTWARE.md#the-frame). The
  block does not split them; the bits are tested only in Baťa.

The current flows through the electrode and the skin and adds a small constant offset to the
measured signal. Only the nanoamp settings are usable: through a contact of 50 kΩ, 6 µA would
already make 0.3 V and 24 µA 1.2 V, beyond the ±187.5 mV range at a gain of 24. We will pick
between 6 and 24 nA, and the comparator threshold, by testing.

## The IMUs' settings

- **1,200 Hz, summed to 120 Hz:** CLKIN at 38,400 Hz scales every rate by 1.2 (DS-000347,
  12.5), so the 1 kHz setting runs at 1,200 Hz, ten samples to one step of 32 ADS samples
  (1/120 s). The block sums each step's ten samples (below) and sends 12 B per IMU per step,
  as a 120 Hz sample would take.
- **Over I3C,** two to a bus; if the first parts do not take SETDASA, the controller talks to
  them as I2C at their static addresses 0x68 and 0x69 (see [hardware](HARDWARE.md#sensing-module),
  *The IMUs on I3C*).
- Each IMU's 12 B go out one byte a frame, placed by the sample number
  ([Porjadok](../porjadok/SOFTWARE.md#the-frame)).

**The registers,** from DS-000347 Rev 1.9 (chapter 14 for bank 0, 15 for bank 1, 12.3 for the
I3C settings, 12.5 for CLKIN). Where the whole byte is known it is given; where a register also
holds fields left at their reset values, only the field is given, and the write is a
read-modify-write.

| bank, address | register | value | why |
|---|---|---|---|
| 0, 0x75 | WHO_AM_I | read, **0x47** | the chip's identity (14.58) |
| 0, 0x11 | DEVICE_CONFIG | bit 0 = 1, once | a soft reset at the start |
| 0, 0x13 | DRIVE_CONFIG | **0x05** | I2C_SLEW_RATE 0, SPI_SLEW_RATE 5: the values for I3C (12.3) |
| 1, 0x7B | INTF_CONFIG5 | PIN9_FUNCTION = 10 | pin 9 is CLKIN (15.18); INT1 stays for interrupts |
| 1, 0x7C | INTF_CONFIG6 | I3C_EN 1, I3C_IBI_EN 1, I3C_SDR_EN 1, I3C_DDR_EN 1 | I3C with in-band interrupts, scenario 2 of 12.3 |
| 1, 0x7A | INTF_CONFIG4 | I3C_BUS_MODE = 0 | the same |
| 0, 0x4D | INTF_CONFIG1 | RTC_MODE = 1, CLKSEL = 01 | the chip wants the external clock; the PLL when available (14.37) |
| 0, 0x4F | GYRO_CONFIG0 | **0x06** | ±2000 °/s (GYRO_FS_SEL 000); GYRO_ODR 0110, the 1 kHz setting, **1,200 Hz** under CLKIN (14.38); 0x08, the 100 Hz setting, for the chip's own 120 Hz |
| 0, 0x50 | ACCEL_CONFIG0 | **0x06** | ±16 g (ACCEL_FS_SEL 000); ACCEL_ODR 0110, 1 kHz, 1,200 Hz under CLKIN (14.39); 0x08 for 120 Hz |
| 0, 0x51 | GYRO_CONFIG1 | GYRO_UI_FILT_ORD = 01 | a second-order filter |
| 0, 0x53 | ACCEL_CONFIG1 | ACCEL_UI_FILT_ORD = 01 | a second-order filter |
| 0, 0x52 | GYRO_ACCEL_CONFIG0 | **0x33** | both filters at code 3, ODR / 8: at the 1 kHz setting 117.5 Hz at −3 dB, a noise bandwidth of 122.7 Hz and 3.2 ms of group delay (the second-order tables, 5.x); under CLKIN × 1.2, ~141 Hz, ~147 Hz, ~2.7 ms. Wide enough to keep a fast swing whole for the sum, which then does the decimation to 120 Hz. For the chip's own 120 Hz, 0x00: code 0, ODR / 2, 49.3 Hz at the 100 Hz setting, ~59 Hz under CLKIN, 6.5 ms |
| 0, 0x64 | INT_CONFIG1 | INT_ASYNC_RESET = 0 | the datasheet asks it for INT1 and INT2 to work (12.6) |
| 0, 0x4E | PWR_MGMT0 | **0x0F**, written last | gyro and accelerometer in Low Noise mode (GYRO_MODE 11, ACCEL_MODE 11), the temperature sensor on; after this write nothing is written for 200 µs, and the gyro is on for at least 45 ms before its data are trusted (14.36) |

- **What is read:** 12 B from 0x1F, ACCEL_DATA_X1 to GYRO_DATA_Z0, at every sample, 1,200 a
  second per IMU, 58 kB/s for four on the two buses, ~4% of I3C SDR; the temperature at
  0x1D–0x1E now and then into the rotating content, °C = TEMP_DATA / 132.48 + 25 (14.5). The
  FIFO is not used: every sample is fetched as it comes, on the IBI or by polling.
- **The sum,** what the 12 B per step carry, strapdown integration as Movella's MTw does it on
  the sensor at 1,000 Hz (its white paper, *Strap-Down Integration*): the turn over the step,
  Δθ = Σ ωᵢ Δt + ½ Σ (θᵢ₋₁ × θᵢ), the ten rate samples summed with the two-sample coning
  term, which the plain sum of rates leaves out when the piece turns about two axes at once;
  and the mean specific force over the step, Σ aᵢ / 10, no sculling term, since nobody
  integrates velocity. Both go out as three i16 each in the raw scale of ±2000 °/s and ±16 g,
  Δθ divided by the step, so a reader may take them as a 120 Hz sample of the gyro and the
  accelerometer and be right to first order. A cross product and two sums a sample, a few
  dozen instructions, in the block's own time.
- **The chip's own 120 Hz** stays as a mode, set by a container of type 4: the 100 Hz setting
  (0x08) and the filter at 0x00, the raw sample as it comes. It is the fallback should the
  IMUs ever talk I2C at 400 kHz on I3C2, where 1,200 Hz would fill the bus, and the way to
  compare the two on recordings.
- **The order:** the soft reset; bank 1 (CLKIN, I3C); bank 0 (the clock, the ranges and rates,
  the filters, INT); PWR_MGMT0 last, since nothing may be written for 200 µs after it.
- **A choice, not a datasheet value:** the second-order filter at ODR / 8 under the sum. In
  noise the two modes come out alike, the chip's filter or the sum of ten; the sum keeps the
  turn right in a fast swing, where a step of 8.3 ms taken as one rotation is off by up to
  ~0.05° a step at 300 °/s about two axes, a few degrees by the end of the swing, and at
  0.83 ms a hundredth of that (an estimate from the coning term, not a datasheet value). To be
  judged on recordings.

## The glove and the foot

- **Interconnect** is one half-duplex wire shared by the five Vnučata, into a third UART on the
  forearm's module: a TX pin lets go of the wire when it is not sending. Everyone on the wire
  hears everything, their own bytes too (the echo); a Vnučka answers only when called, so nothing
  collides.
- **2,000,000 Bd,** 8N1, 16× oversampling. The module makes it from its 196.608 MHz, ÷ 98 =
  2.0062 MBd; a Vnučka from her HSI, 64 MHz ÷ 32 = 2.0000 MBd. The two differ by 0.3%, and the
  HSI itself is 64 MHz ±0.5% at 30 °C and drifts ±1% from −20 to 105 °C (DS14053 Rev 4, HSI
  table), well inside what a UART bears.
- **The messages** are CI-STP containers as on the lines, header, data and CRC-16 (see
  [Porjadok](../porjadok/SOFTWARE.md#the-channel-from-the-master)), with Interconnect's own
  addresses: 1–5 the fingers, thumb first, 0 all of them; on the foot, 1.

  | `type` | from | data |
  |---|---|---|
  | 0x20 call | the module | none: "your turn" |
  | 0xA0 answer | the Vnučka | 1 B state (bits 0–3: a fresh step from IMU 1–4 since the last call, bit 4: I3C1 in order, bit 5: I3C2 in order), then 4 × 12 B, the IMUs' latest steps |
  | 1–6 | the master, forwarded | a container the master sent to the glove (N + 0x80) goes down the wire as it came, with its first data byte, the finger, taken out and put into `addr`; the Vnučka's answer, 0x80 + type, goes back the same way and the module relays it in its slot |

- **One Vnučka at a time,** in turn: the call is 6 B, the answer 55 B, 61 B at 2 MBd = 305 µs,
  longer than a cycle, so Interconnect keeps its own pace: the module sends the next call right
  after the answer, and all five fingers come round every ~1.5 ms, five times faster than the
  IMUs' 120 Hz. A Vnučka answers within 10 µs of the call's last stop bit; the module waits 40 µs,
  then counts a miss, and after three misses in a row marks the finger absent in the glove's
  state byte and keeps calling it, so a finger comes back by itself. A forwarded container takes
  the place of a call, up to 66 B each way, ~0.65 ms at most, and the round is longer by that
  once; the module holds one at a time, so the master sends the next one only in the second
  cycle after.
- **A Vnučka's firmware** comes the same way, finger by finger, since a container to all of them
  (`addr` 0) gets no answer: 1,366 pieces of 48 B for its 64 KB, 53 B of data with the finger
  byte, one every other cycle, ~0.7 s a finger and ~3.6 s for the glove (see
  [Porjadok](../porjadok/SOFTWARE.md#updating-firmware)).
- The Vnučata run on their HSI, read their IMUs when these report data, in-band interrupts over
  I3C or polling, sum them into steps of ten as the module does, and hold the latest step of
  each until they are called: a step is 12 B, as in the module (see
  [the IMUs' settings](#the-imus-settings)). The fingers' IMUs run on the same CLKIN as the
  module's, so their steps are 8.33 ms too, only not in phase with the module's; a call comes
  every ~1.5 ms, so no step is missed.
- **On the line** the forearm's module is two units in software. In its own slot it sends its
  frame, number N, and right after it the glove's, N + 0x80: 20.3 + 20.3 + 1 µs = 41.7 µs of
  the slot's 65.1, and a repeated frame still fits. The glove's frame has a byte per IMU, as a
  module's frame does, in the bytes the ADS channels take in a module's. Commands for N + 0x80
  go on to the glove over Interconnect, one at a time, the next two cycles later. With the glove
  unplugged only the module's frame comes, and Mamka sees the glove go and come back.
- Two gloves add 80 B a cycle on the lines; Baťa's record has their two slots in it always (see
  [Mamka](../mamka/SOFTWARE.md#the-cycle-to-baťa-over-spi)).
- The foot needs no frame of its own. One byte of a frame carries two IMUs (see
  [Porjadok](../porjadok/SOFTWARE.md#the-frame)), so the module's four IMU bytes take
  its own four and the foot's four.
- The module's firmware comes in two versions: one adds the foot to its own frame, the other
  sends the glove's frame as a second unit.

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
- the Interconnect rate and the Vnučata's answer within the forearm module's slot, on a sample.
