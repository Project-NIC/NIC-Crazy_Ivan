<div align="center">

# Rubaška: software

**What the sensing module's firmware does:** the ADS1299's settings, the IMUs', the glove, and
the rules from the errata.

↑ [Rubaška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

The module's firmware is C with no operating system, like every unit's
([Porjadok](../porjadok/README.md#firmware)). Its cycle, the frame it sends and how it reads the
ADS1299 are described under [Porjadok](../porjadok/SOFTWARE.md#the-frames); its registers and its
table under [the registers](../porjadok/SOFTWARE.md#the-registers); the start of a measurement
under [Starting a measurement](../porjadok/SOFTWARE.md#starting-a-measurement). This page holds
what is the module's own.

## The ADS1299's settings

- **The clock and START** come from TIM3, the suit's clock ÷ 5 (1.96608 MHz) and START
  held high for the whole active mode; the CLK output stays low until the ADS supplies are up
  (see [hardware](HARDWARE.md#power), *From the ADS1299 datasheet*).
- **Settings come from Mamka** as writes to the chip 0x01 (see
  [Porjadok](../porjadok/SOFTWARE.md#the-commands)). The module carries them out between two
  reads, SDATAC, WREG, RDATAC, and answers with the result; it knows nothing of what they mean,
  beyond the switches that go with them (below).
- **The bias drive** (see [hardware](HARDWARE.md#right-leg-drive)): on the driving module
  PD_BIAS on, BIAS_SENSP = BIAS_SENSN = 0xFF, and its switch closed (PA1 high); on every other
  module the amplifier powered down and the switch open. Baťa picks the module, by register 0x00
  of its chip 0x00, which closes the switch.
- **The bias electrodes checked at start,** one module at a time: its switch closed (PA1 high),
  CONFIG3 = **0xEA** (the amplifier off, BIAS_LOFF_SENS = 1), CONFIG3 read back, bit 0 being
  BIAS_STAT (0 connected); then its switch opened again. Baťa then picks a module whose bias
  electrode is connected; while it drives, CONFIG3 = 0xEE keeps BIAS_LOFF_SENS on, and its
  BIAS_STAT going to 1 means the drive has run to a rail (see
  [hardware](HARDWARE.md#right-leg-drive)). The module reads CONFIG3 back once in every 32 cycles
  and puts BIAS_STAT in the diagnostics (see [Porjadok](../porjadok/SOFTWARE.md#the-diagnostics));
  Baťa passes it on in the electrodes' meta packet.
- **Two ways of measuring,** on every module, each with its reference electrode (see
  [Bogatyr](../bogatyr/README.md)): differential with MISC1 = 0x00; or against the reference with
  MISC1 = 0x20, the ADS1299's own switch joining SRB1 to the channels and cutting the INnN pins off
  (figure 18). Baťa picks the way by writing MISC1.

**The registers,** from SBAS499C section 9.6 (tables 11 to 28), with the suit's values. Once the
suit is tuned these are expected to stay as they are; the way to change them while running is
there so that nothing has to be rebuilt, not because they will change.

| address | register | value | why |
|---|---|---|---|
| 0x00 | ID | read | bits 4:0 must read `11110`: bit 4 always 1, DEV_ID 11, NU_CH 10 for the eight-channel part; REV_ID is not compared (table 12) |
| 0x01 | CONFIG1 | **0xD2**; **0xD3** to try | bit 7 = 1 and bits 4:3 = 10 as required; DAISY_EN = 1, multiple readback, one chip; CLK_EN = 0, no clock output; DR = 010, fMOD / 256 = 983,040 / 256 = **3,840 SPS**, or DR = 011, fMOD / 512 = **1,920 SPS** (table 13) |
| 0x02 | CONFIG2 | **0xC0** | the test signal off; for a test 0xD0 with an amplitude and a frequency (table 14) |
| 0x03 | CONFIG3 | **0xE8**, the driving module **0xEE**, **0xEA** for the bias check at start | PD_REFBUF = 1, the internal 4.5 V reference buffer on; bits 6:5 = 11 as required; BIASREF_INT = 1, the mid-supply made inside; PD_BIAS = 1 only on the module that drives the body; BIAS_LOFF_SENS = 1 on it, and on each module in turn for the check at start (table 15) |
| 0x04 | LOFF | **0x00** | threshold 95 / 5%, 6 nA, DC; 24 nA is 0x04; the threshold is picked by testing (table 16) |
| 0x05–0x0C | CH1SET–CH8SET | **0x50** | on, gain 12 (101, see below), SRB2 open, MUX 000 the electrode, on every module; the bias has a lead of its own (table 17) |
| 0x0D, 0x0E | BIAS_SENSP, BIAS_SENSN | driving **0xFF**, others **0x00**; against the reference, driving BIAS_SENSN **0x00** | the sum of all sixteen inputs; against the reference every N side is the reference electrode itself, so only the P sides are summed, a choice of ours (tables 18, 19) |
| 0x0F, 0x10 | LOFF_SENSP, LOFF_SENSN | **0xFF**; against the reference LOFF_SENSN **0x00** | lead-off on every input; the N pins stand idle against the reference |
| 0x11 | LOFF_FLIP | **0x00** | the current's polarity as the datasheet has it |
| 0x12, 0x13 | LOFF_STATP, LOFF_STATN | read only | they come in the status word of every read, and go in the diagnostics |
| 0x14 | GPIO | **0x0F**, the reset value | GPIO1–4 as inputs; on the board they are tied to DGND, so GPIO[7:4] in the status word reads 0000 |
| 0x15 | MISC1 | **0x00**; against the reference **0x20** | SRB1 open, or SRB1 to every channel's inverting input (table 26) |
| 0x16 | MISC2 | **0x00** | reserved |
| 0x17 | CONFIG4 | **0x02** | continuous conversion; PD_LOFF_COMP = 1 means the lead-off comparators **enabled**, despite the bit's name (table 28) |

**3,840 SPS, and 1,920 to try.** The rate is set for fast movements in sport, and for the twitches
of a nervous system that does not work as it should, which cannot even be seen from outside; the
band reaches ~1 kHz at −3 dB (SBAS499C, table 3, on the suit's clock). 1,920 SPS, the
professionals' ~2 kHz, is a setting to try, CONFIG1 = 0xD3: its band reaches ~503 Hz, and the
module then sums twenty IMU samples into a step of 60 Hz instead of ten into one of 120 (see
[the IMUs' settings](#the-imus-settings)). The rate is set only before the first start, since a
write of CONFIG1 resets the digital filter (SBAS499C, 9.4.2); why 1,920 is not the rate is under
[WHY](WHY.md#the-sensing-module).

**Gain 12, not 24.** A channel takes ±VREF / gain, ±375 mV at a gain of 12 and ±187.5 mV at 24,
and the electrodes' DC offset takes its share of it (see
[Construction](CONSTRUCTION.md#electrodes)). The noise rises only from 0.56 to 0.65 µVrms at the
4 kSPS setting, ours on the 1.96608 MHz clock (SBAS499C, tables 3 and 4), against EMG of tens of
microvolts and more. The common-mode range narrows as a channel's input grows (SBAS499C,
equation 4: AVDD − 0.2 V − gain · V / 2 > CM > AVSS + 0.2 V + gain · V / 2): with 300 mV across
a channel at a gain of 12 the body may sit anywhere from 2.0 to 3.0 V, and the bias drive holds it
at 2.5 V; at a gain of 24, 176 mV would leave only 2.31 to 2.69 V. The gain is one for the whole
suit, as Baťa's scale assumes (see [signals](../bata/SIGNALS.md#the-emg-channel)); should the
offsets prove small everywhere, 24 is one register value and that scale away.

**At start,** after the datasheet's own sequence (10.1.2, figure 67): the chip wakes in RDATAC, so
first SDATAC; then CONFIG3 with PD_REFBUF and a wait for the internal reference to settle; then the
23 registers of 0x01 to 0x17 as they came in one frame, written by two WREGs, 0x01 to 0x11 and 0x14
to 0x17, the read-only LOFF_STATP and LOFF_STATN skipped, and an RREG of 0x00 to 0x17 back, compared
with what was written; only then START and RDATAC. The sequence of the whole suit's start is under
[Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement). **Asleep** in the service mode the
ADS1299 is in standby, by its STANDBY command, and wakes by WAKEUP (see
[Porjadok](../porjadok/SOFTWARE.md#bring-up)).

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
- Both bytes go in the diagnostics, turned over to 1 for an electrode on the skin and held at 0
  for the 32 samples once an electrode was off; see
  [Porjadok](../porjadok/SOFTWARE.md#the-diagnostics). What it means is Baťa's to judge.

The current flows through the electrode and the skin and adds a small constant offset to the
measured signal. Only the nanoamp settings are usable: through a contact of 50 kΩ, 6 µA would
already make 0.3 V, most of the ±375 mV range at a gain of 12, and 24 µA 1.2 V, far beyond
it. We will pick
between 6 and 24 nA, and the comparator threshold, by testing.

## The IMUs' settings

- **1,200 Hz, summed to 120 Hz:** CLKIN at 38,400 Hz scales every rate by 1.2 (DS-000347,
  12.5), so the 1 kHz setting runs at 1,200 Hz, ten samples to one step of 32 ADS samples
  (1/120 s). The module sums each step's ten samples (below) and sends 12 B per IMU per step,
  as a 120 Hz sample would take. At the 1,920 SPS to try it sums twenty into a step of 60 Hz,
  telling which from CONFIG1.
- **Over I3C,** two to a bus; if the first parts do not take SETDASA, the controller talks to
  them as I2C at their static addresses 0x68 and 0x69 (see [hardware](HARDWARE.md#sensing-module),
  *The IMUs on I3C*).
- Each IMU's 12 B go out after the step, 4 B a frame, placed by the frame's number
  ([Porjadok](../porjadok/SOFTWARE.md#a-units-data)).

**The registers,** from DS-000347 rev. 1.2 (chapter 14 for bank 0, 15 for bank 1, 12.3 for the
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
  0x1D–0x1E now and then into the diagnostics, °C = TEMP_DATA / 132.48 + 25 (14.5). The FIFO is not
  used: every sample is fetched as it comes, on the IBI or by polling.
- **The sum,** what the 12 B per step carry, strapdown integration as Movella's MTw does it on
  the sensor at 1,000 Hz (its white paper, *Strap-Down Integration*): the turn over the step,
  Δθ = Σ ωᵢ Δt + ½ Σ (θᵢ₋₁ × θᵢ), the ten rate samples summed with the two-sample coning
  term, which the plain sum of rates leaves out when the piece turns about two axes at once;
  and the mean specific force over the step, Σ aᵢ / 10, no sculling term, since nobody
  integrates velocity. Both go out as three i16 each in the raw scale of ±2000 °/s and ±16 g,
  Δθ divided by the step, so a reader may take them as a 120 Hz sample of the gyro and the
  accelerometer and be right to first order. A cross product and two sums a sample, a few
  dozen instructions, in the module's own time.
- **The chip's own 120 Hz** stays as a mode, set by register 1 of the module's chip 0x00: the
  100 Hz setting (0x08) and the filter at 0x00, the raw sample as it comes. It is the fallback
  should the IMUs ever talk I2C at 400 kHz on I3C2, where 1,200 Hz would fill the bus, and the way
  to compare the two on recordings.
- **The order:** the soft reset; bank 1 (CLKIN, I3C); bank 0 (the clock, the ranges and rates,
  the filters, INT); PWR_MGMT0 last, since nothing may be written for 200 µs after it.
- **A choice, not a datasheet value:** the second-order filter at ODR / 8 under the sum. In
  noise the two modes come out alike, the chip's filter or the sum of ten; the sum keeps the
  turn right in a fast swing, where a step of 8.3 ms taken as one rotation is off by up to
  ~0.05° a step at 300 °/s about two axes, a few degrees by the end of the swing, and at
  0.83 ms a hundredth of that (an estimate from the coning term, not a datasheet value). To be
  judged on recordings.
- **Asleep** in the service mode the IMUs go to sleep, PWR_MGMT0 with the gyro and the
  accelerometer off, and come back with the order above.

## The glove

The glove, Vešč, is a unit of its own on its arm's line, in the fourth slot (see
[hardware](HARDWARE.md#the-glove) and [Porjadok](../porjadok/SOFTWARE.md#the-units-behind-a-unit)):

- **Its frame of data** is the same 34 B as a module's, its IMUs' steps in all 28 B: 20 IMUs,
  240 B, in the frames 0–8 of the 32 after each step, zeros after them (see
  [Porjadok](../porjadok/SOFTWARE.md#a-units-data)). Its diagnostics are a unit's with no
  ADS1299, the IMUs' temperatures by turns, six a frame.
- **Staršaja** has no ADS1299 and so no DRDY: she gets *get ready* and *start* as every unit,
  and from *start* counts the cycles on her timer from the suit clock. The modules' first DRDY
  falls a fixed time after START, 2,057 CLK periods at 3,840 SPS (SBAS499C, table 7), and every
  2,560 ticks of the suit clock after it, so her fourth slot keeps in step; Mamka's heartbeat
  corrects her. By the same count she knows each IMU step's start and takes the Bratiški's steps
  by it. What she sends in her slot she has from them.
- **The Bratiški** are units behind her: each on a wire of its own, so Staršaja knows each by
  the wire and no straps are needed. A Bratiška reads its four IMUs on its two I3C buses, sums
  each one's ten samples into a step as a module does (see
  [the IMUs' settings](#the-imus-settings)), and sends Staršaja its steps, 48 B a step,
  ~5.8 kB/s; she passes Mamka's frames for it on its
  wire unchanged, firmware among them, and its answers up in the free part of her slot.
- **The CLKIN** for every IMU of the glove is Staršaja's, made from the suit clock and sent on one
  wire across the wrist, so the IMUs sample in step with the suit; a Bratiška runs on its own HSI
  and only reads them.
- **With the glove unplugged** the fourth slot stays empty; plugged back, it joins at the next
  bring-up, as any unit that has reset, answering *discover* by its own UID.
- **What the wires carry,** the frame between Staršaja and a Bratiška and its rate, is set on
  the first board; the steps fix its size, 48 B a step and the wire's answers.

## Clocks

By the suit's clock tree (see [Porjadok](../porjadok/SOFTWARE.md#the-clock-tree)): the core at
49.152 MHz, PLL1P ÷ 8, in VOS1, the line's USARTs on PLL3 Q. **The module** adds:

| what | setting |
|---|---|
| SPI1 to the ADS1299 | PLL1Q ÷ 5 (field 4): 78.6432 MHz, SPI1SEL = 000 (RCC_CCIPR3, 11.8.42), the SPI's own ÷ 4: 19.66 MHz, under the 100 MHz kernel limit of VOS1 (DS14540, table 20) and the ADS1299's 20 MHz |
| USART1 and UART4, the line | PLL3 Q, 196.608 MHz, USART1SEL and UART4SEL = 010 (RCC_CCIPR1, 11.8.40); OVER8 = 1, BRR = 0x0012: 19,660,800 Bd |
| I3C1, I3C2 | the APB clocks, I3C1SEL and I3C2SEL = 00 (RCC_CCIPR4, 11.8.43): 49.152 MHz |
| TIM3, the ADS1299 | PSC = 0, ARR = 24: CH3 in PWM at CCR3 = 12, the CLK at 1.96608 MHz, high for 12 of its 25 counts, the datasheet giving its period only, 414–666 ns (SBAS499C, 7.6); CH4 takes START high at count 18, the middle of the CLK's low half (see [Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement)) |
| TIM1, the IMUs | PSC = 0, ARR = 1,279, CH1 at CCR1 = 640: CLKIN at 38,400 Hz |
| TIM2, the start and the slots | PSC = 4: a tick of the suit clock, 101.7 ns, counted from the start command to START, and from DRDY to the slot |

**After a reset** the module takes the suit clock before it sets anything, and the line runs at
its rate from the start (see [Porjadok](../porjadok/SOFTWARE.md#the-clock-tree)).

**The glove's Staršaja** sets her clocks as the module, without the SPI and TIM3: her TIM1 makes
the glove's CLKIN, her line's USART and her five U(S)ARTs to the Bratiški take PLL3 Q, their rate
set on the first board. **A Bratiška** runs on his HSI, 32 MHz in VOS3 after a reset (RM0492 Rev
3), and never takes the suit clock: his I3C buses and his wire run from the bus clock.

## DMA

By the suit's rules (see [Porjadok](../porjadok/SOFTWARE.md#the-gpdma)). **The module,** 9
channels:

| channel | request (REQSEL) | what | priority | how |
|---|---|---|---|---|
| GPDMA1 0 | 27, uart4_rx | UART4 RX: Mamka's frames, 512 B a cycle at most | 3 | circular |
| GPDMA1 1 | 21, usart1_rx | USART1 RX: the echo of the module's own sending | 3 | circular |
| GPDMA1 2 | 6, spi1_rx | SPI1 RX: the ADS1299's 27 B in frames of 8 bits, a linked list of two nodes: the status word aside, the channels into the frame | 3 | one block at each DRDY |
| GPDMA1 4 | 122, i3c1_tc_dma | I3C1's control words, a frame of two reads | 1 | one block a sample |
| GPDMA1 5 | 120, i3c1_rx_dma | I3C1 RX: 2 × 12 B | 1 | one block a sample |
| GPDMA2 0 | 22, usart1_tx | USART1 TX: the frame and whatever follows it in the slot | 3 | one block a frame |
| GPDMA2 1 | 7, spi1_tx | SPI1 TX: zeros from one fixed word while reading; a command between two reads | 3 | with each read |
| GPDMA2 4 | 138, i3c2_tc_dma | I3C2's control words | 1 | one block a sample |
| GPDMA2 5 | 136, i3c2_rx_dma | I3C2 RX: 2 × 12 B | 1 | one block a sample |

Free: GPDMA1 3 and 6–7, GPDMA2 2–3 and 6–7. The SPI runs full duplex, so its TX channel clocks the
read with zeros; the CRC of the frame is the core's (see
[Porjadok](../porjadok/SOFTWARE.md#the-gpdma)).

**The glove's Staršaja** takes her line's channels as a module and her five wires' at priority 2,
laid out with her pins; **a Bratiška** six: his two buses' four as a module's, his wire's RX and
TX.

## Interrupts

By the suit's levels (see [Porjadok](../porjadok/SOFTWARE.md#interrupts)); the numbers are the
vector table's (RM0481 Rev 5, table 153). **The module:**

| level | interrupt | what it does |
|---|---|---|
| 0 | EXTI2 (13) | DRDY: SPI1's read started, TIM2 cleared for the slot |
| 1 | GPDMA1 channel 2 (29) | the read done: the frame built and, in slot 1, its sending started |
| 1 | TIM2 (45) | in slots 2–4, the slot's start: the frame's sending started |
| 2 | UART4 (61) | Mamka's frames: the line idle, the frame read |
| 2 | USART1 (58) | the end of sending: the echo checked |
| 6 | I3C1 (123, 124), I3C2 (131, 132), event and error | the IMUs' frames and in-band interrupts |
| 8 | ADC1 (37), FLASH (6) | the temperature and the 3.3 V, the firmware update |

**The glove's Staršaja** the same without the ADS1299, her cycle's timer at level 0 and her five
wires at 4; **a Bratiška** his wire at 4, the I3C at 6 and the flash at 8.

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
- the glove's five wires, what they carry and their rate, on the first board,
- against the reference: whether BIAS_SENSN = 0x00 or the full sum holds the body better,
- 3,840 against 1,920 SPS, and a step of 60 Hz against 120, on recordings.
