<div align="center">

# Porjadok: software

**What every module shares in firmware:** the frame, the cycle and its slots, the channel from the
master, the way into Baťa, the errors, the output of the whole suit and the start of a measurement.

↑ [Porjadok](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Every module is C, hard-coded, with no operating system. The lines these frames travel on are
under [hardware](HARDWARE.md#links-between-boards). Two protocols live here: **CI-STP**, the Small
Crazy Ivan Transport Protocol, on the lines inside the suit (the frame, the channel from the master,
the errors), and **CI-BTP**, the Big one, out of Baťa to any computer (under [Output](#output)).

## The frame

After every ADS1299 sample, each block sends one 40-byte frame: 10 words of 4 B. Each ADS1299
channel has a word of its own: 3 B of data as the chip sends them, most significant first, then
1 B of info. Nataša's frame on the head line is
her own, 68 B (see [Nataša](../natasa/SOFTWARE.md#natašas-frame)).

| word | content | B |
|---|---|---|
| 0 | channel 1 and the block number | 4 |
| 1 | channel 2 and LOFF_STATP | 4 |
| 2 | channel 3 and LOFF_STATN | 4 |
| 3 | channel 4 and `1100` with GPIO[7:4] | 4 |
| 4–7 | channels 5–8 and 4 B in rotation (temperatures, settings acknowledgements…) | 16 |
| 8 | IMUs 1–4, 1 B each | 4 |
| 9 | sample number 2 B and CRC-16 2 B | 4 |
| | **total** | **40** |

- **The ADS1299 status word** has 24 bits: `1100`, LOFF_STATP, LOFF_STATN and GPIO[7:4]
  (datasheet SBAS499C, section 9.4.4.2). It goes in full, only regrouped into whole bytes in the
  info bytes of channels 2–4. LOFF_STATP and LOFF_STATN report an electrode that has come off;
  see [Rubaška](../rubaska/SOFTWARE.md#an-electrode-coming-off).
- **The block number** is a check. The line and the slot already say who sent the frame, but
  the number catches a block in the wrong slot or a swapped cable.
- **IMU:** each IMU has 1 B in the frame, so its 12 B for a step take 12 frames. The sample
  number mod 32 gives the byte's position: positions 0–11 carry the IMU's data, 12–31 are free.
  The 16-bit sample number wraps at 65,536 = 32 × 2,048, so the position runs on unbroken across
  the wrap. A step is 32 ADS samples, 1/120 s: the IMU's turn and mean force over it, summed by
  the block from ten samples at 1,200 Hz, or the chip's own 120 Hz sample (see
  [Rubaška](../rubaska/SOFTWARE.md#the-imus-settings)); the master has it after 12 frames
  (~3.1 ms).
- **More than four IMUs:** one byte carries two IMUs at 120 Hz, at positions 0–11 and 12–23, so
  a frame carries up to eight without changing its layout. The calf's module carries the foot's
  IMUs this way (see [Rubaška](../rubaska/SOFTWARE.md#the-glove-and-the-foot)).
- **The rotating content** in the info bytes of channels 5–8, 4 B a frame, is also placed by the
  sample number mod 32: 32 positions, 128 B every 32 frames (8.3 ms, 120 Hz).

  | position | content |
  |---|---|
  | 0 | the block's state (1 B: measuring, glove or foot present, I3C1 and I3C2 in order, running an unconfirmed firmware, the last update failed, its sample count differs from the master's), its firmware version (2 B), the last container `seq` it took (1 B) |
  | 1 | counters: CRC errors seen on the channel from the master (2 B), repeats asked of it (2 B) |
  | 2 | the processor's temperature from its own sensor (2 B, 0.1 °C), its 3.3 V from VREFINT (2 B, mV) |
  | 3–8 | the ADS1299's 24 registers, 0x00–0x17, as the block last read them |
  | 9–10 | the four IMUs: a status byte and a temperature byte each |
  | 11–31 | zeros, reserved |

  The ADS1299 has no temperature register: its sensor is read by switching a channel's MUX to
  it, so it is not in the rotation; the processor's temperature stands for the board's.
- **The CRC-16** of the frame, and of everything else on the lines, is CRC-16/CCITT-FALSE:
  polynomial 0x1021, initial value 0xFFFF, no reflection, no final XOR, over the bytes in the
  order they are sent, stored little-endian like every 16-bit field. The STM32H5's CRC unit
  computes it in hardware: its polynomial and its size, 7, 8, 16 or 32 bits, are programmable
  (RM0481 Rev 5, 19.2 and 19.5.5).

## How a block builds the frame

SPI1 to SPI3 on the STM32H523 take frames of 4 to 32 bits (DS14540, table 10). Reading the
ADS1299 (216 bits) therefore arrives as 9 pieces of 24 bits: the status word and 8 channels.
The SPI itself delivers each 24-bit frame right-aligned in a 32-bit word, its top 8 bits
padded with zeros (RM0481 Rev 5, 58.4.9 *Data frame format*, figure 824, and 58.4.12), so the
GPDMA moves it word for word, with no alignment of its own (its PAM field does only bytes,
half-words and words, 16.4.10): the status word just before the frame, the channels straight
into words 0–7. The processor regroups the three status bytes into the info bytes, adds the
block number, the IMU bytes and the sample number, and starts the hardware CRC and the DMA to
the USART. On the receiving side a channel takes two operations: `v = (int32_t)(w << 8) >> 8;`
and `info = w >> 24;` (w is the word in little-endian, the channel in its low 24 bits).

## Timing of one cycle

260 µs at 3,840 SPS, the line at 19.66 Mbaud, four blocks.

The cycle is split into four equal slots of 65.1 µs, one per block. A block sends its frame at the
start of its slot. The rest of the slot is its own to send anything: a repeated frame, a
settings acknowledgement and so on.

```
0 µs          DRDY – every ADS1299 at once
0–11 µs       each block reads its ADS1299 (216 bits, SPI at 19.66 MHz)
11–76 µs      slot of block 1: frame at 11–31 µs (40 B = 20.3 µs), the rest free
76–141 µs     slot of block 2: frame at 76–97 µs
141–206 µs    slot of block 3: frame at 141–162 µs
206–271 µs    slot of block 4: frame at 206–227 µs; the slot's last 11 µs fall
              into the next cycle, while the blocks read their ADS
```

The ADS1299 takes SCLK at most at 20 MHz (a 50 ns period), and the STM32H523's SPI kernel clock
at most 100 MHz in VOS1 (DS14540, table 20), so the 197 MHz line clock cannot feed it. The same
PLL's second output does: the suit clock straight in, × 40 = a 393.216 MHz VCO, which gives
the line's 196.608 MHz ÷ 2 and the SPI's 78.6432 MHz ÷ 5; the SPI divides that by 4 to 19.66 MHz
(50.9 ns). The input and the VCO lie in the PLL's wide range of 2–16 MHz and 128–560 MHz
(DS14540, table 46). One PLL serves the whole block, and the read takes 11.0 µs.

Each slot ends with a 1 µs gap, ten times what the drivers need: a THVD1452 lets go of the
pair within 25 ns of DE falling and drives it within 50 ns of DE rising, with its receiver on
(SLLSEY3E, 7.8), and the frame's last stop bit and the next block's first start bit are placed
by the suit clock to within the ~0.2 µs the START spread allows. The free part of a slot holds
~44 µs, that is ~86 B. The frames
alone keep the line 31% busy. Latency from DRDY to a frame's last byte on Mamka is
31 µs for block 1 and 227 µs for block 4.

## The channel from the master

The pair from the master is nearly empty: exactly 512 B pass through it each cycle (19,660,800 Bd
÷ 10 × 260.4 µs). The master sends **one message a cycle**: the control frame, then the
containers announced in it, then nothing until the next cycle. The master is the time master, so
its cycles and the blocks' DRDYs run in step from the start command on.

**The control frame,** 6 B, ~3 µs:

| byte | field | meaning |
|---|---|---|
| 0 | `cmd` (bits 7–5), `count` (bits 3–0) | the command; how many containers follow in this cycle, 0–12 |
| 1 | `addr` | the block the command is for; 0x00 every block on the line; bit 7 set: the unit behind that block (N + 0x80), a glove behind its module, Míša behind Nataša |
| 2–3 | `sample` | the master's sample number, little-endian; for *repeat*, the sample number of the frame to repeat |
| 4–5 | `crc` | CRC-16 over bytes 0–3 |

| `cmd` | command | what the block does |
|---|---|---|
| 0 | running | compares `sample` with its own count of DRDYs; a difference is reported in its state byte |
| 1 | get ready | stops everything else and waits for *start*; the master sends it in at least four cycles in a row, so a missed frame does not matter |
| 2 | start | takes START high after a fixed number of suit-clock ticks from the frame's last stop bit (see [Starting a measurement](#starting-a-measurement)); counts samples from zero |
| 3 | stop | takes START low; the measurement ends |
| 4 | repeat | sends, in its next slot, its fresh frame and then the frame of sample `sample` again (see [Errors](#errors)) |
| 5 | reset | resets itself and its chips, and loads its settings from its own memory again |
| 6–7 | reserved | |

**A container** is a header of 4 B, up to 60 B of data and a CRC of 2 B, 66 B at most. Up to 60 B
so that one cycle's sound for [Nataša](../natasa/SOFTWARE.md#sound-across-the-suit), 48–52 B,
rides in one container; after the control frame 506 B are left in a cycle, seven full containers
or a dozen short ones.

| byte | field | meaning |
|---|---|---|
| 0 | `addr` | as in the control frame |
| 1 | `type` | see the table below |
| 2 | `len` | the data's length, 0–60 |
| 3 | `seq` | a running number; the block echoes it in its answer, and the same `seq` twice is carried out once |
| 4… | data | by type |
| last 2 | `crc` | CRC-16 over the header and the data |

| `type` | container | data |
|---|---|---|
| 1 | write ADS1299 registers | the first register's address, then the values in order |
| 2 | write IMU registers | which IMU (0–3), the bank, the first register's address, then the values |
| 3 | read back | 1 for the ADS1299, 2 for an IMU with its number and bank; then the first register and the count |
| 4 | the block's own settings | which IMU bytes it sends, the IMU mode (steps summed from 1,200 Hz, or the chip's own 120 Hz), the lead-off current and threshold it drives, whether it is the bias module |
| 5 | a piece of firmware | the piece's offset in the image (4 B) and 48 B of it; see [Updating firmware](#updating-firmware) |
| 6 | firmware control | *begin* (the unit's kind, the image's version, length and CRC-32), *commit*, *abort*, *confirm* |
| 7 | another repeat | the sample numbers of further frames to repeat, 2 B each, when one cycle had more than one bad frame |
| 8 | sound down | Nataša: one cycle's stereo, 12 or 13 samples of 4 B |
| 9 | the head | Nataša: a vibration command, a setting for the headband (see [Nataša](../natasa/SOFTWARE.md#buttons-and-vibration)) |
| 10 | the sphere | Míša to Nataša on their wire, 112 B (see [Nataša](../natasa/SOFTWARE.md#míšas-wire)) |
| 11 | measure | Nataša to Míša: the sample number the radar's frame starts at |
| 12–127 | reserved | |

**The block's answer** goes in the free part of its slot, after its frame, in the same container
format: `type` = 0x80 + the type it answers, the same `seq`, and as data a result byte (0 done,
otherwise an error code) followed by what was read back. A repeated frame has precedence: 40 B
and an answer of up to 66 B would not fit the ~86 B free, so in a cycle with a repeat the answer
waits for the next. Mamka reads the answers; those meant for Baťa she passes on in her UART
packets (see [Mamka](../mamka/SOFTWARE.md#the-uart)).

- **Chip settings:** the master sends a ready-made write in a container of type 1 or 2. The
  block carries it out between two ADS reads, at most one transaction per cycle, and answers
  with a read-back when asked. Knowledge of the chips stays in one place, in the STM32H562 or
  Baťa.
- **The ADS1299 while running:** in RDATAC mode it takes another command only after SDATAC
  (datasheet, section 9.5.3.7). So between two reads the block sends SDATAC, WREG and RDATAC
  again. Conversions go on and START stays high. The bytes of a multi-byte command must be
  4 CLK periods apart (~2.0 µs), so writing one register takes an estimated ~16 µs.
- **The ICM-42688-P:** its registers sit in banks chosen with `REG_BANK_SEL` (DS-000347), so a
  write in another bank is the bank switch and the write, well within one transaction a cycle.
- **Firmware updates** use the same containers while the measurement is stopped; the whole
  procedure is under [Updating firmware](#updating-firmware).

## Into Baťa

Each cycle brings 16 × 40 B = 640 B from the suit's lines, 2.3 MiB a second, that is 19.7 Mbit/s.
The head line's few bytes, such as Nataša's buttons, go over a separate control channel, an I2C
(see [Mamka](../mamka/SOFTWARE.md#the-control-channel)), and its sound over the I2S. The computer
is the SPI master and the STM32H562 the slave: when it has data it raises a "data ready" pin and
the computer reads it. The STM32H562 sends at up to 43 MHz as a slave; on PB14 that limit is
6 MHz, so MISO stays off PB14 (DS14258 table 115).

- **On the ROCK 5T** SPI runs at 37.5 MHz: the RK3588's SPI takes an even divider of a 200,
  150 or 24 MHz source, and 150 MHz ÷ 4 is the fastest under 43 MHz. Two SPIs move a cycle's
  record, two halves of 384 B, in 82 µs, and a sample reaches the computer ~310 µs after DRDY.
- **On the Raspberry Pi** SPI runs at 33.3 MHz, 200 MHz ÷ 6 in the RP1. The Linux driver rounds
  the divider up to an even number (`(⌈200 MHz / f⌉ + 1) & ~1` in spi-dw-core.c), so asking for
  33.3 MHz gives ÷ 8 = 25 MHz; the speed to ask for is 40 MHz, which gives ÷ 6. One SPI moves a
  cycle's record in 184 µs, two in 92 µs. A sample reaches the computer ~320 µs after DRDY, the
  227 µs of the last slot and the 92 µs over two SPIs. The Raspberry Pi cannot be the SPI slave:
  the Linux driver does not support it.
- Mamka hands over a whole cycle in either case, as a record of 768 B in two halves with a
  header and a CRC each (see [Mamka](../mamka/SOFTWARE.md#the-cycle-to-baťa-over-spi)). When
  Baťa is late, the cycles wait in a ring on her processor 1, ~178 ms of them.

## Errors

Every frame has a CRC. When the master gets a bad frame, it tells the block over the channel
from the master in the next control frame, *repeat* with the block's address and the sample
number; a second bad frame in the same cycle goes in a container of type 7. In the next cycle
the block sends its fresh frame at the start of its slot and the bad one again right after it;
the two (80 B) fit in the slot. The repeated frame arrives one cycle later (+260 µs) and the
master files it by its sample number. No further synchronisation is needed; the block just
keeps its last few frames in memory (16 frames = 640 B). The echo watches each block's own
transmission.

## Output

The suit puts out up to 127 values for the whole body, one byte each. A joint has one, two or
three axes, each with its own range from a table: 0 and 255 are the ends of that joint's range,
for example 0–140° for the knee.

- One byte is plenty. Over 120° a step is 0.47° and the rounding error 0.14° RMS; over 180° the
  step is 0.7°. Published work typically puts joint angles from IMUs a few degrees off, and EMG
  adds its own error, so more bits would only carry noise.
- More bits would not make the model heavier either: its cost comes from its size, not from the
  precision of its output. The Hailo computes in integers and can hand its output straight out
  as `UINT8` (HailoRT also offers `UINT16` and `FLOAT32`).
- The axes follow anatomy: flexion and extension, abduction and adduction, rotation.
- Three angles in a row always have a pose where the first and third axes line up and both
  describe the same movement (a singularity, gimbal lock). For the shoulder in the usual ISB
  convention it is the arm hanging at the side. Joints with one or two axes and a limited range
  keep it outside their range. The shoulder and the hip cannot, so they go out as a swing and a
  twist, still 3 B: two numbers tilt the bone from its rest direction in one go, forward and
  out to the side, and the third turns it about its own axis. Unreal's physics constraints
  limit a joint the same way, as Swing 1, Swing 2 and Twist.
- The swing has one pose it cannot describe: the bone pointing straight away from rest, 180°
  off. Rest is chosen to put that pose out of reach. For the arm it is raised 45° in the plane
  halfway between forward and sideways, which leaves the bad pose up behind the head over the
  other shoulder; for the leg it is down and a little forward, which leaves it up behind the
  back. Over ±150° a step of the swing is 1.2°, and over ±90° a step of the twist 0.7°.
- **Contact points:** 32 bits, 4 B in every snapshot, for where the body rests on something: a
  wall, the floor, a chair, the hands and feet in a push-up. Each bit is one area of the body,
  and a pose is only a combination of them: sitting on the floor is the buttocks, the heels and
  the balls of the feet; a chair with a back and arms adds the backs of the thighs, the back and
  the forearms. The model sees it in the EMG and the IMUs: a limb that neither hangs nor is held
  by its muscles must rest on something, on the side gravity pulls towards. The same rule marks
  the contacts in the recordings, so nobody labels them by hand. A game engine keeps a foot on
  the ground planted instead of sliding, and the steps give the path walked. Which area each bit
  stands for is set by a table, like the joints; these are the basic 32, and more can come in
  time.

  | part of the body | areas | bits |
  |---|---|---|
  | the head | the front, the back, the left, the right | 4 |
  | the shoulders | each from the front, the side and the back | 6 |
  | the trunk | the chest, the belly, the upper back, the lower back | 4 |
  | the trunk's sides | left, right | 2 |
  | the hips, from the side | left, right | 2 |
  | the buttocks | left, right | 2 |
  | the backs of the thighs | left, right | 2 |
  | the elbows and forearms | left, right | 2 |
  | the palms | left, right | 2 |
  | the knees and shins | left, right | 2 |
  | the heels | left, right | 2 |
  | the balls of the feet and the toes | left, right | 2 |
  | **all** | | **32** |

- At 120 frames a second, the joints' 127 B and the contacts' 4 B make ~16 kB/s.
- Neural networks learn rotations better in a six-number form than as angles or quaternions
  (Zhou et al., *On the Continuity of Rotation Representations in Neural Networks*, CVPR 2019).
  The model can put that out and the output core converts it at the end.

**Out of the suit: CI-BTP,** the Big Crazy Ivan Transport Protocol. Baťa sends the output over
UDP in frames of **512 B**: 64 blocks of 8 B, little-endian, the last block the frame's control
block. The size, the blocks and the control block at the end come from the owner's design of March
2026; the rest is what the suit needs today. The protocol on the lines inside the suit, above, is
its small brother, CI-STP.

| bytes | field | meaning |
|---|---|---|
| 0–3 | `sample` | u32: the suit's sample number the frame belongs to; the suit counts 16 bits, Baťa adds the upper half, so a recording carries its time in samples from the start, 310 hours before it wraps |
| 4 | `type` | u8: 0x00 an idle frame, 0x01 the suit's packets; a changed layout gets a new number, so there is no version field |
| 5 | `count` | u8: the number of packets in the frame |
| 6–7 | `crc16` | CRC-16/CCITT-FALSE over the whole 512 B with these two bytes as zeros, the same CRC as on the lines |

The first 63 blocks, 504 B, are a row of **packets**; what they do not fill is zeros. A packet is
a header of 4 B and its data, and the next packet starts on the next 8 B boundary: `type` (u8),
`sub` (u8, by type), `len` (u16, the data's length in bytes). The snapshot is the base: at 128
frames a second 120 frames carry a snapshot and 8 a meta packet, and whatever else is due in that
moment, an event, a few bytes of ECG, the sphere, is packed in behind it in the same frame, not
sent on its own. Every value has a fixed place in its packet, set by a table, so a converter into
another format is a table too. A frame with no snapshot and no meta is an idle frame, type 0x00,
sent once a second when nothing else goes, so that a listener knows the suit is still there.

| `type` | packet | data | `sub` |
|---|---|---|---|
| 1 | snapshot | the joints' 127 B and the contacts' 4 B | its place in the cycle |
| 2 | meta | one of the eight meta packets below: the suit's identity and the run, the bones, the joint and contact tables, the electrodes, temperatures and the battery, the muscles' fatigue, the UTC label and the GPS position | which of the eight, 1–8 |
| 3 | ECG | the ECG separated from the EMG, **1 B a sample** a channel: the first sample's number (2 B), the count (1 B), the channels (1 B), then the bytes, channel by channel; 480 SPS by default (see [Baťa](../bata/SIGNALS.md#the-ecg-and-the-breath)) | the decimation, 1–32 |
| 4 | sphere | Míša's sphere, ~112 B | |
| 5 | event | 8 B: a running count of events (1 B), what (1 B: a button, a BMS alarm, an electrode off, start, stop, a sound Soňa heard, *halted* by [Storož](../bata/SOFTWARE.md#storož) with his reason in *which*), which (1 B), 5 B by kind; the event's time is the frame's `sample` | |
| 6 | vitals | 8 B once a second: the heart rate (bpm), its variability (RMSSD, ms), the breathing rate, the skin temperature (°C), the ECG's quality and the breath's source, 3 B zeros (see [Baťa](../bata/SIGNALS.md#the-ecg-and-the-breath)) | |
| 16 | raw record half | to disk only: one half of Mamka's record, 384 B as she sent it, flags and all; two a cycle | which half |
| 17 | raw Nataša frame | to disk only: her 68 B frame as it came | |
| 7–15, 18–255 | reserved | | |

**The eight meta packets,** each in its own frame, one a cycle of eight meta frames, so the whole
set comes once a second at the full rate. All numbers little-endian; a temperature is an i16 in
0.1 °C, 0x7FFF for none.

| `sub` | packet | data | B |
|---|---|---|---|
| 1 | the suit and the run | the suit's serial (8 B), the run's number (u32) and its start (u32, Unix time), Baťa's software version (u16), the firmware versions of processor 1, processor 2, Nataša and Míša (4 × u16), the blocks present (u16, bit = block), the blocks' firmware versions (16 × u16), the snapshot rate code (u8), the number of joint values, contacts and ECG channels in use (3 × u8) | 64 |
| 2 | the bones | the wearer's height (u16, mm) and mass (u16, 0.1 kg), then the lengths in mm (u16 each): the neck, the torso from the shoulders to the hips, the shoulder width, the pelvis width, and left then right the upper arm, the forearm, the hand, the thigh, the shin and the foot | 36 |
| 3 | the joint table, values 0–63 | 4 B a value: the joint (u8, from the joint list), the axis (u8: 1 flexion, 2 abduction, 3 rotation, 4 swing forward, 5 swing out, 6 twist), the range's low and high ends (2 × i8, in 2°); the value's place in the snapshot is its index | 256 |
| 4 | the joint table, values 64–126, and the contacts | 63 values as above, then the 32 contact areas (u8 each, from the area list) | 284 |
| 5 | the electrodes | 128 channels, block by block, 1 B each: bit 0 P off, bit 1 N off (from LOFF_STAT), bit 2 the channel is on, bit 3 the channel drives the bias, bits 4–7 the signal's quality 0–15 as Baťa rates it; then the bias module's number (u8) and 3 B zeros | 132 |
| 6 | temperatures and the battery | the blocks' processors (16 × i16), the IMUs (64 × i8, °C, block by block, 0x7F none), Mamka's two processors and Baťa's CPU (3 × i16), the battery as the BMS gives it: the cells (4 × u16, mV), the pack (u16, mV), the current (i16, mA), three temperatures (3 × i16), the alarms (u16), the state of charge (u8, %), the remaining capacity (u16, mAh); the converters' PGOOD and EN (u8), the fan (u16, rpm), 4 B zeros | 132 |
| 7 | the muscles' fatigue | the muscle group of each of the 128 channels (u8 each, 0 none), then the fatigue of groups 1–64 (u8 each, 0 fresh to 255) | 192 |
| 8 | time and place | the UTC label: the suit's sample (u32) at which a UTC second began and that second (u32, Unix time), 0 while no PPS has come; the position (2 × i32, 10⁻⁷ °), the height (i16, m), the fix's quality (u8), the satellites (u8), 4 B zeros | 24 |

The joint list and the area list, the names behind the numbers, are tables in Baťa's software
and the recordings' reader, not in the stream. The set is ~1.1 KB.

- **Ties to time.** The frame's `sample` is the suit's clock, so the snapshot, the ECG and an
  event in one frame share one time; the meta packets carry the UTC label for it. A lost frame
  shows as a jump in `sample`, since snapshots come every 32nd sample; a lost event would not, so
  the event packet counts its events.
- **The ECG at one byte.** Cheap ECG recorders resolve about as much, and a doctor reads it. What
  matters is the sample number: every ADS1299 in the suit samples in the same instant on the
  same clock, so the ECG bytes of the trunk's electrodes line up to the sample, and a picture of
  how the current passes through the chest can be put together from them later.
- **Raw data do not go out this way.** Raw EMG (2.46 MB/s) and raw IMU are for learning and go
  to a disk, Deduška's or an SSD on Baťa, as files of the same 512 B frames with packet types of
  their own, 16 and 17 above, never over the network live: a cycle's record takes two frames,
  ~3.9 MB/s with Nataša's frames. One parser then reads a live stream and a recording alike,
  and every recording begins with a full set of meta packets. The simulator under
  [software](../software/protocol/README.md) writes such files.
- **Converters run on Baťa,** not on the computer that listens: Live Link, VMC over OSC, LSL,
  HID and the rest are programs on Baťa that read the native stream and send out the format the
  other side knows (see [Baťa](../bata/SOFTWARE.md#output-modes)). A client that wants the native
  stream sends Baťa a *subscribe* message on his port, 8 B: `magic` 0xC1A1 (u16), the packet
  types it wants as a bit mask (u32), the snapshot rate 128, 64 or 32 as a code (u8), zero (u8),
  and repeats it every second; Baťa stops sending five seconds after the last one.
- **The flow** is 128 × 512 B = 64 kB/s at the full rate, 32 kB/s and 16 kB/s at the lower two,
  which Wi-Fi carries with room.

| frames a second | snapshots | meta frames | the whole model description every |
|---|---|---|---|
| 128 | 120 Hz | 8 | 1 s |
| 64 | 60 Hz | 4 | 2 s |
| 32 | 30 Hz | 2 | 4 s |

- The snapshots are the suit's own: the IMUs run at 120 Hz, one sample per 32 ADS samples, so
  every snapshot at 120 Hz is a measured one, 60 Hz takes every other and 30 Hz every fourth.
  Baťa puts the meta frames in between; UDP needs no common clock with the suit, and every
  snapshot carries its number.
- The meta frames carry, as the set of eight above, what changes slowly. Fatigue goes as a byte
  per muscle group: surface EMG hears the neighbouring muscles too, so it cannot tell each muscle
  apart. Whoever connects waits one cycle and has the whole model.
- Formats a converter can feed: Unreal Engine's Live Link; VMC over OSC for Unity, VRChat and
  VTubing; SteamVR trackers; OSC or MIDI for music; LSL with XDF for research; BDF or EDF+ for
  the EMG and the ECG; BVH, FBX or glTF for animation; C3D and OpenSim for biomechanics; ROS 2
  for robots; and USB HID for anything with a USB port.

## Starting a measurement

Every ADS1299 in the suit should start converting at the same moment. The sequence:

1. After power-up each block loads its complete settings from its own memory and writes them
   into the ADS1299 and the IMUs, even if the chips should still remember them.
2. The ADS1299 is reset and prepared, with its START pin held low.
3. The master sends "get ready" down every line. The block turns off every other interrupt and
   waits in a loop for one thing only: the start command arriving on the bus. It can wait a
   whole second.
4. The master broadcasts START down every line at once. The block immediately takes the START
   pin of its ADS1299 high and leaves it there.

**START stays high for the whole measurement.** According to the datasheet (sections 9.4.1 and
9.4.5), conversions begin once START has been high for at least 2 CLK periods and go on until
START goes low. A short pulse would stop the measurement right after the first conversion. The
delay from START to the first DRDY is fixed for a given data rate: 2,057 CLK periods at the 4 kSPS
setting, 3,840 SPS here (table 7).

The spread between blocks:

| cause | estimate |
|---|---|
| processor reaction in the loop | a few cycles, 5.1 ns a cycle at 197 MHz |
| difference between THVD drivers and receivers | 20–30 ns |
| difference in cable length | under 10 ns |
| path from the processor pin to the ADS pin | the same on every block, same boards |
| **total** | **~50–70 ns** |

The ADS1299 reads START on its own clock (1.96608 MHz, a 509 ns period). If the dividers that make
it on the blocks are not in the same phase, conversions can drift apart by up to one ADS clock
period, about 0.5 µs. That is still 0.2% of the sample period (260 µs); for a 1 kHz signal, a phase
error of ~0.2°.

**Aligning to the ADS clock edge.** Every line takes its clock from one source through one buffer
(an SN74LVC126A on Mamka, with an SN74LVC1G126 for the fifth line), so the suit clock is the same on
every block apart from the THVD and cable spread. The ADS clock's dividers, though, come up in a
different phase on each block, so they are cleared at the start: on the start command the block
clears its divider and starts a timer counting suit-clock ticks. After a fixed number of ticks the
timer takes START high in the middle of the ADS clock's low half. The datasheet does not say which
CLK edge reads START, nor give any setup time. In the middle of the low half START is about a
quarter period (~130 ns) from both edges, so every ADS reads it on the same edge, whichever it is.
What remains is the spread in the command's arrival rounded to suit-clock ticks, on the order of
100–200 ns; conversions no longer drift a whole ADS clock period apart. The timer is only needed at
the start and is free for anything else the rest of the time.

## Updating firmware

Every unit with a processor of its own takes new firmware the same way, in containers of types 5
and 6 over whatever reaches it: a block over its line, a Vnučka over Interconnect through the
forearm's module (see [Rubaška](../rubaska/SOFTWARE.md#the-glove-and-the-foot)), Nataša and Míša
over the head line through Mamka's processor 2, processor 1 over the UART and processor 2 over
the I2C (see [Mamka](../mamka/SOFTWARE.md#firmware)). Baťa drives every update; Mamka only
carries the containers, except for her own images. The measurement is stopped first: the master
keeps its cycle and its control frame (*stop*), the containers ride as always, and a block's
answer goes at the start of its slot, there being no frame.

**Two banks.** Every STM32H5 here has its flash in two banks and reads one while writing the
other (DS14540 Rev 3 and DS14258 Rev 6, 3.4; DS14053 Rev 4, 3.4). The unit runs from one bank
while the new image goes into the other, so a failed update never leaves it without a firmware.
An image is at most one bank: 128 KB on a block's STM32H523CC (two equal banks of its 256 KB,
RM0481 Rev 5, table 53), 256 KB on Nataša's STM32H523RE, 64 KB on a Vnučka's STM32H503KB
(RM0492 Rev 3, 7.2, with the same bank swap, 7.3.10) and 512 KB on Mamka's STM32H562RG, two
equal banks of its 1 MB. Flash is written in words of 128 bits, 16 B (RM0481, 7.3.3 and
7.3.5), so a piece carries 48 B, three words, and the last piece is padded with 0xFF to a
whole word. The one exception is processor 2's own image on the I2C, whose transfers hold
122 B of data: there a piece carries 112 B, seven words (see
[Mamka](../mamka/SOFTWARE.md#firmware)).

**The containers,** with the data after the result byte of the answer:

| container | data | answer |
|---|---|---|
| 6 *begin* | 1 (1 B), the unit's kind (1 B), the image's version (2 B), its length (4 B), its CRC-32 (4 B): 12 B | once the other bank is erased: 16 sectors of 8 KB at up to 10 ms each (DS14540, tERASE), ~0.2 s |
| 5 a piece | the piece's offset in the image (4 B), then 48 B of it: 52 B | the offset it expects next (4 B) |
| 6 *commit* | 2 | after the CRC-32 over the whole image in flash matched; the unit resets one cycle after answering |
| 6 *abort* | 3 | the update is forgotten; also clears "the last update failed" |
| 6 *confirm* | 4 | the running firmware is confirmed and stays |

- **Kinds:** 1 a block, 2 a Vnučka, 3 Nataša, 4 Míša, 5 Mamka's processor 1, 6 processor 2.
  A unit refuses an image of another kind, or longer than its bank, or whose first sector is
  not its own (below).
- **Result codes** in the answer: 0 done; 1 the measurement is running; 2 the wrong kind or too
  long; 3 not the offset expected, the expected one follows; 4 the CRC-32 did not match;
  5 the flash refused to erase or write; 6 no update begun; 7 the first sector differs.
- **The CRC-32** is the one zlib computes: polynomial 0x04C11DB7, reflected input and output,
  initial value and final XOR 0xFFFFFFFF. The CRC unit does it with its default polynomial and
  the reversal of its input and output set (RM0481, 19.4.3 and 19.5.3).

**The sequence,** for a line of blocks; the other channels differ only in what carries the
containers:

1. Baťa stops the measurement and sends *begin* to the line, `addr` 0 when every block on it
   takes the same image, each block answering in its own slot after its erase.
2. The pieces follow in order of offset, one container a cycle. Baťa does not wait for the
   answers, which lag a cycle; when one says "not the offset expected", he goes back to that
   offset for the whole line. A block that already has a piece acknowledges it and drops it, so
   a rewind for one block costs the others nothing.
3. *Commit.* The block computes the CRC-32 over the `length` bytes of the new bank, checks
   that the image's first sector is byte for byte its own (below), and when both hold writes a
   note into its backup registers (below), programs the option bit SWAP_BANK
   (RM0481, 7.3.11, the sequence in seven steps) and resets. Mamka reports the block gone and
   back; the master sees the new version in the state, position 0 of the rotating content, with
   the bit "running an unconfirmed firmware".
4. Baťa checks what it wants, a short measurement if it likes, and sends *confirm* within
   **30 s** of the block's return. The block writes "confirmed" into the note and the update is
   over.
5. **Without the confirm,** or when the new firmware resets before it got one, the unit goes
   back to the old one by itself and the master sees "the last update failed" in its state.

**The note** in the backup registers, which no system reset clears (RM0481, 52.4.10): a check
pattern, a phase and a count of starts. The committing firmware writes the phase *trying* with the
count 0 before the swap. Every firmware, old or new, reads the note first thing after a start, and
only when the pattern matches, since the registers can come up with random contents after a
brownout (ES0565 Rev 8, 2.2.20): in *trying* it adds one to the count; a count of 1 is the first
start of the new image, which runs with a 30 s timer waiting for *confirm*; a count of 2 or more is
a start after a reset nobody asked for, so the firmware writes the phase *failed*, swaps the banks
back and resets, and the old image comes up and shows the failure. The timer running out does the
same. The independent watchdog is set to start by hardware, the option bit IWDG_SW cleared (RM0481,
7.4.4; RM0492, 7.4.5), so a new image that hangs before it even feeds the watchdog still ends in a
reset and the swap back; the option bytes are not swapped with the banks, so this holds for every
image. A unit with *begin* taken and no container for **2 s** forgets the update; the next *begin*
erases the bank again.

**The zero stage.** MCUboot, the usual bootloader of this class, keeps the test-and-revert
decision in a bootloader of its own that no update touches (its design, *Flash map* and *Image
trailers*). Here the first sector of every image, 8 KB, is that stage: the same bytes in every
image of a kind, built once and linked in at offset 0. It does one thing: reads the note, adds
the start, swaps back when the count says so, and jumps to the application in the rest of the
bank. A unit refuses at *commit* an image whose first sector is not its own, so the stage
never changes by an update; a new stage, should one ever be needed, goes in over SWD. Without
it a new image that hung before its first lines ran would be restarted by the watchdog into
the same bank for ever, with nobody to count.

**How long.** A block's image of 128 KB is 2,731 pieces, one a cycle: 0.71 s down a line; the
UART that brings them from Baťa carries ~2,460 packets of 61 B a second, so a line takes
~1.1 s and all four together, with `line` 0xFF, the same. A Vnučka's 64 KB take 1,366 pieces,
finger by finger. Mamka's own images and the head's are under
[Mamka](../mamka/SOFTWARE.md#firmware).

## Open questions

- the ADS1299 read at 19.66 MHz, which its DVDD of 3.3 V allows (SCLK period at least 50 ns at
  2.7–3.6 V, datasheet section 7.6), and the slots' 1 µs gaps, seen on the line,
- the ADS1299: the datasheet does not say which CLK edge reads START; confirm by measurement,
- the contact points: how well the model learns them, tried on recordings.
